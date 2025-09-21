"""
Property search and listing service for WhatsApp bot
"""
import logging
import re
from typing import Dict, Any, List, Optional
from app.core.database import database

logger = logging.getLogger(__name__)


class PropertySearchService:
    """Service for searching and filtering properties"""

    def __init__(self):
        self.search_sessions = {}  # Store user search state

    async def search_properties(self, filters: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search properties based on filters

        Args:
            filters: Dictionary of search filters
            limit: Maximum number of results

        Returns:
            List of property dictionaries
        """
        try:
            await database.connect()

            # Build dynamic query
            query_parts = ["SELECT * FROM \"Listing\" WHERE status = 'ACTIVE'"]
            params = {}

            # Add filters dynamically
            if filters.get('city'):
                query_parts.append("AND LOWER(city) = LOWER(:city)")
                params['city'] = filters['city']

            if filters.get('state'):
                query_parts.append("AND LOWER(state) = LOWER(:state)")
                params['state'] = filters['state']

            if filters.get('type'):
                query_parts.append("AND type = :type")
                params['type'] = filters['type'].upper()

            if filters.get('bedrooms'):
                query_parts.append("AND bedrooms = :bedrooms")
                params['bedrooms'] = filters['bedrooms']

            if filters.get('max_price'):
                query_parts.append("AND price <= :max_price")
                params['max_price'] = filters['max_price']

            if filters.get('min_price'):
                query_parts.append("AND price >= :min_price")
                params['min_price'] = filters['min_price']

            # Add ordering and limit
            query_parts.append('ORDER BY featured DESC, "createdAt" DESC')
            query_parts.append(f"LIMIT {limit}")

            query = " ".join(query_parts)

            logger.info(f"Property search query: {query}")
            logger.info(f"Query params: {params}")

            results = await database.fetch_all(query, params)
            await database.disconnect()

            return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"Property search failed: {e}")
            try:
                await database.disconnect()
            except:
                pass
            return []

    def extract_search_keywords(self, message: str) -> Dict[str, Any]:
        """
        Extract search criteria from natural language message

        Args:
            message: User's message text

        Returns:
            Dictionary of extracted filters
        """
        message_lower = message.lower()
        filters = {}

        # Extract number of bedrooms
        bedroom_match = re.search(r'(\d+)\s*bedroom', message_lower)
        if bedroom_match:
            filters['bedrooms'] = int(bedroom_match.group(1))

        # Extract property type
        if any(word in message_lower for word in ['apartment', 'flat']):
            filters['type'] = 'APARTMENT'
        elif any(word in message_lower for word in ['house', 'duplex', 'bungalow']):
            filters['type'] = 'HOUSE'
        elif any(word in message_lower for word in ['office', 'commercial']):
            filters['type'] = 'OFFICE'

        # Extract location
        locations = {
            'lagos': 'Lagos',
            'abuja': 'Abuja',
            'port harcourt': 'Port Harcourt',
            'kano': 'Kano',
            'ibadan': 'Ibadan'
        }

        for location_key, location_value in locations.items():
            if location_key in message_lower:
                filters['city'] = location_value
                break

        # Extract price filters
        price_match = re.search(r'under\s*(?:₦|naira|ngn)?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|m)', message_lower)
        if price_match:
            price_str = price_match.group(1).replace(',', '')
            filters['max_price'] = float(price_str) * 1_000_000

        # Extract exact price
        exact_price_match = re.search(r'(?:₦|naira|ngn)\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|m)', message_lower)
        if exact_price_match and 'under' not in message_lower:
            price_str = exact_price_match.group(1).replace(',', '')
            target_price = float(price_str) * 1_000_000
            filters['min_price'] = target_price * 0.8  # 20% below
            filters['max_price'] = target_price * 1.2  # 20% above

        return filters

    def format_property_message(self, property_data: Dict[str, Any]) -> str:
        """
        Format property data for WhatsApp message

        Args:
            property_data: Property dictionary

        Returns:
            Formatted WhatsApp message
        """
        try:
            # Format price
            price = property_data.get('price', 0)
            if price >= 1_000_000:
                price_str = f"₦{price/1_000_000:.1f}M"
            else:
                price_str = f"₦{price:,.0f}"

            # Format area
            area = property_data.get('area')
            area_str = f"{area}sqm" if area else "Area not specified"

            # Format bedrooms/bathrooms
            bedrooms = property_data.get('bedrooms', 0)
            bathrooms = property_data.get('bathrooms', 0)
            rooms_str = f"{bedrooms}BR/{bathrooms}BA" if bedrooms else "Rooms not specified"

            message = f"""🏠 *{property_data.get('title', 'Property')}*

📍 *Location:* {property_data.get('address', '')}, {property_data.get('city', '')}, {property_data.get('state', '')}

💰 *Price:* {price_str}
🏢 *Type:* {property_data.get('type', '').title()}
🛏️ *Rooms:* {rooms_str}
📐 *Area:* {area_str}

📝 *Description:*
{property_data.get('description', 'No description available')[:200]}{'...' if len(property_data.get('description', '')) > 200 else ''}

🆔 *Property ID:* {property_data.get('id', '')[:8]}...
"""

            return message

        except Exception as e:
            logger.error(f"Error formatting property message: {e}")
            return f"🏠 Property details available\nID: {property_data.get('id', 'Unknown')}"

    def get_main_menu(self) -> str:
        """Get main property search menu"""
        return """🏠 *INSPEKTA PROPERTY SEARCH*

Welcome! How would you like to search for properties?

*Quick Search:*
1️⃣ Show all available properties
2️⃣ Properties under ₦50M
3️⃣ Properties in Lagos
4️⃣ Properties in Abuja

*Detailed Search:*
5️⃣ Search by property type
6️⃣ Search by number of bedrooms
7️⃣ Search by price range
8️⃣ Search by location

*Or simply type your request:*
💬 "Show me 3 bedroom apartments in Lagos"
💬 "Houses under 40 million naira"
💬 "Office spaces in Abuja"

Reply with a number (1-8) or type your search request."""

    def get_property_type_menu(self) -> str:
        """Get property type selection menu"""
        return """🏢 *SELECT PROPERTY TYPE*

1️⃣ Apartments/Flats
2️⃣ Houses/Duplexes
3️⃣ Office Spaces
4️⃣ All types

0️⃣ Back to main menu

Reply with your choice (1-4):"""

    def get_bedroom_menu(self) -> str:
        """Get bedroom selection menu"""
        return """🛏️ *SELECT NUMBER OF BEDROOMS*

1️⃣ 1 Bedroom
2️⃣ 2 Bedrooms
3️⃣ 3 Bedrooms
4️⃣ 4 Bedrooms
5️⃣ 5+ Bedrooms
6️⃣ Any number

0️⃣ Back to main menu

Reply with your choice (1-6):"""

    def get_location_menu(self) -> str:
        """Get location selection menu"""
        return """📍 *SELECT LOCATION*

1️⃣ Lagos
2️⃣ Abuja
3️⃣ Port Harcourt
4️⃣ Kano
5️⃣ Ibadan
6️⃣ All locations

0️⃣ Back to main menu

Reply with your choice (1-6):"""

    def get_price_menu(self) -> str:
        """Get price range selection menu"""
        return """💰 *SELECT PRICE RANGE*

1️⃣ Under ₦25M
2️⃣ ₦25M - ₦50M
3️⃣ ₦50M - ₦100M
4️⃣ ₦100M - ₦200M
5️⃣ Above ₦200M
6️⃣ Any price

0️⃣ Back to main menu

Reply with your choice (1-6):"""

    async def handle_menu_selection(self, user_id: str, selection: str, current_menu: str = "main") -> Dict[str, Any]:
        """
        Handle user menu selections

        Args:
            user_id: User identifier
            selection: User's menu selection
            current_menu: Current menu context

        Returns:
            Response with next menu or search results
        """
        try:
            # Initialize user session if not exists
            if user_id not in self.search_sessions:
                self.search_sessions[user_id] = {}

            session = self.search_sessions[user_id]

            if current_menu == "main":
                if selection == "1":
                    # Show all properties
                    properties = await self.search_properties({}, limit=5)
                    return self._format_search_results(properties)

                elif selection == "2":
                    # Properties under 50M
                    properties = await self.search_properties({"max_price": 50_000_000}, limit=5)
                    return self._format_search_results(properties)

                elif selection == "3":
                    # Properties in Lagos
                    properties = await self.search_properties({"city": "Lagos"}, limit=5)
                    return self._format_search_results(properties)

                elif selection == "4":
                    # Properties in Abuja
                    properties = await self.search_properties({"city": "Abuja"}, limit=5)
                    return self._format_search_results(properties)

                elif selection == "5":
                    return {"type": "menu", "message": self.get_property_type_menu(), "next_menu": "property_type"}

                elif selection == "6":
                    return {"type": "menu", "message": self.get_bedroom_menu(), "next_menu": "bedrooms"}

                elif selection == "7":
                    return {"type": "menu", "message": self.get_price_menu(), "next_menu": "price"}

                elif selection == "8":
                    return {"type": "menu", "message": self.get_location_menu(), "next_menu": "location"}

                else:
                    return {"type": "menu", "message": "❌ Invalid selection. Please choose 1-8.\n\n" + self.get_main_menu(), "next_menu": "main"}

            # Handle other menu types...
            return {"type": "menu", "message": self.get_main_menu(), "next_menu": "main"}

        except Exception as e:
            logger.error(f"Error handling menu selection: {e}")
            return {"type": "menu", "message": "❌ An error occurred. Returning to main menu.\n\n" + self.get_main_menu(), "next_menu": "main"}

    def _format_search_results(self, properties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format search results for display"""
        if not properties:
            return {
                "type": "results",
                "message": "❌ No properties found matching your criteria.\n\nTry adjusting your search or reply *menu* for more options.",
                "count": 0
            }

        message = f"🏠 *FOUND {len(properties)} PROPERTIES*\n\n"

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

        message += "📱 *For full details of any property, reply with the property number (1-5)*\n"
        message += "🔍 *Reply 'menu' for more search options*"

        return {
            "type": "results",
            "message": message,
            "count": len(properties),
            "properties": properties
        }


# Global property search service instance
property_service = PropertySearchService()