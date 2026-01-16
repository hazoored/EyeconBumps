from telethon import TelegramClient, functions
import inspect

print("--- send_message ---")
print(inspect.signature(TelegramClient.send_message))

print("\n--- functions.messages.ForwardMessages ---")
# Raw functions are classes, inspect __init__
print(inspect.signature(functions.messages.ForwardMessages.__init__))
