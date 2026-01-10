#!/usr/bin/env python3
"""
Main script for Telegram message logger.
This script connects to the Telegram API using a user account and monitors chats for deleted messages.
"""

import logging
import os
from datetime import datetime
from telethon import TelegramClient, events
from config import API_ID, API_HASH, PHONE_NUMBER, SESSION_NAME, LOG_DIR

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
def log_deleted_message(chat_id, chat_title, message_text, deleted_at):
    """Log deleted messages to a file."""
    ensure_log_dir()
    
    # Create a log entry
    log_entry = (
        f"Deleted Message in Chat: {chat_title} (ID: {chat_id})\n"
        f"Message: {message_text}\n"
        f"Deleted At: {deleted_at}\n"
        f"----------------------------------------\n"
    )
    
    # Write to log file
    log_file_path = os.path.join(LOG_DIR, f"deleted_messages_{chat_id}.log")
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_entry)
    
    logger.info(f"Logged deleted message in chat {chat_id}")

# Handler for deleted messages
async def handle_deleted_message(event):
    """Handle deleted messages."""
    chat_id = event.chat_id
    chat_title = event.chat.title if hasattr(event.chat, 'title') else "Private Chat"
    message_text = event.message.text if hasattr(event.message, 'text') else "No text content"
    deleted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log_deleted_message(chat_id, chat_title, message_text, deleted_at)

# Main function
async def main():
    """Start the client and monitor for deleted messages."""
    # Create the TelegramClient and pass it your credentials
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    # Connect to Telegram
    await client.start(PHONE_NUMBER)
    
    # Register handler for deleted messages
    client.add_event_handler(handle_deleted_message, events.MessageDeleted())
    
    # Start the client
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())