"""
WhatsApp service for handling messages and business logic
"""
import logging
from typing import Dict, Any, Optional
from pywa import WhatsApp, types, filters
from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    WhatsApp service for message handling and business logic
    """

    def __init__(self):
        """Initialize WhatsApp service"""
        self.client: Optional[WhatsApp] = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize PyWa WhatsApp client"""
        try:
            if settings.WHATSAPP_TOKEN == "test_token_placeholder":
                logger.warning("WhatsApp client not initialized - test token in use")
                return

            # Initialize WhatsApp client with production settings
            self.client = WhatsApp(
                phone_id=settings.WHATSAPP_PHONE_ID,
                token=settings.WHATSAPP_TOKEN,
                # Note: server will be integrated later when we set up the full PyWa integration
                # For now, we handle webhooks manually in our FastAPI endpoints
            )
            logger.info("WhatsApp client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp client: {e}")
            self.client = None

    async def handle_text_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming text messages with property search functionality

        Args:
            message_data: WhatsApp message data from webhook

        Returns:
            Response data
        """
        try:
            # Extract message information
            message_text = self._extract_message_text(message_data)
            sender_id = self._extract_sender_id(message_data)
            message_id = self._extract_message_id(message_data)
            timestamp = self._extract_timestamp(message_data)
            sender_name = self._extract_sender_name(message_data)

            # Log detailed message info
            logger.info(f"📱 INCOMING MESSAGE:")
            logger.info(f"   From: {sender_id} ({sender_name})")
            logger.info(f"   Message ID: {message_id}")
            logger.info(f"   Timestamp: {timestamp}")
            logger.info(f"   Text: '{message_text}'")

            # Process the message based on content
            response_text = await self._process_message_content(message_text, sender_id, sender_name)

            response = {
                "type": "text_response",
                "recipient": sender_id,
                "message": response_text,
                "original_message_id": message_id,
                "sender_info": {
                    "id": sender_id,
                    "name": sender_name,
                    "timestamp": timestamp
                }
            }

            # Try to send the response immediately
            try:
                send_result = self.send_message(sender_id, response_text, "property_search")
                if send_result.get("success"):
                    logger.info(f"✅ Property search response sent successfully to {sender_id}")
                    logger.info(f"   Message ID: {send_result.get('message_id')}")
                else:
                    logger.error(f"❌ Failed to send response: {send_result.get('error')}")
            except Exception as e:
                logger.error(f"❌ Exception sending response: {e}")

            return response

        except Exception as e:
            logger.error(f"❌ Error handling text message: {e}")
            logger.error(f"Raw message data: {message_data}")
            return {"type": "error", "message": f"Failed to process message: {str(e)}"}

    def handle_button_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle button callback interactions

        Args:
            callback_data: Button callback data from webhook

        Returns:
            Response data
        """
        try:
            # TODO: Implement button callback handling
            logger.info(f"Handling button callback: {callback_data}")

            return {
                "type": "callback_response",
                "message": "Button callback received"
            }

        except Exception as e:
            logger.error(f"Error handling button callback: {e}")
            return {"type": "error", "message": "Failed to process callback"}

    def send_message(self, recipient: str, message: str, message_type: str = "text") -> Dict[str, Any]:
        """
        Send a message to a recipient using WhatsApp Cloud API

        Args:
            recipient: Phone number or WhatsApp ID
            message: Message text to send
            message_type: Type of message (text, template, etc.)

        Returns:
            Response dictionary with success status and details
        """
        try:
            import httpx
            from app.core.config import settings

            # Use direct API call instead of PyWa client for more reliability
            url = f"https://graph.facebook.com/v20.0/{settings.WHATSAPP_PHONE_ID}/messages"

            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "text",
                "text": {
                    "body": message
                }
            }

            logger.info(f"📤 Sending {message_type} message via API to {recipient}")
            logger.info(f"   URL: {url}")
            logger.info(f"   Message: {message[:100]}...")

            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=headers, timeout=30)

                if response.status_code == 200:
                    response_data = response.json()
                    logger.info(f"✅ Message sent successfully to {recipient}")
                    logger.info(f"   Response: {response_data}")
                    return {
                        "success": True,
                        "message_id": response_data.get("messages", [{}])[0].get("id"),
                        "recipient": recipient,
                        "response": response_data
                    }
                else:
                    logger.error(f"❌ Failed to send message. Status: {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code,
                        "recipient": recipient
                    }

        except Exception as e:
            logger.error(f"❌ Exception sending message to {recipient}: {e}")
            return {
                "success": False,
                "error": str(e),
                "recipient": recipient
            }

    def send_template_message(self, recipient: str, template_name: str, language: str = "en_US",
                            components: list = None) -> Dict[str, Any]:
        """
        Send a template message to a recipient

        Args:
            recipient: Phone number or WhatsApp ID
            template_name: Name of the approved template
            language: Language code (default: en_US)
            components: Template components/parameters

        Returns:
            Response dictionary with success status and details
        """
        try:
            import httpx
            from app.core.config import settings

            url = f"https://graph.facebook.com/v20.0/{settings.WHATSAPP_PHONE_ID}/messages"

            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language
                    }
                }
            }

            if components:
                payload["template"]["components"] = components

            logger.info(f"📤 Sending template '{template_name}' to {recipient}")

            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=headers, timeout=30)

                if response.status_code == 200:
                    response_data = response.json()
                    logger.info(f"✅ Template message sent successfully to {recipient}")
                    return {
                        "success": True,
                        "message_id": response_data.get("messages", [{}])[0].get("id"),
                        "recipient": recipient,
                        "template": template_name,
                        "response": response_data
                    }
                else:
                    logger.error(f"❌ Failed to send template. Status: {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code,
                        "recipient": recipient
                    }

        except Exception as e:
            logger.error(f"❌ Exception sending template to {recipient}: {e}")
            return {
                "success": False,
                "error": str(e),
                "recipient": recipient
            }

    def send_interactive_message(self, recipient: str, message_text: str, buttons: list) -> Dict[str, Any]:
        """
        Send an interactive message with buttons

        Args:
            recipient: Phone number or WhatsApp ID
            message_text: Text content of the message
            buttons: List of button objects

        Returns:
            Response dictionary with success status and details
        """
        try:
            import httpx
            from app.core.config import settings

            url = f"https://graph.facebook.com/v20.0/{settings.WHATSAPP_PHONE_ID}/messages"

            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": message_text
                    },
                    "action": {
                        "buttons": buttons
                    }
                }
            }

            logger.info(f"📤 Sending interactive message to {recipient}")

            with httpx.Client() as client:
                response = client.post(url, json=payload, headers=headers, timeout=30)

                if response.status_code == 200:
                    response_data = response.json()
                    logger.info(f"✅ Interactive message sent successfully to {recipient}")
                    return {
                        "success": True,
                        "message_id": response_data.get("messages", [{}])[0].get("id"),
                        "recipient": recipient,
                        "response": response_data
                    }
                else:
                    logger.error(f"❌ Failed to send interactive message. Status: {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    return {
                        "success": False,
                        "error": response.text,
                        "status_code": response.status_code,
                        "recipient": recipient
                    }

        except Exception as e:
            logger.error(f"❌ Exception sending interactive message to {recipient}: {e}")
            return {
                "success": False,
                "error": str(e),
                "recipient": recipient
            }

    def _extract_message_text(self, data: Dict[str, Any]) -> str:
        """Extract message text from webhook data"""
        try:
            # WhatsApp webhook structure: entry[0].changes[0].value.messages[0].text.body
            return data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0].get("text", {}).get("body", "")
        except (IndexError, KeyError) as e:
            logger.warning(f"Could not extract message text: {e}")
            return ""

    def _extract_sender_id(self, data: Dict[str, Any]) -> str:
        """Extract sender ID from webhook data"""
        try:
            return data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0].get("from", "")
        except (IndexError, KeyError) as e:
            logger.warning(f"Could not extract sender ID: {e}")
            return ""

    def _extract_message_id(self, data: Dict[str, Any]) -> str:
        """Extract message ID from webhook data"""
        try:
            return data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0].get("id", "")
        except (IndexError, KeyError) as e:
            logger.warning(f"Could not extract message ID: {e}")
            return ""

    def _extract_timestamp(self, data: Dict[str, Any]) -> str:
        """Extract timestamp from webhook data"""
        try:
            timestamp = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [{}])[0].get("timestamp", "")
            if timestamp:
                import datetime
                return datetime.datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
            return ""
        except (IndexError, KeyError, ValueError) as e:
            logger.warning(f"Could not extract timestamp: {e}")
            return ""

    def _extract_sender_name(self, data: Dict[str, Any]) -> str:
        """Extract sender name from webhook data"""
        try:
            # WhatsApp doesn't always provide name in webhook, but we can try
            contacts = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("contacts", [])
            if contacts:
                return contacts[0].get("profile", {}).get("name", "")
            return ""
        except (IndexError, KeyError) as e:
            logger.warning(f"Could not extract sender name: {e}")
            return ""

    async def _process_message_content(self, message_text: str, sender_id: str, sender_name: str) -> str:
        """
        Process message content using session management for proper user isolation

        Args:
            message_text: The message text from user
            sender_id: User's WhatsApp ID
            sender_name: User's name

        Returns:
            Response message text
        """
        try:
            from app.services.session_service import session_manager

            # Use session manager to handle the message with user context
            result = await session_manager.handle_user_message(sender_id, sender_name, message_text)

            logger.info(f"Session-managed response for {sender_id}: {result['response']['type']}")

            return result['response']['message']

        except Exception as e:
            logger.error(f"Error processing message content: {e}")
            return f"❌ Sorry, I encountered an error processing your request.\n\nReply *menu* to see search options."

    def is_message_webhook(self, data: Dict[str, Any]) -> bool:
        """
        Check if webhook data contains a message

        Args:
            data: Webhook data

        Returns:
            True if data contains a message, False otherwise
        """
        try:
            return bool(
                data.get("entry", [{}])[0]
                .get("changes", [{}])[0]
                .get("value", {})
                .get("messages")
            )
        except (IndexError, KeyError):
            return False


# Global WhatsApp service instance
whatsapp_service = WhatsAppService()