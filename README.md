# Telegram Message Logger

This project is a Python-based application that monitors your Telegram account for deleted, edited, and received messages. It logs these events to separate files for easy tracking and analysis.

## Features

- **Monitor Deleted Messages**: Logs when a message is deleted in any of your chats.
- **Monitor Edited Messages**: Logs when a message is edited, including both the old and new text.
- **Monitor Received Messages**: Logs all received messages with their IDs and content.
- **Configurable**: All settings are stored in a configuration file for easy customization.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/byjk/tglogger.git
   cd tglogger
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - On Linux/Mac:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Configuration**:
   - Copy `config.example.py` to `config.py`:
     ```bash
     cp config.example.py config.py
     ```
   - Edit `config.py` and fill in your `API_ID`, `API_HASH`, and `PHONE_NUMBER`.
   - You can get `API_ID` and `API_HASH` from https://my.telegram.org by following the instructions in the `config.example.py` file.

## Running the Application

1. **Start the Application**:
   ```bash
   python main.py
   ```

2. **Enter the Verification Code**:
   - When you run the application for the first time, you will receive a verification code on your Telegram account.
   - Enter this code in the terminal to complete the authentication process.
   - Note: The verification code may not arrive immediately after creating your API credentials. It may take several hours or even a day to receive the code. Please be patient and try again later if you do not receive the code right away.

## Viewing Logs

All logs are stored in the `logs` directory, which is created automatically when the application starts. The logs are categorized as follows:

- **Deleted Messages**: `logs/deleted_messages_{chat_id}.log`
- **Edited Messages**: `logs/edited_messages_{chat_id}.log`
- **Received Messages**: `logs/received_messages_{chat_id}.log`
- **Errors**: `logs/errors.log`

Each log file contains detailed information about the event, including the chat title, message ID, message content, and timestamp.

## Configuration

The `config.py` file contains all the necessary settings for the application:

- `API_ID`: Your Telegram API ID.
- `API_HASH`: Your Telegram API hash.
- `PHONE_NUMBER`: Your phone number in international format.
- `TG_PASSWORD`: Your Telegram password (if you have two-factor authentication enabled).
- `SESSION_NAME`: The name of the session file.
- `LOG_DIR`: The directory where logs will be stored.
- `DC_ID`: The Telegram Data Center ID.
- `DC_IP`: The Telegram Data Center IP address.
- `DC_PORT`: The Telegram Data Center port.