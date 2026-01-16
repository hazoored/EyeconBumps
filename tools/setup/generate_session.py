from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

def main():
    print("=== Telegram Session String Generator ===")
    print(f"Using API ID: {TELEGRAM_API_ID}")

    with TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        print("\nPlease follow the prompts to log in (Phone Number, Code, 2FA if enabled).")

        if not client.is_user_authorized():
             client.start()
        
        print("\nLogin Successful!")
        session_string = client.session.save()
        print("\n=== YOUR SESSION STRING TO COPY ===")
        print(session_string)
        print("===================================")
        print("\nCopy the string above and paste it into config.py as ADMIN_SESSION_STRING")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
