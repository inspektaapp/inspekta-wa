"""
WhatsApp webhook endpoints for receiving and handling messages
"""
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import PlainTextResponse
import logging
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/webhook", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
):
    """
    WhatsApp webhook verification endpoint

    This endpoint is called by WhatsApp to verify that your webhook URL is valid
    and that you own the server. It's part of the initial webhook setup process.
    """
    logger.info(f"Webhook verification requested - mode: {hub_mode}, token: {hub_verify_token[:8]}...")

    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verification successful")
        return hub_challenge

    logger.warning("Webhook verification failed - invalid verify token")
    raise HTTPException(status_code=403, detail="Invalid verify token")


@router.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle incoming WhatsApp webhook updates

    This endpoint receives updates from WhatsApp including:
    - Incoming messages
    - Message status updates (delivered, read, etc.)
    - User interactions with buttons/menus
    """
    try:
        # Parse JSON data
        data = await request.json()

        logger.info(f"Received webhook update: {data}")

        # Import WhatsApp service
        from app.services.whatsapp_service import whatsapp_service

        # Check if this is a message webhook
        if whatsapp_service.is_message_webhook(data):
            logger.info("Processing incoming message")

            # Handle the message
            response = whatsapp_service.handle_text_message(data)

            logger.info(f"Message processed: {response}")

            return {
                "status": "processed",
                "type": "message",
                "response": response
            }
        else:
            logger.info("Non-message webhook received")
            return {
                "status": "received",
                "type": "status_update"
            }

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/webhook/status")
async def webhook_status():
    """
    Get webhook configuration status
    """
    return {
        "webhook_configured": bool(settings.WHATSAPP_VERIFY_TOKEN != "test_verify_token_placeholder"),
        "phone_id_configured": bool(settings.WHATSAPP_PHONE_ID != "test_phone_id_placeholder"),
        "token_configured": bool(settings.WHATSAPP_TOKEN != "test_token_placeholder"),
        "verify_token": settings.WHATSAPP_VERIFY_TOKEN[:8] + "..." if settings.WHATSAPP_VERIFY_TOKEN else None,
        "phone_id": settings.WHATSAPP_PHONE_ID[:8] + "..." if settings.WHATSAPP_PHONE_ID else None
    }