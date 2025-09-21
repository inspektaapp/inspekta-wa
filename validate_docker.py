#!/usr/bin/env python3
"""
Docker deployment validation script for Inspector WhatsApp Bot
"""
import subprocess
import time
import sys
import json
import requests
from typing import Dict, List


class DockerValidator:
    def __init__(self):
        self.results = []

    def add_result(self, name: str, passed: bool, message: str, details: str = ""):
        self.results.append({
            "name": name,
            "passed": passed,
            "message": message,
            "details": details
        })

    def run_command(self, cmd: List[str]) -> tuple:
        """Run shell command and return (returncode, stdout, stderr)"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def check_docker_daemon(self):
        """Check if Docker daemon is running"""
        code, stdout, stderr = self.run_command(["docker", "info"])
        if code == 0:
            self.add_result("Docker Daemon", True, "Docker daemon is running")
        else:
            self.add_result("Docker Daemon", False, f"Docker daemon not available: {stderr}")

    def check_docker_image(self):
        """Check if our Docker image exists"""
        code, stdout, stderr = self.run_command(["docker", "images", "-q", "inspector-whatsapp-bot:latest"])
        if code == 0 and stdout.strip():
            self.add_result("Docker Image", True, "inspector-whatsapp-bot:latest image exists")
        else:
            self.add_result("Docker Image", False, "inspector-whatsapp-bot:latest image not found")

    def check_docker_compose_syntax(self):
        """Validate docker-compose file syntax"""
        compose_files = ["docker-compose.yml", "docker-compose.dev.yml"]

        for compose_file in compose_files:
            code, stdout, stderr = self.run_command(["docker-compose", "-f", compose_file, "config"])
            if code == 0:
                self.add_result(f"Compose Syntax ({compose_file})", True, f"{compose_file} syntax is valid")
            else:
                self.add_result(f"Compose Syntax ({compose_file})", False, f"{compose_file} syntax error: {stderr}")

    def test_container_startup(self):
        """Test if container can start successfully"""
        print("🔄 Testing container startup...")

        # Try to start the development compose
        code, stdout, stderr = self.run_command([
            "docker-compose", "-f", "docker-compose.dev.yml", "up", "-d"
        ])

        if code != 0:
            self.add_result("Container Startup", False, f"Failed to start containers: {stderr}")
            return

        # Wait for containers to be ready
        time.sleep(30)

        # Check if containers are running
        code, stdout, stderr = self.run_command([
            "docker-compose", "-f", "docker-compose.dev.yml", "ps"
        ])

        if "Up" in stdout:
            self.add_result("Container Startup", True, "Containers started successfully")

            # Test health endpoint
            self.test_health_endpoint()
        else:
            self.add_result("Container Startup", False, f"Containers not running properly: {stdout}")

        # Cleanup
        self.run_command(["docker-compose", "-f", "docker-compose.dev.yml", "down"])

    def test_health_endpoint(self):
        """Test if health endpoint is accessible"""
        try:
            response = requests.get("http://localhost:8000/api/v1/health/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.add_result("Health Endpoint", True, "Health endpoint responding correctly")
                else:
                    self.add_result("Health Endpoint", False, f"Health endpoint returned wrong status: {data}")
            else:
                self.add_result("Health Endpoint", False, f"Health endpoint returned {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.add_result("Health Endpoint", False, f"Failed to reach health endpoint: {e}")

    def validate_environment_files(self):
        """Check if required environment files exist"""
        import os

        files_to_check = [
            ("Dockerfile", "Main Dockerfile"),
            ("docker-compose.yml", "Production compose file"),
            ("docker-compose.dev.yml", "Development compose file"),
            ("requirements-docker.txt", "Docker requirements"),
            (".dockerignore", "Docker ignore file")
        ]

        for filename, description in files_to_check:
            if os.path.exists(filename):
                self.add_result(f"File Check ({filename})", True, f"{description} exists")
            else:
                self.add_result(f"File Check ({filename})", False, f"{description} missing")

    def run_all_validations(self):
        """Run all Docker validation checks"""
        print("🐳 Running Docker deployment validation...\n")

        self.validate_environment_files()
        self.check_docker_daemon()
        self.check_docker_image()
        self.check_docker_compose_syntax()

        # Only test container startup if Docker is available
        docker_available = any(r["name"] == "Docker Daemon" and r["passed"] for r in self.results)
        image_available = any(r["name"] == "Docker Image" and r["passed"] for r in self.results)

        if docker_available and image_available:
            self.test_container_startup()
        else:
            self.add_result("Container Testing", False, "Skipped - Docker daemon or image not available")

    def print_results(self):
        """Print validation results"""
        print("🐳 DOCKER VALIDATION RESULTS")
        print("=" * 50)

        passed = 0
        total = len(self.results)

        for result in self.results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['name']}: {result['message']}")
            if result["details"] and not result["passed"]:
                print(f"   Details: {result['details']}")
            if result["passed"]:
                passed += 1

        print("\n" + "=" * 50)
        print(f"📊 SUMMARY")
        print(f"Total Checks: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed / total) * 100:.1f}%")

        if passed == total:
            print("\n🎉 ALL DOCKER CHECKS PASSED! Ready for containerized deployment.")
            return True
        else:
            print(f"\n⚠️  {total - passed} Docker checks failed. Please address issues before deployment.")
            return False


def main():
    """Main validation function"""
    validator = DockerValidator()
    validator.run_all_validations()
    success = validator.print_results()

    print("\n📋 DOCKER COMMANDS TO TRY:")
    print("Development: docker-compose -f docker-compose.dev.yml up")
    print("Production:  docker-compose up")
    print("Build only:  docker build -t inspector-whatsapp-bot:latest .")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()