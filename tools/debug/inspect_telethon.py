from telethon import TelegramClient
import inspect

print(inspect.signature(TelegramClient.forward_messages))
print(inspect.getdoc(TelegramClient.forward_messages))
