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

            # Handle the message (now async)
            response = await whatsapp_service.handle_text_message(data)

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


@router.post("/send-message")
async def send_test_message(
    recipient: str = Query(..., description="Phone number to send message to"),
    message: str = Query(..., description="Message text to send")
):
    """
    Send a test message via WhatsApp (for testing purposes)
    """
    try:
        from app.services.whatsapp_service import whatsapp_service

        logger.info(f"📤 SENDING TEST MESSAGE:")
        logger.info(f"   To: {recipient}")
        logger.info(f"   Message: '{message}'")

        result = whatsapp_service.send_message(recipient, message, "test")

        if result.get("success"):
            logger.info(f"✅ Test message sent successfully to {recipient}")
            return {
                "status": "success",
                "message": "Message sent successfully",
                "recipient": recipient,
                "sent_message": message,
                "message_id": result.get("message_id"),
                "whatsapp_response": result.get("response")
            }
        else:
            logger.error(f"❌ Failed to send test message to {recipient}")
            return {
                "status": "failed",
                "message": f"Failed to send message: {result.get('error', 'Unknown error')}",
                "recipient": recipient,
                "error_details": result
            }

    except Exception as e:
        logger.error(f"❌ Error sending test message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.post("/send-template")
async def send_template_message(
    recipient: str = Query(..., description="Phone number to send template to"),
    template_name: str = Query(..., description="Name of the approved template"),
    language: str = Query(default="en_US", description="Language code")
):
    """
    Send a template message via WhatsApp
    """
    try:
        from app.services.whatsapp_service import whatsapp_service

        logger.info(f"📤 SENDING TEMPLATE MESSAGE:")
        logger.info(f"   To: {recipient}")
        logger.info(f"   Template: '{template_name}' ({language})")

        result = whatsapp_service.send_template_message(recipient, template_name, language)

        if result.get("success"):
            return {
                "status": "success",
                "message": "Template message sent successfully",
                "recipient": recipient,
                "template": template_name,
                "message_id": result.get("message_id"),
                "whatsapp_response": result.get("response")
            }
        else:
            return {
                "status": "failed",
                "message": f"Failed to send template: {result.get('error', 'Unknown error')}",
                "recipient": recipient,
                "template": template_name,
                "error_details": result
            }

    except Exception as e:
        logger.error(f"❌ Error sending template message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send template: {str(e)}")


@router.post("/send-interactive")
async def send_interactive_message(
    recipient: str = Query(..., description="Phone number to send message to"),
    message_text: str = Query(..., description="Message text"),
    button_1_id: str = Query(..., description="Button 1 ID"),
    button_1_title: str = Query(..., description="Button 1 title"),
    button_2_id: str = Query(default="", description="Button 2 ID (optional)"),
    button_2_title: str = Query(default="", description="Button 2 title (optional)"),
    button_3_id: str = Query(default="", description="Button 3 ID (optional)"),
    button_3_title: str = Query(default="", description="Button 3 title (optional)")
):
    """
    Send an interactive message with buttons via WhatsApp
    """
    try:
        from app.services.whatsapp_service import whatsapp_service

        # Build buttons list
        buttons = [
            {
                "type": "reply",
                "reply": {
                    "id": button_1_id,
                    "title": button_1_title
                }
            }
        ]

        if button_2_id and button_2_title:
            buttons.append({
                "type": "reply",
                "reply": {
                    "id": button_2_id,
                    "title": button_2_title
                }
            })

        if button_3_id and button_3_title:
            buttons.append({
                "type": "reply",
                "reply": {
                    "id": button_3_id,
                    "title": button_3_title
                }
            })

        logger.info(f"📤 SENDING INTERACTIVE MESSAGE:")
        logger.info(f"   To: {recipient}")
        logger.info(f"   Text: '{message_text}'")
        logger.info(f"   Buttons: {len(buttons)}")

        result = whatsapp_service.send_interactive_message(recipient, message_text, buttons)

        if result.get("success"):
            return {
                "status": "success",
                "message": "Interactive message sent successfully",
                "recipient": recipient,
                "button_count": len(buttons),
                "message_id": result.get("message_id"),
                "whatsapp_response": result.get("response")
            }
        else:
            return {
                "status": "failed",
                "message": f"Failed to send interactive message: {result.get('error', 'Unknown error')}",
                "recipient": recipient,
                "error_details": result
            }

    except Exception as e:
        logger.error(f"❌ Error sending interactive message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send interactive message: {str(e)}")


@router.get("/webhook/logs")
async def get_recent_webhook_logs():
    """
    Get recent webhook activity for debugging
    """
    try:
        import os
        log_file = "logs/app.log"

        if not os.path.exists(log_file):
            return {"logs": [], "message": "No log file found"}

        # Read last 50 lines of log file
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-50:] if len(lines) > 50 else lines

        # Filter for webhook-related logs
        webhook_logs = [
            line.strip() for line in recent_lines
            if any(keyword in line for keyword in ['webhook', 'INCOMING MESSAGE', 'WhatsApp', 'MESSAGE'])
        ]

        return {
            "logs": webhook_logs[-20:],  # Last 20 webhook-related logs
            "total_recent_logs": len(recent_lines),
            "webhook_logs_found": len(webhook_logs)
        }

    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return {"error": f"Failed to read logs: {str(e)}"}


@router.get("/webhook/sessions")
async def get_session_stats():
    """
    Get current session statistics for monitoring multi-user support
    """
    try:
        from app.services.session_service import session_manager

        stats = session_manager.get_session_stats()

        return {
            "status": "success",
            "session_stats": stats,
            "message": f"Currently managing {stats['active_sessions']} active sessions"
        }

    except Exception as e:
        logger.error(f"Error getting session stats: {e}")
        return {"error": f"Failed to get session stats: {str(e)}"}


@router.post("/webhook/end-session")
async def end_user_session(user_id: str = Query(..., description="User ID to end session for")):
    """
    End a specific user session (for testing/admin purposes)
    """
    try:
        from app.services.session_service import session_manager

        success = session_manager.end_session(user_id)

        if success:
            return {
                "status": "success",
                "message": f"Session ended for user {user_id}"
            }
        else:
            return {
                "status": "not_found",
                "message": f"No active session found for user {user_id}"
            }

    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return {"error": f"Failed to end session: {str(e)}"}