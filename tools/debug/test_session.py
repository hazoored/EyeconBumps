#!/usr/bin/env python3
"""Quick test to verify the session string works"""
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, ADMIN_SESSION_STRING

async def test_session():
    print(f"API ID: {TELEGRAM_API_ID}")
    print(f"Session string length: {len(ADMIN_SESSION_STRING)}")
    print(f"Session string preview: {ADMIN_SESSION_STRING[:50]}...")
    
    try:
        session = StringSession(ADMIN_SESSION_STRING)
        client = TelegramClient(session, TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await client.connect()
        
        if await client.is_user_authorized():
            me = await client.get_me()
            print(f"✅ Session is VALID! Logged in as: {me.first_name} (@{me.username or 'no username'})")
        else:
            print("❌ Session exists but not authorized")
        
        await client.disconnect()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_session())
