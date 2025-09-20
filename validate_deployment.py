#!/usr/bin/env python3
"""
Deployment validation script for Inspector WhatsApp Bot
"""
import sys
import subprocess
import importlib
from pathlib import Path
from typing import List, Dict, Any


class ValidationResult:
    def __init__(self, name: str, passed: bool, message: str, details: Any = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details


class DeploymentValidator:
    def __init__(self):
        self.results: List[ValidationResult] = []

    def add_result(self, name: str, passed: bool, message: str, details: Any = None):
        """Add a validation result"""
        self.results.append(ValidationResult(name, passed, message, details))

    def validate_python_version(self) -> None:
        """Validate Python version"""
        version = sys.version_info
        min_version = (3, 8)

        if version >= min_version:
            self.add_result(
                "Python Version",
                True,
                f"Python {version.major}.{version.minor}.{version.micro} (>= 3.8 required)",
                version
            )
        else:
            self.add_result(
                "Python Version",
                False,
                f"Python {version.major}.{version.minor}.{version.micro} (< 3.8, upgrade required)",
                version
            )

    def validate_core_dependencies(self) -> None:
        """Validate core dependencies can be imported"""
        core_deps = [
            ("fastapi", "FastAPI"),
            ("uvicorn", "Uvicorn"),
            ("pydantic", "Pydantic"),
            ("pydantic_settings", "Pydantic Settings"),
            ("dotenv", "Python Dotenv")
        ]

        for module_name, display_name in core_deps:
            try:
                importlib.import_module(module_name)
                self.add_result(
                    f"Dependency: {display_name}",
                    True,
                    f"{display_name} imported successfully"
                )
            except ImportError as e:
                self.add_result(
                    f"Dependency: {display_name}",
                    False,
                    f"Failed to import {display_name}: {e}"
                )

    def validate_app_import(self) -> None:
        """Validate application can be imported"""
        try:
            from app.main import app
            from app.core.config import settings

            self.add_result(
                "Application Import",
                True,
                "FastAPI application imported successfully"
            )

            # Test settings
            self.add_result(
                "Settings Configuration",
                True,
                f"Settings loaded: DEBUG={settings.DEBUG}, PROJECT_NAME={settings.PROJECT_NAME}"
            )

            # Check production readiness
            self.add_result(
                "Production Readiness",
                settings.is_production_ready,
                f"Production ready: {settings.is_production_ready}",
                settings.configured_services
            )

        except Exception as e:
            self.add_result(
                "Application Import",
                False,
                f"Failed to import application: {e}"
            )

    def validate_file_structure(self) -> None:
        """Validate required files and directories exist"""
        required_paths = [
            "app/",
            "app/main.py",
            "app/core/config.py",
            "app/api/v1/endpoints/health.py",
            "requirements-core.txt",
            ".env",
            "Dockerfile",
            "logs/",
        ]

        for path_str in required_paths:
            path = Path(path_str)
            if path.exists():
                file_type = "directory" if path.is_dir() else "file"
                self.add_result(
                    f"File Structure: {path_str}",
                    True,
                    f"{file_type.title()} exists"
                )
            else:
                self.add_result(
                    f"File Structure: {path_str}",
                    False,
                    f"Missing required {path_str}"
                )

    def validate_environment(self) -> None:
        """Validate environment configuration"""
        try:
            from app.core.config import settings

            # Check critical environment variables
            critical_vars = {
                "SECRET_KEY": settings.SECRET_KEY,
                "PROJECT_NAME": settings.PROJECT_NAME,
                "API_V1_STR": settings.API_V1_STR,
            }

            for var_name, var_value in critical_vars.items():
                if var_value and len(str(var_value)) > 0:
                    self.add_result(
                        f"Environment: {var_name}",
                        True,
                        f"{var_name} is configured"
                    )
                else:
                    self.add_result(
                        f"Environment: {var_name}",
                        False,
                        f"{var_name} is missing or empty"
                    )

        except Exception as e:
            self.add_result(
                "Environment Configuration",
                False,
                f"Failed to validate environment: {e}"
            )

    def validate_logging(self) -> None:
        """Validate logging configuration"""
        try:
            import logging
            from app.core.logging_config import setup_logging

            # Test logging setup
            setup_logging()
            logger = logging.getLogger("test_validation")
            logger.info("Test log message")

            self.add_result(
                "Logging Configuration",
                True,
                "Logging setup successful"
            )

            # Check log directory
            logs_dir = Path("logs")
            if logs_dir.exists() and logs_dir.is_dir():
                log_files = list(logs_dir.glob("*.log"))
                self.add_result(
                    "Log Directory",
                    True,
                    f"Log directory exists with {len(log_files)} log files"
                )
            else:
                self.add_result(
                    "Log Directory",
                    False,
                    "Log directory missing or not accessible"
                )

        except Exception as e:
            self.add_result(
                "Logging Configuration",
                False,
                f"Logging setup failed: {e}"
            )

    def validate_api_endpoints(self) -> None:
        """Test API endpoints are accessible"""
        try:
            import httpx
            import asyncio
            from app.main import app
            from fastapi.testclient import TestClient

            client = TestClient(app)

            # Test health endpoints
            health_endpoints = [
                ("/api/v1/health/", "Basic Health Check"),
                ("/api/v1/health/detailed", "Detailed Health Check"),
                ("/api/v1/health/ready", "Readiness Check"),
                ("/api/v1/health/live", "Liveness Check"),
            ]

            for endpoint, name in health_endpoints:
                try:
                    response = client.get(endpoint)
                    if response.status_code == 200:
                        self.add_result(
                            f"API Endpoint: {name}",
                            True,
                            f"GET {endpoint} returned 200"
                        )
                    else:
                        self.add_result(
                            f"API Endpoint: {name}",
                            False,
                            f"GET {endpoint} returned {response.status_code}"
                        )
                except Exception as e:
                    self.add_result(
                        f"API Endpoint: {name}",
                        False,
                        f"Error testing {endpoint}: {e}"
                    )

        except ImportError:
            self.add_result(
                "API Endpoint Testing",
                False,
                "Cannot test endpoints - missing test dependencies (httpx, TestClient)"
            )
        except Exception as e:
            self.add_result(
                "API Endpoint Testing",
                False,
                f"Endpoint testing failed: {e}"
            )

    def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print("🔍 Running deployment validation checks...\n")

        # Run all validation methods
        self.validate_python_version()
        self.validate_core_dependencies()
        self.validate_file_structure()
        self.validate_environment()
        self.validate_logging()
        self.validate_app_import()
        self.validate_api_endpoints()

        # Calculate results
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results if r.passed)
        failed_checks = total_checks - passed_checks

        return {
            "total": total_checks,
            "passed": passed_checks,
            "failed": failed_checks,
            "success_rate": (passed_checks / total_checks) * 100 if total_checks > 0 else 0,
            "results": self.results
        }

    def print_results(self, summary: Dict[str, Any]) -> None:
        """Print validation results"""
        print("📋 VALIDATION RESULTS")
        print("=" * 50)

        # Print individual results
        for result in self.results:
            status = "✅" if result.passed else "❌"
            print(f"{status} {result.name}: {result.message}")
            if result.details and not result.passed:
                print(f"   Details: {result.details}")

        print("\n" + "=" * 50)
        print(f"📊 SUMMARY")
        print(f"Total Checks: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")

        if summary['failed'] == 0:
            print("\n🎉 ALL CHECKS PASSED! Deployment is ready.")
        else:
            print(f"\n⚠️  {summary['failed']} checks failed. Please address issues before deployment.")
            return False

        return True


def main():
    """Main validation function"""
    validator = DeploymentValidator()
    summary = validator.run_all_validations()
    success = validator.print_results(summary)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()