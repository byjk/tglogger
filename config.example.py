"""
Example configuration file for Telegram message logger.
Copy this file to config.py and fill in your actual credentials.

To get API_ID and API_HASH:
1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to "API development tools"
4. Fill in the form to create a new application
5. After creating the application, you will receive API_ID and API_HASH

PHONE_NUMBER should be your phone number in international format (e.g., +1234567890)
TG_PASSWORD is optional and needed only if your account has two-factor authentication enabled

DC_ID, DC_IP, and DC_PORT are Telegram Data Center settings.
You can find the list of available DC addresses here: https://core.telegram.org/bots/api#available-datacenters
"""

# Replace these with your actual credentials
API_ID = "YOUR_API_ID"
API_HASH = "YOUR_API_HASH"
PHONE_NUMBER = "YOUR_PHONE_NUMBER"
TG_PASSWORD = None

# Session file name
SESSION_NAME = "session_name"

# Directory for storing logs
LOG_DIR = "logs"

# Telegram DC settings
DC_ID = 2
DC_IP = "149.154.167.50"
DC_PORT = 443