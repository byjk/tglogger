import logging
import os
from datetime import datetime
from typing import Optional
from config import LOG_DIR

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ensure the log directory exists
def ensure_log_dir() -> None:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

# Function to log messages
def log_message(
    action_type: str,
    chat_id: int,
    chat_title: str,
    message_id: int,
    timestamp: str,
    username: Optional[str] = None,
    message_text: Optional[str] = None,
    old_message_text: Optional[str] = None,
    new_message_text: Optional[str] = None
) -> None:
    """
    Log messages to a file based on action type.

    Args:
        action_type: 'deleted', 'received', or 'edited'
        chat_id: ID of the chat
        chat_title: Title of the chat
        message_id: ID of the message
        timestamp: Timestamp string
        username: Username of the sender (optional)
        message_text: Message text (for deleted and received messages)
        old_message_text: Old message text (for edited messages)
        new_message_text: New message text (for edited messages)
    """
    ensure_log_dir()

    # Create a log entry based on action type
    username_info = f"From User: {username}\n" if username else ""

    if action_type == 'deleted':
        log_entry = (
            f"Deleted Message in Chat: {chat_title} (ID: {chat_id})\n"
            f"{username_info}"
            f"Message ID: {message_id}\n"
            f"Message: {message_text}\n"
            f"Deleted At: {timestamp}\n"
            f"----------------------------------------\n"
        )
        log_file_path = os.path.join(LOG_DIR, f"{chat_id}_deleted_messages.log")
        logger.info(f"Logged deleted message in chat {chat_id}")
    elif action_type == 'received':
        log_entry = (
            f"Received Message in Chat: {chat_title} (ID: {chat_id})\n"
            f"{username_info}"
            f"Message ID: {message_id}\n"
            f"Message: {message_text}\n"
            f"Received At: {timestamp}\n"
            f"----------------------------------------\n"
        )
        log_file_path = os.path.join(LOG_DIR, f"{chat_id}_received_messages.log")
        logger.info(f"Logged received message in chat {chat_id}")
    elif action_type == 'edited':
        log_entry = (
            f"Edited Message in Chat: {chat_title} (ID: {chat_id})\n"
            f"{username_info}"
            f"Message ID: {message_id}\n"
            f"Old Message: {old_message_text}\n"
            f"New Message: {new_message_text}\n"
            f"Edited At: {timestamp}\n"
            f"----------------------------------------\n"
        )
        log_file_path = os.path.join(LOG_DIR, f"{chat_id}_edited_messages.log")
        logger.info(f"Logged edited message in chat {chat_id}")
    else:
        logger.error(f"Unknown action type: {action_type}")
        return

    # Write to log file
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)

# Function to log errors
def log_error(error_message: str) -> None:
    """Log errors to a separate file."""
    ensure_log_dir()

    # Create a log entry
    log_entry = (
        f"Error: {error_message}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"----------------------------------------\n"
    )

    # Write to log file
    log_file_path = os.path.join(LOG_DIR, "errors.log")
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)

    logger.error(f"Logged error: {error_message}")