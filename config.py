import os
import sys
from dotenv import load_dotenv

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
        if not phone.startswith('+'):
            errors.append("PHONE_NUMBER must start with '+' (e.g., +1234567890)")
        elif len(phone) < 9:
            errors.append("PHONE_NUMBER is too short")
        elif not phone[1:].isdigit():
            errors.append("PHONE_NUMBER must contain only digits after '+'")

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