import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, ADMIN_SESSION_STRING

async def main():
    if not ADMIN_SESSION_STRING:
        print("❌ No ADMIN_SESSION_STRING found in config.py")
        return

    print("🔍 Attempting to connect to Telegram using your session string...")
    client = TelegramClient(StringSession(ADMIN_SESSION_STRING), TELEGRAM_API_ID, TELEGRAM_API_HASH)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ The session string is INVALID or has been logged out/expired.")
            print("Telegram has disconnected this session. You will need an SMS code to log in again.")
            return

        print("✅ SUCCESS! The session string is still AUTHORIZED.")
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (@{me.username if me.username else 'No Username'})")
        
        print("\n📥 Checking Telegram Service Notifications (777000) for login codes...")
        # Telegram official notifications come from user ID 777000
        async for message in client.iter_messages(777000, limit=5):
            print(f"--- {message.date} ---")
            print(message.text)
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
