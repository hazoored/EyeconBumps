import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from telegram_manager import TelegramManager
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

class TestTelegramManagerRefactor(unittest.IsolatedAsyncioTestCase):
    async def test_get_user_client_creates_new_client(self):
        manager = TelegramManager()
        fake_session = "1BVtsOMQBuFakeSessionString..." 
        
        with patch('telegram_manager.TelegramClient') as MockClient, \
             patch('telegram_manager.StringSession') as MockSession:
            # Setup mock
            mock_instance = MockClient.return_value
            mock_instance.connect = AsyncMock()
            mock_instance.is_user_authorized = AsyncMock(return_value=True)
            mock_instance.is_connected = MagicMock(return_value=True)
            
            # Call method
            client = await manager.get_user_client(fake_session)
            
            # Verify usage
            self.assertTrue(MockClient.called)
            args, kwargs = MockClient.call_args
            # args[0] is session, args[1] api_id, args[2] api_hash
            self.assertEqual(args[1], TELEGRAM_API_ID)
            self.assertEqual(args[2], TELEGRAM_API_HASH)
            
            mock_instance.connect.assert_called()
            self.assertEqual(client, mock_instance)
            self.assertIn(fake_session, manager.user_clients)

    async def test_get_user_client_uses_cache(self):
        manager = TelegramManager()
        fake_session = "cached_session"
        mock_client = MagicMock()
        mock_client.is_connected = MagicMock(return_value=True)
        manager.user_clients[fake_session] = mock_client
        
        with patch('telegram_manager.TelegramClient') as MockClient:
            client = await manager.get_user_client(fake_session)
            self.assertEqual(client, mock_client)
            MockClient.assert_not_called()

    async def test_forward_message_uses_session(self):
        manager = TelegramManager()
        fake_session = "session_for_forwarding"
        
        with patch.object(manager, 'get_user_client', new_callable=AsyncMock) as mock_get_client:
            mock_client = MagicMock()
            mock_client.forward_messages = AsyncMock()
            mock_get_client.return_value = mock_client
            
            await manager.forward_message(-100, 1, -200, 50, session_string=fake_session)
            
            mock_get_client.assert_called_with(fake_session)
            mock_client.forward_messages.assert_called()

if __name__ == '__main__':
    unittest.main()
