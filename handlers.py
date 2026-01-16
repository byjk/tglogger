from datetime import datetime, timedelta
from config import ALLOWED_CHAT_IDS
from globals import message_history, message_history_lock
from logger import log_message, log_error, logger

# Function to clean up old messages from message_history
async def cleanup_old_messages() -> None:
    """Remove messages older than 5 hours from message_history, but only once per hour."""
    # Use function attribute to track last cleanup time
    if not hasattr(cleanup_old_messages, 'last_cleanup_time'):
        cleanup_old_messages.last_cleanup_time = None

    current_time = datetime.now()

    # Check if cleanup was called less than an hour ago - if so, do nothing
    if (cleanup_old_messages.last_cleanup_time is not None and
        (current_time - cleanup_old_messages.last_cleanup_time).total_seconds() < 3600):
        return  # Early return if called less than hour ago

    # Update last cleanup time
    cleanup_old_messages.last_cleanup_time = current_time

    five_hours_ago = current_time - timedelta(hours=5)

    # Create a list of message IDs to remove (to avoid modifying dict during iteration)
    messages_to_remove = []

    async with message_history_lock:
        for message_id, message_data in message_history.items():
            if isinstance(message_data, tuple) and len(message_data) >= 3:
                try:
                    message_date_str = message_data[0]
                    # Parse the date string (format: 'YYYY-MM-DD HH:MM:SS')
                    message_date = datetime.strptime(message_date_str, '%Y-%m-%d %H:%M:%S')

                    if message_date < five_hours_ago:
                        messages_to_remove.append(message_id)
                except (ValueError, IndexError):
                    # If date parsing fails, keep the message
                    continue
            elif isinstance(message_data, tuple) and len(message_data) >= 2:
                # Handle old format (date, text) for backward compatibility
                try:
                    message_date_str = message_data[0]
                    # Parse the date string (format: 'YYYY-MM-DD HH:MM:SS')
                    message_date = datetime.strptime(message_date_str, '%Y-%m-%d %H:%M:%S')

                    if message_date < five_hours_ago:
                        messages_to_remove.append(message_id)
                except (ValueError, IndexError):
                    # If date parsing fails, keep the message
                    continue

        # Remove the old messages
        for message_id in messages_to_remove:
            message_history.pop(message_id, None)

    if messages_to_remove:
        logger.info(f"Cleaned up {len(messages_to_remove)} old messages from message_history")

    logger.info("Performing hourly cleanup of old messages")

# Handler for deleted messages
async def handle_deleted_message(event) -> None:
    """Handle deleted messages."""
    try:
        message_id = event.deleted_id
        chat_id = event.chat_id

        # Check if chat_id is in allowed list, if not, do nothing
        # If ALLOWED_CHAT_IDS is empty, log all chats
        if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
            return

        chat_title = event.chat.title if hasattr(event.chat, 'title') else "Private Chat"
        deleted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if message exists in message_history, if not, do nothing
        # Remove message from global dictionary and get its data
        async with message_history_lock:
            message_data = message_history.pop(message_id, None)
            if message_data is None:
                return

        message_text = message_data[1] if isinstance(message_data, tuple) and len(message_data) >= 2 else message_data
        username = message_data[2] if isinstance(message_data, tuple) and len(message_data) >= 3 else None

        log_message('deleted', chat_id, chat_title, message_id, deleted_at, username, message_text)
    except Exception as e:
        log_error(f"Error in handle_deleted_message: {str(e)}")

# Handler for received messages
async def handle_received_message(event) -> None:
    """Handle received messages."""
    try:
        chat_id = event.chat_id

        # Check if chat_id is in allowed list, if not, do nothing
        # If ALLOWED_CHAT_IDS is empty, log all chats
        if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
            return

        chat_title = event.chat.title if hasattr(event.chat, 'title') else "Private Chat"
        message_id = event.message.id
        message_text = event.message.text if hasattr(event.message, 'text') else "No text content"
        received_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Extract username from sender
        username = None
        if hasattr(event.message, 'sender') and event.message.sender:
            if hasattr(event.message.sender, 'username') and event.message.sender.username:
                username = event.message.sender.username
            elif hasattr(event.message.sender, 'first_name'):
                username = event.message.sender.first_name
                if hasattr(event.message.sender, 'last_name') and event.message.sender.last_name:
                    username += f" {event.message.sender.last_name}"

        # Clean up old messages (function handles hourly logic internally)
        await cleanup_old_messages()

        # Store message in global dictionary as tuple (date, text, username)
        async with message_history_lock:
            message_history[message_id] = (received_at, message_text, username)

        log_message('received', chat_id, chat_title, message_id, received_at, username, message_text)
    except Exception as e:
        log_error(f"Error in handle_received_message: {str(e)}")

# Handler for edited messages
async def handle_edited_message(event) -> None:
    """Handle edited messages."""
    try:
        message_id = event.message.id
        chat_id = event.chat_id

        # Check if chat_id is in allowed list, if not, do nothing
        # If ALLOWED_CHAT_IDS is empty, log all chats
        if ALLOWED_CHAT_IDS and chat_id not in ALLOWED_CHAT_IDS:
            return

        chat_title = event.chat.title if hasattr(event.chat, 'title') else "Private Chat"
        new_message_text = event.message.text if hasattr(event.message, 'text') else "No text content"
        edited_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Check if message exists in message_history and get/update its data
        async with message_history_lock:
            if message_id not in message_history:
                return

            old_message_data = message_history.get(message_id, ("No date", "No old text content", None))
            old_message_text = old_message_data[1] if isinstance(old_message_data, tuple) and len(old_message_data) >= 2 else old_message_data

            if old_message_text == new_message_text:
                return

            # Get the username from the old message data if available
            old_username = old_message_data[2] if isinstance(old_message_data, tuple) and len(old_message_data) >= 3 else None

            # Update message in global dictionary as tuple (date, text, username)
            message_history[message_id] = (edited_at, new_message_text, old_username)

        log_message('edited', chat_id, chat_title, message_id, edited_at, old_username, None, old_message_text, new_message_text)
    except Exception as e:
        log_error(f"Error in handle_edited_message: {str(e)}")