import asyncio

# Global dictionary to store message history
message_history = {}

# Lock for thread-safe access to message_history
message_history_lock = asyncio.Lock()