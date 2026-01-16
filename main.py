#!/usr/bin/env python3
"""
Main script for Telegram message logger.
This script connects to the Telegram API using a user account and monitors chats for deleted messages.
"""

from telethon import TelegramClient, events
from config import API_ID, API_HASH, PHONE_NUMBER, TG_PASSWORD, SESSION_NAME, DC_ID, DC_IP, DC_PORT
from handlers import handle_deleted_message, handle_received_message, handle_edited_message

# Main function
async def main() -> None:

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
