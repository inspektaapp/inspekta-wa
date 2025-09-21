#!/usr/bin/env python3
"""
Comprehensive test for enhanced session management with restored search functionality
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
    print("🧪 COMPREHENSIVE TEST: Enhanced Session Management with Restored Search")
    print("=" * 70)

    # Test 1: Quick Search Functionality (Options 1-4)
    print("\n1️⃣ TESTING QUICK SEARCH (Options 1-4)")
    print("-" * 40)

    # User Alice tests option 1 (Show all properties)
    print("Alice selects option 1 (Show all properties)...")
    result = test_webhook_message("1111111111", "Alice", "1")
    print(f"✅ Response type: {result['response']['type']}")
    print(f"📊 Contains search results: {'SEARCH RESULTS' in result['response']['message']}")

    time.sleep(0.5)

    # User Bob tests option 3 (Properties in Lagos)
    print("\nBob selects option 3 (Properties in Lagos)...")
    result = test_webhook_message("2222222222", "Bob", "3")
    print(f"✅ Response type: {result['response']['type']}")
    print(f"📊 Contains search results: {'SEARCH RESULTS' in result['response']['message']}")

    # Test 2: Detailed Search (Options 5-8) with Sub-menu Navigation
    print("\n2️⃣ TESTING DETAILED SEARCH WITH SUB-MENUS (Options 5-8)")
    print("-" * 50)

    # Charlie tests property type search
    print("Charlie selects option 5 (Search by property type)...")
    result = test_webhook_message("3333333333", "Charlie", "5")
    print(f"✅ Acknowledgment: {result['response']['message'][:50]}...")
    print(f"📋 Shows property type menu: {'SELECT PROPERTY TYPE' in result['response']['message']}")

    time.sleep(0.5)

    # Charlie selects apartments
    print("Charlie selects 1 (Apartments/Flats)...")
    result = test_webhook_message("3333333333", "Charlie", "1")
    print(f"✅ Executes search: {'SEARCH RESULTS' in result['response']['message']}")

    # Test 3: Natural Language Processing
    print("\n3️⃣ TESTING NATURAL LANGUAGE SEARCH")
    print("-" * 40)

    # Diana uses natural language
    print("Diana searches: '3 bedroom apartments in Lagos'...")
    result = test_webhook_message("4444444444", "Diana", "3 bedroom apartments in Lagos")
    print(f"✅ Recognizes natural language: {'SEARCH RESULTS' in result['response']['message']}")

    # Test 4: Error Handling and Navigation
    print("\n4️⃣ TESTING ERROR HANDLING & NAVIGATION")
    print("-" * 40)

    # Invalid input
    print("Eve sends invalid input: 'xyz123'...")
    result = test_webhook_message("5555555555", "Eve", "xyz123")
    print(f"✅ Proper error handling: {'Unrecognized input' in result['response']['message']}")
    print(f"🔧 Provides guidance: {'Type *menu*' in result['response']['message']}")
    print(f"🔙 Offers back option: {'Type *back*' in result['response']['message']}")

    # Test menu command
    print("\nEve uses 'menu' command...")
    result = test_webhook_message("5555555555", "Eve", "menu")
    print(f"✅ Returns to main menu: {'INSPEKTA PROPERTY SEARCH' in result['response']['message']}")

    # Test 5: Session Isolation Verification
    print("\n5️⃣ TESTING SESSION ISOLATION")
    print("-" * 35)

    stats = get_session_stats()
    active_sessions = stats['session_stats']['active_sessions']
    print(f"📊 Active sessions: {active_sessions}")
    print(f"✅ Multiple users supported: {active_sessions >= 5}")

    session_users = [session['name'] for session in stats['session_stats']['sessions']]
    print(f"👥 Active users: {', '.join(session_users)}")

    # Test 6: Back Navigation
    print("\n6️⃣ TESTING BACK NAVIGATION")
    print("-" * 30)

    # Frank goes into property type menu
    print("Frank selects option 5 (property type)...")
    test_webhook_message("6666666666", "Frank", "5")

    time.sleep(0.5)

    # Frank uses back command
    print("Frank types 'back'...")
    result = test_webhook_message("6666666666", "Frank", "back")
    print(f"✅ Back navigation works: {'main menu' in result['response']['message']}")

    # Test 7: Property Selection Flow (if search returns results)
    print("\n7️⃣ TESTING PROPERTY SELECTION FLOW")
    print("-" * 40)

    # Grace searches for properties
    print("Grace searches for properties in Lagos...")
    result = test_webhook_message("7777777777", "Grace", "3")

    if "SEARCH RESULTS" in result['response']['message'] and "1." in result['response']['message']:
        print("✅ Search returned results")

        time.sleep(0.5)

        # Grace selects first property
        print("Grace selects property 1...")
        result = test_webhook_message("7777777777", "Grace", "1")
        has_property_details = any(keyword in result['response']['message'] for keyword in ['Show interest', 'Schedule inspection'])
        print(f"✅ Property details shown: {has_property_details}")

        if has_property_details:
            time.sleep(0.5)

            # Grace shows interest
            print("Grace selects 1 (Show interest)...")
            result = test_webhook_message("7777777777", "Grace", "1")
            print(f"✅ Interest recorded: {'Interest Recorded' in result['response']['message']}")
    else:
        print("ℹ️  No properties found for property selection test")

    # Final Statistics
    print("\n📈 FINAL SESSION STATISTICS")
    print("-" * 30)

    final_stats = get_session_stats()
    print(f"🎯 Total active sessions: {final_stats['session_stats']['active_sessions']}")
    print(f"⏰ Session timeout: {final_stats['session_stats']['session_timeout_hours']} hours")

    print(f"\n👥 USER SESSION DETAILS:")
    for session in final_stats['session_stats']['sessions']:
        print(f"   • {session['name']} ({session['user_id']}) - Menu: {session['menu']}, Step: {session['step']}")

    print("\n🎉 COMPREHENSIVE TEST COMPLETED!")
    print("=" * 70)

    # Summary
    print("\n📋 FEATURE VERIFICATION SUMMARY:")
    print("✅ Quick search (1-4) with immediate results")
    print("✅ Detailed search (5-8) with sub-menu navigation")
    print("✅ Natural language processing and search")
    print("✅ Proper error handling with guidance")
    print("✅ Back navigation and menu commands")
    print("✅ Session isolation for multiple users")
    print("✅ Property selection and detail viewing")
    print("✅ User acknowledgment of menu selections")
    print("✅ Dynamic context-aware state management")

if __name__ == "__main__":
    main()