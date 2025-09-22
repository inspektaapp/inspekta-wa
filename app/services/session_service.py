"""
User session management for WhatsApp bot conversations
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class UserSession:
    """Individual user session data"""

    def __init__(self, user_id: str, name: str = ""):
        self.user_id = user_id
        self.name = name
        self.current_menu = "main"
        self.search_filters = {}
        self.conversation_step = 0
        self.last_activity = datetime.now()
        self.conversation_history = []
        self.selected_property_ids = []

        # Enhanced context management
        self.current_context = "main"  # main, search_results, property_detail, sub_menu
        self.context_data = {}  # Store search results, selected property, etc.
        self.available_options = []  # Dynamic options based on current context
        self.navigation_stack = []  # For "back" functionality
        self.last_search_results = []  # Cache last search results

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    def add_to_history(self, message_type: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": message_type,
            "content": content
        })

        # Keep only last 20 messages
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def set_menu_context(self, menu: str, step: int = 0):
        """Set current menu context and step"""
        self.current_menu = menu
        self.conversation_step = step
        self.update_activity()

    def add_search_filter(self, key: str, value: Any):
        """Add or update search filter"""
        self.search_filters[key] = value
        self.update_activity()

    def clear_search_filters(self):
        """Clear all search filters"""
        self.search_filters = {}
        self.update_activity()

    def set_context(self, context: str, data: Any = None, available_options: List[str] = None):
        """Set current context with data and available options"""
        # Save current state to navigation stack
        if self.current_context != "main":
            self.navigation_stack.append({
                "context": self.current_context,
                "menu": self.current_menu,
                "step": self.conversation_step,
                "data": self.context_data.copy(),
                "options": self.available_options.copy()
            })

        self.current_context = context
        self.context_data = data or {}
        self.available_options = available_options or []
        self.update_activity()

    def go_back(self):
        """Go back to previous context"""
        if self.navigation_stack:
            previous = self.navigation_stack.pop()
            self.current_context = previous["context"]
            self.current_menu = previous["menu"]
            self.conversation_step = previous["step"]
            self.context_data = previous["data"]
            self.available_options = previous["options"]
            self.update_activity()
            return True
        return False

    def go_to_main_menu(self):
        """Reset to main menu"""
        self.current_context = "main"
        self.current_menu = "main"
        self.conversation_step = 0
        self.context_data = {}
        self.available_options = ["1", "2", "3", "4", "5", "6", "7", "8"]
        self.navigation_stack = []
        self.update_activity()

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "current_menu": self.current_menu,
            "search_filters": self.search_filters,
            "conversation_step": self.conversation_step,
            "last_activity": self.last_activity.isoformat(),
            "conversation_history": self.conversation_history[-5:],  # Last 5 for summary
            "selected_property_ids": self.selected_property_ids
        }


class SessionManager:
    """Manages user sessions for WhatsApp bot"""

    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}
        self.session_timeout = timedelta(hours=2)  # 2 hour timeout

    def get_or_create_session(self, user_id: str, user_name: str = "") -> UserSession:
        """Get existing session or create new one"""

        # Clean expired sessions first
        self._cleanup_expired_sessions()

        if user_id not in self.sessions:
            logger.info(f"Creating new session for user {user_id} ({user_name})")
            self.sessions[user_id] = UserSession(user_id, user_name)
        else:
            # Update name if provided
            if user_name and self.sessions[user_id].name != user_name:
                self.sessions[user_id].name = user_name

        self.sessions[user_id].update_activity()
        return self.sessions[user_id]

    def get_session(self, user_id: str) -> Optional[UserSession]:
        """Get existing session"""
        self._cleanup_expired_sessions()
        return self.sessions.get(user_id)

    def end_session(self, user_id: str) -> bool:
        """End user session"""
        if user_id in self.sessions:
            logger.info(f"Ending session for user {user_id}")
            del self.sessions[user_id]
            return True
        return False

    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_users = []

        for user_id, session in self.sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                expired_users.append(user_id)

        for user_id in expired_users:
            logger.info(f"Removing expired session for user {user_id}")
            del self.sessions[user_id]

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        self._cleanup_expired_sessions()

        active_sessions = len(self.sessions)
        session_details = []

        for session in self.sessions.values():
            session_details.append({
                "user_id": session.user_id[-4:] + "...",  # Show last 4 digits for privacy
                "name": session.name,
                "menu": session.current_menu,
                "step": session.conversation_step,
                "last_active": session.last_activity.strftime("%H:%M:%S"),
                "filters": len(session.search_filters)
            })

        return {
            "active_sessions": active_sessions,
            "session_timeout_hours": self.session_timeout.total_seconds() / 3600,
            "sessions": session_details
        }

    async def handle_user_message(self, user_id: str, user_name: str, message: str) -> Dict[str, Any]:
        """
        Handle user message with session context

        Returns:
            Dictionary with response and session info
        """
        session = self.get_or_create_session(user_id, user_name)
        session.add_to_history("user_message", message)

        logger.info(f"Processing message for user {user_id} in menu '{session.current_menu}' step {session.conversation_step}")

        # Handle the message based on current context
        response = await self._process_contextual_message(session, message)

        session.add_to_history("bot_response", response["message"])

        return {
            "response": response,
            "session_info": {
                "user_id": user_id,
                "current_menu": session.current_menu,
                "step": session.conversation_step,
                "filters": session.search_filters
            }
        }

    async def _process_contextual_message(self, session: UserSession, message: str) -> Dict[str, Any]:
        """Process message based on current session context with integrated search functionality"""

        message_lower = message.lower().strip()

        # Handle global navigation commands first
        if message_lower in ['menu', 'start', 'help', 'main', '*']:
            session.go_to_main_menu()
            from app.services.property_service import property_service
            return {
                "type": "menu",
                "message": f"👋 Welcome back {session.name}!\n\n" + property_service.get_main_menu()
            }

        if message_lower == 'back':
            if session.go_back():
                return await self._get_context_response(session)
            else:
                # If no back history, go to main menu
                session.go_to_main_menu()
                from app.services.property_service import property_service
                return {
                    "type": "menu",
                    "message": "🔄 No previous step. Returning to main menu...\n\n" + property_service.get_main_menu()
                }

        if message_lower in ['quit', 'exit', 'stop', 'end']:
            self.end_session(session.user_id)
            return {
                "type": "end",
                "message": "👋 Thanks for using INSPEKTA Property Search! Your session has ended.\n\nSend any message to start a new search."
            }

        # Handle greetings with friendly response
        if message_lower in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings', 'hola', 'howdy']:
            session.go_to_main_menu()
            from app.services.property_service import property_service
            greeting_responses = [
                f"👋 Hi there, {session.name}! Welcome to INSPEKTA Property Search!",
                f"🏠 Hello {session.name}! Ready to find your perfect property?",
                f"👋 Hey {session.name}! Let's find you an amazing property today!",
                f"🌟 Hi {session.name}! Welcome back to INSPEKTA Property Search!"
            ]
            # Use a simple hash to get consistent but varied greetings per user
            greeting_index = hash(session.user_id) % len(greeting_responses)
            greeting = greeting_responses[greeting_index]

            return {
                "type": "greeting",
                "message": f"{greeting}\n\n" + property_service.get_main_menu()
            }

        # Handle based on current context
        if session.current_context == "main":
            return await self._handle_main_menu_enhanced(session, message)
        elif session.current_context == "search_results":
            return await self._handle_search_results_selection(session, message)
        elif session.current_context == "property_detail":
            return await self._handle_property_detail_options(session, message)
        elif session.current_context == "sub_menu":
            return await self._handle_sub_menu_selection(session, message)
        else:
            # Fallback to main menu
            session.go_to_main_menu()
            from app.services.property_service import property_service
            return {
                "type": "menu",
                "message": "🔄 Returning to main menu...\n\n" + property_service.get_main_menu()
            }

    async def _handle_main_menu_enhanced(self, session: UserSession, message: str) -> Dict[str, Any]:
        """Enhanced main menu handler with restored search functionality"""

        from app.services.property_service import property_service

        if message.strip() in ['1', '2', '3', '4', '5', '6', '7', '8']:
            selection = message.strip()

            # Quick search options (1-4) - Execute immediate search
            if selection == "1":
                # Show all properties
                properties = await property_service.search_properties({}, limit=5)
                return await self._handle_search_results(session, properties, "Show all available properties")

            elif selection == "2":
                # Properties under 50M
                properties = await property_service.search_properties({"max_price": 50_000_000}, limit=5)
                return await self._handle_search_results(session, properties, "Properties under ₦50M")

            elif selection == "3":
                # Properties in Lagos
                properties = await property_service.search_properties({"city": "Lagos"}, limit=5)
                return await self._handle_search_results(session, properties, "Properties in Lagos")

            elif selection == "4":
                # Properties in Abuja
                properties = await property_service.search_properties({"city": "Abuja"}, limit=5)
                return await self._handle_search_results(session, properties, "Properties in Abuja")

            # Detailed search options (5-8) - Show sub-menus
            elif selection == "5":
                session.set_context("sub_menu", {"menu_type": "property_type"}, ["1", "2", "3", "4", "0", "back", "*"])
                return {"type": "menu", "message": f"✅ You selected: *Search by property type*\n\n" + property_service.get_property_type_menu()}

            elif selection == "6":
                session.set_context("sub_menu", {"menu_type": "bedrooms"}, ["1", "2", "3", "4", "5", "6", "0", "back", "*"])
                return {"type": "menu", "message": f"✅ You selected: *Search by number of bedrooms*\n\n" + property_service.get_bedroom_menu()}

            elif selection == "7":
                session.set_context("sub_menu", {"menu_type": "price"}, ["1", "2", "3", "4", "5", "6", "0", "back", "*"])
                return {"type": "menu", "message": f"✅ You selected: *Search by price range*\n\n" + property_service.get_price_menu()}

            elif selection == "8":
                session.set_context("sub_menu", {"menu_type": "location"}, ["1", "2", "3", "4", "5", "6", "0", "back", "*"])
                return {"type": "menu", "message": f"✅ You selected: *Search by location*\n\n" + property_service.get_location_menu()}

        # Try natural language processing
        filters = property_service.extract_search_keywords(message)
        if filters:
            # Execute search immediately
            properties = await property_service.search_properties(filters, limit=5)
            return await self._handle_search_results(session, properties, f"Natural search: \"{message}\"", natural_query=True)

        # Unrecognized input - Better error handling
        return {
            "type": "error",
            "message": f"❌ Unrecognized input: \"{message}\"\n\nPlease select a number (1-8) from the menu or try natural language like:\n• \"3 bedroom apartments in Lagos\"\n• \"Properties under 50 million\"\n\n💡 *Available commands:*\n• Type *menu* to return to main menu\n• Type *back* to go back one step\n\n" + property_service.get_main_menu()
        }



    async def _handle_search_results(self, session: UserSession, properties: List[Dict[str, Any]], search_description: str, natural_query: bool = False) -> Dict[str, Any]:
        """Handle search results and set up property selection context"""
        from app.services.property_service import property_service

        if not properties:
            return {
                "type": "no_results",
                "message": f"❌ No properties found for: *{search_description}*\n\nLet me show you our main search options:\n\n" + property_service.get_main_menu()
            }

        # Store search results in session
        session.last_search_results = properties

        # Set up property selection context
        available_options = [str(i) for i in range(1, len(properties) + 1)] + ["back", "*"]
        session.set_context("search_results", {
            "results": properties,
            "search_description": search_description,
            "natural_query": natural_query
        }, available_options)

        # Format results message
        message = f"🔍 *SEARCH RESULTS* for: *{search_description}*\n\n"
        message += f"Found {len(properties)} properties:\n\n"

        for i, prop in enumerate(properties, 1):
            # Format price
            price = prop.get('price', 0)
            price_str = f"₦{price/1_000_000:.1f}M" if price >= 1_000_000 else f"₦{price:,.0f}"

            # Format basic info
            bedrooms = prop.get('bedrooms', 0)
            prop_type = prop.get('type', '').title()
            location = f"{prop.get('city', '')}, {prop.get('state', '')}"

            message += f"*{i}. {prop.get('title', 'Property')[:30]}{'...' if len(prop.get('title', '')) > 30 else ''}*\n"
            message += f"📍 {location}\n"
            message += f"💰 {price_str} | 🛏️ {bedrooms}BR | 🏢 {prop_type}\n"
            message += f"🆔 {prop.get('id', '')[:8]}...\n\n"

        message += "📱 *Select a property by typing its number (1-" + str(len(properties)) + ")*\n"
        message += "💡 Type *back* to go back | Type *menu* for main menu"

        return {
            "type": "search_results",
            "message": message,
            "count": len(properties)
        }

    async def _handle_search_results_selection(self, session: UserSession, message: str) -> Dict[str, Any]:
        """Handle property selection from search results"""
        from app.services.property_service import property_service

        # Check if it's a valid property selection
        if message.strip().isdigit():
            selection = int(message.strip())
            results = session.context_data.get("results", [])

            if 1 <= selection <= len(results):
                selected_property = results[selection - 1]
                return await self._show_property_details(session, selected_property)

        # Invalid selection
        results = session.context_data.get("results", [])
        return {
            "type": "error",
            "message": f"❌ Unrecognized input: \"{message}\"\n\nPlease select a property by typing a number (1-{len(results)})\n\n💡 *Available commands:*\n• Type *back* to go back\n• Type *menu* for main menu"
        }

    async def _show_property_details(self, session: UserSession, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Show detailed property information"""
        from app.services.property_service import property_service

        # Set property detail context
        session.set_context("property_detail", {
            "property": property_data
        }, ["1", "2", "back", "*"])

        # Format detailed property message
        message = property_service.format_property_message(property_data)
        message += "\n\n🎯 *What would you like to do?*\n"
        message += "1️⃣ Show interest in this property\n"
        message += "2️⃣ Schedule an inspection\n\n"
        message += "💡 Type *back* to return to search results | Type *menu* for main menu"

        return {
            "type": "property_detail",
            "message": message
        }

    async def _handle_property_detail_options(self, session: UserSession, message: str) -> Dict[str, Any]:
        """Handle options in property detail view"""
        if message.strip() == "1":
            return {
                "type": "interest",
                "message": "✅ *Interest Recorded!*\n\nThank you for showing interest in this property. This feature is being developed.\n\n🔄 Coming soon:\n• Direct contact with agent\n• Save to favorites\n• Request more information\n\n💡 Type *back* to return to property details | Type *menu* for main menu"
            }

        elif message.strip() == "2":
            return {
                "type": "inspection",
                "message": "📅 *Schedule Inspection*\n\nScheduling feature is being developed.\n\n🔄 Coming soon:\n• Available time slots\n• Calendar integration\n• Agent coordination\n• Reminder notifications\n\n💡 Type *back* to return to property details | Type *menu* for main menu"
            }

        # Invalid option
        return {
            "type": "error",
            "message": f"❌ Unrecognized input: \"{message}\"\n\nPlease select an option:\n1️⃣ Show interest\n2️⃣ Schedule inspection\n\n💡 Type *back* to return to property details | Type *menu* for main menu"
        }

    async def _handle_sub_menu_selection(self, session: UserSession, message: str) -> Dict[str, Any]:
        """Handle selections in sub-menus (property type, bedrooms, etc.)"""
        menu_type = session.context_data.get("menu_type")

        if menu_type == "property_type":
            return await self._handle_property_type_selection(session, message)
        elif menu_type == "bedrooms":
            return await self._handle_bedroom_selection(session, message)
        elif menu_type == "price":
            return await self._handle_price_selection(session, message)
        elif menu_type == "location":
            return await self._handle_location_selection(session, message)

        # Fallback
        session.go_to_main_menu()
        from app.services.property_service import property_service
        return {
            "type": "menu",
            "message": "🔄 Returning to main menu...\n\n" + property_service.get_main_menu()
        }

    async def _handle_property_type_selection(self, session: UserSession, message: str) -> Dict[str, Any]:
        """Handle property type selection and execute search"""
        from app.services.property_service import property_service

        if message.strip() == "0":
            session.go_to_main_menu()
            return {
                "type": "menu",
                "message": "🔙 Returning to main menu...\n\n" + property_service.get_main_menu()
            }

        type_map = {
            "1": ("APARTMENT", "Apartments/Flats"),
            "2": ("HOUSE", "Houses/Duplexes"),
            "3": ("OFFICE", "Office Spaces"),
            "4": ("ALL", "All property types")
        }

        if message.strip() in type_map:
            selection = message.strip()
            property_type, type_name = type_map[selection]

            # Execute search
            filters = {"type": property_type} if property_type != "ALL" else {}
            properties = await property_service.search_properties(filters, limit=5)

            return await self._handle_search_results(session, properties, f"Property type: {type_name}")

        return {
            "type": "error",
            "message": f"❌ Unrecognized input: \"{message}\"\n\nPlease select 1-4 or 0 to go back.\n\n💡 Type *back* to go back | Type *menu* for main menu"
        }

    async def _handle_bedroom_selection(self, session: UserSession, message: str) -> Dict[str, Any]:
        """Handle bedroom selection and execute search"""
        from app.services.property_service import property_service

        if message.strip() == "0":
            session.go_to_main_menu()
            return {
                "type": "menu",
                "message": "🔙 Returning to main menu...\n\n" + property_service.get_main_menu()
            }

        bedroom_map = {
            "1": (1, "1 Bedroom"),
            "2": (2, "2 Bedrooms"),
            "3": (3, "3 Bedrooms"),
            "4": (4, "4 Bedrooms"),
            "5": (5, "5+ Bedrooms"),
            "6": ("ANY", "Any number of bedrooms")
        }

        if message.strip() in bedroom_map:
            selection = message.strip()
            bedrooms, bedroom_name = bedroom_map[selection]

            # Execute search
            filters = {"bedrooms": bedrooms} if bedrooms != "ANY" else {}
            properties = await property_service.search_properties(filters, limit=5)

            return await self._handle_search_results(session, properties, f"Bedrooms: {bedroom_name}")

        return {
            "type": "error",
            "message": f"❌ Unrecognized input: \"{message}\"\n\nPlease select 1-6 or 0 to go back.\n\n💡 Type *back* to go back | Type *menu* for main menu"
        }

    async def _handle_price_selection(self, session: UserSession, message: str) -> Dict[str, Any]:
        """Handle price range selection and execute search"""
        from app.services.property_service import property_service

        if message.strip() == "0":
            session.go_to_main_menu()
            return {
                "type": "menu",
                "message": "🔙 Returning to main menu...\n\n" + property_service.get_main_menu()
            }

        price_map = {
            "1": ({"max_price": 25_000_000}, "Under ₦25M"),
            "2": ({"min_price": 25_000_000, "max_price": 50_000_000}, "₦25M - ₦50M"),
            "3": ({"min_price": 50_000_000, "max_price": 100_000_000}, "₦50M - ₦100M"),
            "4": ({"min_price": 100_000_000, "max_price": 200_000_000}, "₦100M - ₦200M"),
            "5": ({"min_price": 200_000_000}, "Above ₦200M"),
            "6": ({}, "Any price")
        }

        if message.strip() in price_map:
            selection = message.strip()
            filters, price_name = price_map[selection]

            # Execute search
            properties = await property_service.search_properties(filters, limit=5)

            return await self._handle_search_results(session, properties, f"Price range: {price_name}")

        return {
            "type": "error",
            "message": f"❌ Unrecognized input: \"{message}\"\n\nPlease select 1-6 or 0 to go back.\n\n💡 Type *back* to go back | Type *menu* for main menu"
        }

    async def _handle_location_selection(self, session: UserSession, message: str) -> Dict[str, Any]:
        """Handle location selection and execute search"""
        from app.services.property_service import property_service

        if message.strip() == "0":
            session.go_to_main_menu()
            return {
                "type": "menu",
                "message": "🔙 Returning to main menu...\n\n" + property_service.get_main_menu()
            }

        location_map = {
            "1": ("Lagos", "Lagos"),
            "2": ("Abuja", "Abuja"),
            "3": ("Port Harcourt", "Port Harcourt"),
            "4": ("Kano", "Kano"),
            "5": ("Ibadan", "Ibadan"),
            "6": ("ALL", "All locations")
        }

        if message.strip() in location_map:
            selection = message.strip()
            location, location_name = location_map[selection]

            # Execute search
            filters = {"city": location} if location != "ALL" else {}
            properties = await property_service.search_properties(filters, limit=5)

            return await self._handle_search_results(session, properties, f"Location: {location_name}")

        return {
            "type": "error",
            "message": f"❌ Unrecognized input: \"{message}\"\n\nPlease select 1-6 or 0 to go back.\n\n💡 Type *back* to go back | Type *menu* for main menu"
        }

    async def _get_context_response(self, session: UserSession) -> Dict[str, Any]:
        """Get appropriate response for current context after going back"""
        from app.services.property_service import property_service

        if session.current_context == "main":
            return {
                "type": "menu",
                "message": f"🔙 Back to main menu\n\n" + property_service.get_main_menu()
            }
        elif session.current_context == "search_results":
            # Recreate search results display
            results = session.context_data.get("results", [])
            search_desc = session.context_data.get("search_description", "Previous search")
            return await self._handle_search_results(session, results, search_desc)
        elif session.current_context == "property_detail":
            # Recreate property detail display
            property_data = session.context_data.get("property", {})
            return await self._show_property_details(session, property_data)
        else:
            # Fallback to main menu
            session.go_to_main_menu()
            return {
                "type": "menu",
                "message": "🔄 Returning to main menu...\n\n" + property_service.get_main_menu()
            }


# Global session manager instance
session_manager = SessionManager()