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

    def handle_text_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming text messages

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

            logger.info(f"Handling text message from {sender_id}: {message_text}")

            # Simple echo response for now
            response = {
                "type": "text_response",
                "recipient": sender_id,
                "message": f"Echo: {message_text}",
                "original_message_id": message_id
            }

            return response

        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            return {"type": "error", "message": "Failed to process message"}

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

    def send_message(self, recipient: str, message: str) -> bool:
        """
        Send a text message to a recipient

        Args:
            recipient: Phone number or WhatsApp ID
            message: Message text to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.client:
                logger.warning("Cannot send message - WhatsApp client not initialized")
                return False

            # Send message using PyWa client
            self.client.send_message(
                to=recipient,
                text=message
            )

            logger.info(f"Message sent to {recipient}: {message}")
            return True

        except Exception as e:
            logger.error(f"Failed to send message to {recipient}: {e}")
            return False

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