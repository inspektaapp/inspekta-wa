#!/usr/bin/env python3
"""
Test script to verify session isolation and state management
"""
import json
import requests
import time

BASE_URL = "http://localhost:8000"

def test_webhook_message(user_id: str, user_name: str, message: str):
    """Simulate a WhatsApp webhook message"""
    webhook_data = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "112782131816859",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "15550259024",
                        "phone_number_id": "101245802980691"
                    },
                    "contacts": [{
                        "profile": {"name": user_name},
                        "wa_id": user_id
                    }],
                    "messages": [{
                        "from": user_id,
                        "id": f"wamid.TEST_{user_id}_{int(time.time())}",
                        "timestamp": str(int(time.time())),
                        "text": {"body": message},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    response = requests.post(f"{BASE_URL}/api/v1/whatsapp/webhook", json=webhook_data)
    return response.json()

def get_session_stats():
    """Get current session statistics"""
    response = requests.get(f"{BASE_URL}/api/v1/whatsapp/webhook/sessions")
    return response.json()

def main():
    print("🧪 Testing Session Isolation & Multi-User Support\n")

    # Test 1: First user starts conversation
    print("1. User Alice starts conversation...")
    result1 = test_webhook_message("1234567890", "Alice", "hi")
    print(f"   Response: {result1['response']['message'][:50]}...")

    # Check sessions after first user
    stats = get_session_stats()
    print(f"   Active sessions: {stats['session_stats']['active_sessions']}")

    time.sleep(1)

    # Test 2: Second user starts conversation
    print("\n2. User Bob starts conversation...")
    result2 = test_webhook_message("0987654321", "Bob", "hello")
    print(f"   Response: {result2['response']['message'][:50]}...")

    # Check sessions after second user
    stats = get_session_stats()
    print(f"   Active sessions: {stats['session_stats']['active_sessions']}")

    time.sleep(1)

    # Test 3: Alice selects menu option
    print("\n3. Alice selects option 1...")
    result3 = test_webhook_message("1234567890", "Alice", "1")
    print(f"   Response: {result3['response']['message'][:50]}...")

    time.sleep(1)

    # Test 4: Bob selects different menu option
    print("\n4. Bob selects option 5...")
    result4 = test_webhook_message("0987654321", "Bob", "5")
    print(f"   Response: {result4['response']['message'][:50]}...")

    # Final session check
    print("\n5. Final session statistics:")
    stats = get_session_stats()
    print(f"   Active sessions: {stats['session_stats']['active_sessions']}")
    for session in stats['session_stats']['sessions']:
        print(f"   User {session['user_id']}: {session['name']} - Menu: {session['menu']}, Step: {session['step']}")

    print("\n✅ Session isolation test completed!")

    # Test 6: Natural language search
    print("\n6. Testing natural language search...")
    result5 = test_webhook_message("1234567890", "Alice", "3 bedroom apartments in Lagos")
    print(f"   Response: {result5['response']['message'][:100]}...")

    print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    main()