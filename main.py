#!/usr/bin/env python3
"""
Main script for Telegram message logger.
This script connects to the Telegram API using a user account and monitors chats for deleted messages.
"""

import logging
import os
from datetime import datetime
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
        message_text = message_history.get(message_id, "No text content")
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
        
        # Store message in global dictionary
        message_history[message_id] = message_text
        
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
        old_message_text = message_history.get(message_id, "No old text content")
        new_message_text = event.message.text if hasattr(event.message, 'text') else "No text content"
        edited_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update message in global dictionary
        message_history[message_id] = new_message_text
        
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

    # client.session.set_dc(2, '149.154.167.40', 443)
    # client.start(
    #     phone='9996621234', code_callback=lambda: '22222'
    # )
    try:
        client.loop.run_until_complete(main())
    finally:
        client.disconnect()
