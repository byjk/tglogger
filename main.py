#!/usr/bin/env python3
"""
Main script for Telegram message logger.
This script connects to the Telegram API using a user account and monitors chats for deleted messages.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from telethon import TelegramClient, events

# Load environment variables from .env file
load_dotenv()

# Function to validate configuration
def validate_config() -> None:
    """Validate that all required configuration values are present and valid."""
    errors = []
    
    # Validate API_ID
    api_id_str = os.getenv('API_ID')
    if not api_id_str:
        errors.append("API_ID is not set in environment variables")
    else:
        try:
            api_id = int(api_id_str)
            if api_id <= 0:
                errors.append("API_ID must be a positive integer")
        except ValueError:
            errors.append("API_ID must be a valid integer")
    
    # Validate API_HASH
    api_hash = os.getenv('API_HASH')
    if not api_hash or not api_hash.strip():
        errors.append("API_HASH is not set or is empty")
    elif len(api_hash) != 32:
        errors.append("API_HASH must be 32 characters long")
    
    # Validate PHONE_NUMBER
    phone_number = os.getenv('PHONE_NUMBER')
    if not phone_number or not phone_number.strip():
        errors.append("PHONE_NUMBER is not set or is empty")
    else:
        # Basic phone number validation (should start with + and contain only digits after)
        phone = phone_number.strip()
        if phone.startswith('+'):
            errors.append("PHONE_NUMBER must NOT start with '+' (e.g., 1234567890)")
        elif len(phone) < 8:
            errors.append("PHONE_NUMBER is too short")
        elif not phone[:].isdigit():
            errors.append("PHONE_NUMBER must contain only digits")
    
    # Validate optional ALLOWED_CHAT_IDS
    allowed_chat_ids_str = os.getenv('ALLOWED_CHAT_IDS', '')
    if allowed_chat_ids_str:
        for chat_id_str in allowed_chat_ids_str.split(','):
            chat_id_str = chat_id_str.strip()
            if chat_id_str:
                try:
                    int(chat_id_str)
                except ValueError:
                    errors.append(f"ALLOWED_CHAT_IDS contains invalid value: {chat_id_str} (must be integer)")
    
    # Validate DC_ID
    dc_id_str = os.getenv('DC_ID', '2')
    try:
        dc_id = int(dc_id_str)
        if dc_id < 1 or dc_id > 5:
            errors.append("DC_ID must be between 1 and 5")
    except ValueError:
        errors.append("DC_ID must be a valid integer")
    
    # Validate DC_PORT
    dc_port_str = os.getenv('DC_PORT', '443')
    try:
        int(dc_port_str)
    except ValueError:
        errors.append("DC_PORT must be a valid integer")
    
    # Validate DC_IP (basic check)
    dc_ip = os.getenv('DC_IP', '149.154.167.50')
    if not dc_ip or not dc_ip.strip():
        errors.append("DC_IP is not set or is empty")
    else:
        # Basic IP format validation
        ip_parts = dc_ip.strip().split('.')
        if len(ip_parts) != 4:
            errors.append("DC_IP must be a valid IPv4 address")
        else:
            try:
                for part in ip_parts:
                    num = int(part)
                    if num < 0 or num > 255:
                        errors.append("DC_IP must be a valid IPv4 address")
            except ValueError:
                errors.append("DC_IP must be a valid IPv4 address")
    
    # If there are any errors, print them and exit
    if errors:
        print("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        print("\nPlease check your .env file and ensure all required values are set correctly.")
        sys.exit(1)
    
    print("Configuration validation passed.")

# Validate configuration before using it
validate_config()

# Get configuration from environment variables
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
TG_PASSWORD = os.getenv('TG_PASSWORD') if os.getenv('TG_PASSWORD') else None
SESSION_NAME = os.getenv('SESSION_NAME', 'tglogger')
LOG_DIR = os.getenv('LOG_DIR', 'logs')

# Parse ALLOWED_CHAT_IDS from comma-separated string
ALLOWED_CHAT_IDS_str = os.getenv('ALLOWED_CHAT_IDS', '')
ALLOWED_CHAT_IDS = [int(chat_id) for chat_id in ALLOWED_CHAT_IDS_str.split(',') if chat_id.strip()] if ALLOWED_CHAT_IDS_str else []

# Telegram DC settings
DC_ID = int(os.getenv('DC_ID', 2))
DC_IP = os.getenv('DC_IP', '149.154.167.50')
DC_PORT = int(os.getenv('DC_PORT', 443))

# Global dictionary to store message history
message_history = {}

# Lock for thread-safe access to message_history
message_history_lock = asyncio.Lock()

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

# Main function
async def main() -> None:
    
    me = await client.get_me()
    print(me.stringify())
    # Connect to Telegram
    #await client.start(PHONE_NUMBER)
    
    # Register handler for deleted messages
    client.add_event_handler(handle_deleted_message, events.MessageDeleted())
    
    # Register handler for received messages
    client.add_event_handler(handle_received_message, events.NewMessage())
    
    # Register handler for edited messages
    client.add_event_handler(handle_edited_message, events.MessageEdited())
    
    # Start the client
    await client.run_until_disconnected()

if __name__ == '__main__':
    """Start the client and monitor for deleted messages."""
    # Create the TelegramClient and pass it your credentials
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    client.session.set_dc(DC_ID, DC_IP, DC_PORT)
    client.start(phone=PHONE_NUMBER, password=TG_PASSWORD)

    try:
        client.loop.run_until_complete(main())
    finally:
        client.disconnect()
