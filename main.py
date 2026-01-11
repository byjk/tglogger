#!/usr/bin/env python3
"""
Main script for Telegram message logger.
This script connects to the Telegram API using a user account and monitors chats for deleted messages.
"""

import logging
import os
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from config import API_ID, API_HASH, PHONE_NUMBER, TG_PASSWORD, SESSION_NAME, LOG_DIR, DC_ID, DC_IP, DC_PORT

# Global dictionary to store message history
message_history = {}

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ensure the log directory exists
def ensure_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

# Function to clean up old messages from message_history
def cleanup_old_messages():
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
    
    for message_id, message_data in message_history.items():
        if isinstance(message_data, tuple) and len(message_data) >= 2:
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

# Function to log deleted messages
def log_deleted_message(chat_id, chat_title, message_id, message_text, deleted_at):
    """Log deleted messages to a file."""
    ensure_log_dir()
    
    # Create a log entry
    log_entry = (
        f"Deleted Message in Chat: {chat_title} (ID: {chat_id})\n"
        f"Message ID: {message_id}\n"
        f"Message: {message_text}\n"
        f"Deleted At: {deleted_at}\n"
        f"----------------------------------------\n"
    )
    
    # Write to log file
    log_file_path = os.path.join(LOG_DIR, f"deleted_messages_{chat_id}.log")
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)
    
    logger.info(f"Logged deleted message in chat {chat_id}")

# Function to log errors
def log_error(error_message):
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

# Function to log received messages
def log_received_message(chat_id, chat_title, message_id, message_text, received_at):
    """Log received messages to a file."""
    ensure_log_dir()
    
    # Create a log entry
    log_entry = (
        f"Received Message in Chat: {chat_title} (ID: {chat_id})\n"
        f"Message ID: {message_id}\n"
        f"Message: {message_text}\n"
        f"Received At: {received_at}\n"
        f"----------------------------------------\n"
    )
    
    # Write to log file
    log_file_path = os.path.join(LOG_DIR, f"received_messages_{chat_id}.log")
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)
    
    logger.info(f"Logged received message in chat {chat_id}")

# Function to log edited messages
def log_edited_message(chat_id, chat_title, message_id, old_message_text, new_message_text, edited_at):
    """Log edited messages to a file."""
    ensure_log_dir()
    
    # Create a log entry
    log_entry = (
        f"Edited Message in Chat: {chat_title} (ID: {chat_id})\n"
        f"Message ID: {message_id}\n"
        f"Old Message: {old_message_text}\n"
        f"New Message: {new_message_text}\n"
        f"Edited At: {edited_at}\n"
        f"----------------------------------------\n"
    )
    
    # Write to log file
    log_file_path = os.path.join(LOG_DIR, f"edited_messages_{chat_id}.log")
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)
    
    logger.info(f"Logged edited message in chat {chat_id}")

# Handler for deleted messages
async def handle_deleted_message(event):
    """Handle deleted messages."""
    try:
        chat_id = event.chat_id
        chat_title = event.chat.title if hasattr(event.chat, 'title') else "Private Chat"
        message_id = event.deleted_id
        message_data = message_history.get(message_id, ("No date", "No text content"))
        message_text = message_data[1] if isinstance(message_data, tuple) else message_data
        deleted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Remove message from global dictionary
        message_history.pop(message_id, None)
        
        log_deleted_message(chat_id, chat_title, message_id, message_text, deleted_at)
    except Exception as e:
        log_error(f"Error in handle_deleted_message: {str(e)}")

# Handler for received messages
async def handle_received_message(event):
    """Handle received messages."""
    try:
        chat_id = event.chat_id
        chat_title = event.chat.title if hasattr(event.chat, 'title') else "Private Chat"
        message_id = event.message.id
        message_text = event.message.text if hasattr(event.message, 'text') else "No text content"
        received_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Clean up old messages (function handles hourly logic internally)
        cleanup_old_messages()
        
        # Store message in global dictionary as tuple (date, text)
        message_history[message_id] = (received_at, message_text)
        
        log_received_message(chat_id, chat_title, message_id, message_text, received_at)
    except Exception as e:
        log_error(f"Error in handle_received_message: {str(e)}")

# Handler for edited messages
async def handle_edited_message(event):
    """Handle edited messages."""
    try:
        chat_id = event.chat_id
        chat_title = event.chat.title if hasattr(event.chat, 'title') else "Private Chat"
        message_id = event.message.id
        old_message_data = message_history.get(message_id, ("No date", "No old text content"))
        old_message_text = old_message_data[1] if isinstance(old_message_data, tuple) else old_message_data
        new_message_text = event.message.text if hasattr(event.message, 'text') else "No text content"
        if (old_message_text == new_message_text):
            return
        edited_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update message in global dictionary as tuple (date, text)
        message_history[message_id] = (edited_at, new_message_text)
        
        log_edited_message(chat_id, chat_title, message_id, old_message_text, new_message_text, edited_at)
    except Exception as e:
        log_error(f"Error in handle_edited_message: {str(e)}")

# Main function
async def main():
    
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
