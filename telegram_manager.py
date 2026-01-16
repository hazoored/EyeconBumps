import asyncio
import os
import logging
import random
from telethon import TelegramClient, events, functions, types, connection, errors
from telethon.sessions import StringSession
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, ADMIN_SESSION_STRING, TELEGRAM_PROXY, DEVICE_MODELS
import hashlib
import time

from utils.logger import bot_logger as logger

class TelegramManager:
    def __init__(self):
        client_kwargs = {}
        
        # Determine if proxy is MTProto (host, port, secret)
        if TELEGRAM_PROXY and isinstance(TELEGRAM_PROXY, tuple) and len(TELEGRAM_PROXY) == 3 and isinstance(TELEGRAM_PROXY[2], str):
            host, port, secret = TELEGRAM_PROXY
            logger.info(f"Configuring MTProto Proxy: {host}:{port}")
            client_kwargs['connection'] = connection.ConnectionTcpMTProxyRandomizedIntermediate
            client_kwargs['proxy'] = TELEGRAM_PROXY
        else:
            client_kwargs['proxy'] = TELEGRAM_PROXY

        # Stealth client configuration

        # Stealth client configuration: We will now override this dynamically per session!
        # Default fallback if needed
        self.default_client_config = {
            'device_model': 'iPhone 15 Pro Max',
            'system_version': 'iOS 17.2.1',
            'app_version': '10.3.1',
            'lang_code': 'en',
            'system_lang_code': 'en-US'
        }
        client_kwargs.update(self.default_client_config)

        self.client_kwargs = client_kwargs # Save for new clients
        self.user_clients = {} # Cache for user clients

        # User Client
        # We try to use the session string if available, otherwise file based.
        # This client represents the ADMIN/DEFAULT account.
        if ADMIN_SESSION_STRING:
            session = StringSession(ADMIN_SESSION_STRING)
            self.client = TelegramClient(
                session,
                TELEGRAM_API_ID, 
                TELEGRAM_API_HASH,
                **client_kwargs
            )
            logger.info(f"Using provided ADMIN_SESSION_STRING (Length: {len(str(ADMIN_SESSION_STRING))})")
            
            # --- FORCE CLEANUP ---
            # If we are using StringSession, ensure no file-based session exists to confuse things
            if os.path.exists('admin_session.session'):
                try:
                    os.remove('admin_session.session')
                    logger.warning("Deleted stale 'admin_session.session' file to prevent conflicts.")
                except Exception as e:
                    logger.warning(f"Failed to delete stale session file: {e}")

        else:
            self.client = TelegramClient(
                'admin_session', 
                TELEGRAM_API_ID, 
                TELEGRAM_API_HASH,
                **client_kwargs
            )
            logger.info("Using file-based session 'admin_session' since ADMIN_SESSION_STRING is empty.")

    async def start(self):
        if self.client:
            try:
                logger.info("Connecting to Default Telegram Account (timeout=30s)...")
                await asyncio.wait_for(self.client.connect(), timeout=30)
                
                if not await self.client.is_user_authorized():
                     logger.warning("Default client is not authorized! Some features might require a default session.")
                else:
                     me = await self.client.get_me()
                     logger.info(f"Default client connected and authorized as: {me.first_name} (ID: {me.id})")
                     
            except asyncio.TimeoutError:
                logger.warning("Could not connect to Telegram: Request timed out (30s).")
            except Exception as e:
                logger.error(f"Could not connect to Telegram: {e}", exc_info=True)

    async def get_user_client(self, session_string):
        """
        Returns a connected TelegramClient for the given session string.
        Maintains a cache of clients to avoid reconnecting.
        """
        if not session_string:
            logger.debug("Requesting default/admin client.")
            return self.client
        
        if session_string in self.user_clients:
            logger.debug("Returning cached client for session.")
            client = self.user_clients[session_string]
            if not client.is_connected():
                logger.info("Cached client disconnected. Reconnecting...")
                await client.connect()
            return client
        
        # Create new client
        logger.info("Initializing new client for provided session string...")
        # Telemetry Spoofing: Deterministically select a device model based on session hash
        # This ensures the SAME session always gets the SAME device config.
        session_hash = int(hashlib.md5(session_string.encode()).hexdigest(), 16)
        device_config = DEVICE_MODELS[session_hash % len(DEVICE_MODELS)]
        
        logger.debug(f"Assigned Device Telemetry: {device_config['device_model']} ({device_config['system_version']})")

        current_kwargs = self.client_kwargs.copy()
        current_kwargs.update(device_config)

        try:
            session = StringSession(session_string)
            client = TelegramClient(
                session,
                TELEGRAM_API_ID,
                TELEGRAM_API_HASH,
                **current_kwargs
            )
            await client.connect()
            if not await client.is_user_authorized():
                logger.error("Session is invalid or not authorized.")
                raise Exception("Session is invalid or not authorized.")
            
            me = await client.get_me()
            logger.info(f"New client connected: {me.first_name} ({me.id})")
            
            self.user_clients[session_string] = client
            return client
        except Exception as e:
            logger.error(f"Failed to create client for session: {e}", exc_info=True)
            raise e
    
    async def get_message_from_link(self, link, session_string=None):
        """
        Resolves a Telegram message link to (chat_id, message_id).
        Link formats: 
        - https://t.me/c/1234567890/123 (Private/Public Supergroup with ID)
        - https://t.me/username/123 (Public Channel/Group)
        """
        client = await self.get_user_client(session_string)
        if not client or not await client.is_user_authorized():
            raise Exception("Telegram Client not connected or invalid session.")

        try:
            link = link.strip()
            # Handle standard invite links or message links
            
            if "t.me/c/" in link:
                # Format: https://t.me/c/CHANNEL_ID/MSG_ID
                # CHANNEL_ID is usually the ID without -100 prefix for private supergroups
                parts = link.split('t.me/c/')[1].split('/')
                channel_id_part = parts[0]
                msg_id = int(parts[1])
                
                # Try constructing peer ID
                peer_id = int(f"-100{channel_id_part}")
                
                # To get a message from a private channel/group we aren't "seen" yet by ID,
                # we might need the entity. If we are already in it, get_entity works.
                # If it's a private chat we just joined, get_entity(peer_id) should work if cache is up to date 
                # or if we fetch dialogs. Look up by ID is tricky if not cached.
                
                try:
                    entity = await client.get_entity(peer_id)
                except ValueError:
                    # Attempt to refresh dialogs?
                    await client.get_dialogs(limit=None)
                    entity = await client.get_entity(peer_id)

                msgs = await client.get_messages(entity, ids=[msg_id])
                if not msgs or not msgs[0]:
                    raise Exception("Message not found or not accessible (are you a member?).")
                    
                return peer_id, msg_id

            elif "t.me/" in link:
                # Format: https://t.me/USERNAME/MSG_ID
                parts = link.split('t.me/')[1].split('/')
                username = parts[0]
                msg_id = int(parts[1])
                
                entity = await client.get_entity(username)
                msgs = await client.get_messages(entity, ids=[msg_id])
                if not msgs or not msgs[0]:
                    raise Exception("Message not found.")
                
                return entity.id, msg_id
            
            else:
                 raise Exception("Invalid link format. Use https://t.me/c/... or https://t.me/username/...")

        except Exception as e:
            logger.error(f"Failed to resolve link {link}: {e}")
            raise Exception(f"Failed to resolve link: {e}")

    async def forward_message(self, target_chat_id, target_topic_id, source_chat_id, source_msg_id, session_string=None):
        logger.info(f"Forwarding from {source_chat_id}:{source_msg_id} to {target_chat_id} (Topic: {target_topic_id})...")
        
        client = await self.get_user_client(session_string)
        if not client:
             logger.error("Client not initialized")
             return False, None
        
        if session_string:
            logger.debug("Using user-provided session string.")
        else:
            logger.debug("Using default admin session.")

        try:
             # Resolve entities
             # We use get_input_entity to ensure we have the correct AccessHash/InputPeer
             try:
                 from_peer = await client.get_input_entity(source_chat_id)
                 to_peer = await client.get_input_entity(target_chat_id)
             except ValueError:
                 # Attempt to refresh dialogs if entity not found
                 logger.info(f"Entities not found for {source_chat_id} or {target_chat_id}. Refreshing dialogs...")
                 await client.get_dialogs(limit=None)
                 # Retry resolving entities
                 from_peer = await client.get_input_entity(source_chat_id)
                 to_peer = await client.get_input_entity(target_chat_id)
             
             # Prepare request args
             request_kwargs = {
                 'from_peer': from_peer,
                 'id': [source_msg_id],
                 'to_peer': to_peer,
                 'random_id': [random.randint(0, 2**63 - 1)]
             }
             
             # Add topic ID if present
             if target_topic_id:
                 request_kwargs['top_msg_id'] = target_topic_id
                 

             # --- BIOLOGICAL BEHAVIOR ---
             # 1. Send Read Acknowledge (Mark chat as read)
             try:
                 await client.send_read_acknowledge(to_peer)
             except:
                 pass # Ignore if fails, not critical

             # 2. Send Typing Action (Simulate typing)
             # Random delay for typing duration (2 to 5 seconds)
             typing_duration = random.randint(2, 5)
             logger.info(f"Simulating typing in {target_chat_id} for {typing_duration}s...")
             try:
                 # 'action' parameter for SendMessageTypingAction is generic in recent Telethon or just use the convenience method
                 async with client.action(to_peer, 'typing'):
                     await asyncio.sleep(typing_duration)
             except Exception as type_err:
                 logger.warning(f"Typing simulation failed: {type_err}. Proceeding with send.")
                 # Just wait if action context manager fails
                 await asyncio.sleep(typing_duration)
            
             # Use generic Raw API Request
             result = await client(functions.messages.ForwardMessagesRequest(**request_kwargs))

             # Result is Updates object. Extract ID to build link.
             new_msg_id = None
             if hasattr(result, 'updates'):
                 for u in result.updates:
                     if isinstance(u, types.UpdateMessageID):
                         new_msg_id = u.id
                         break
                     if isinstance(u, types.UpdateNewMessage):
                         new_msg_id = u.message.id
                         break
                     if isinstance(u, types.UpdateNewChannelMessage):
                        new_msg_id = u.message.id
                        break
             
             # Construct Link
             msg_link = None
             if new_msg_id:
                 try:
                    # Resolve to_peer again to check if it has username
                    entity = await client.get_entity(to_peer)
                    if hasattr(entity, 'username') and entity.username:
                        msg_link = f"https://t.me/{entity.username}/{new_msg_id}"
                    else:
                        # Private channel/group link format: t.me/c/CHANNEL_ID_WITHOUT_PREFIX/MSG_ID
                        clean_id = str(abs(target_chat_id)).replace("100", "", 1) if str(target_chat_id).startswith("-100") else abs(target_chat_id)
                        msg_link = f"https://t.me/c/{clean_id}/{new_msg_id}"
                 except Exception as link_err:
                     logger.warning(f"Failed to generate link: {link_err}")

             logger.info("Forwarding successful.")
             return True, msg_link
             
        except (errors.RPCError, ValueError) as e:
            # Check for common forwarding restrictions or specific errors
            # 403 CHAT_SEND_WEBPAGE_FORBIDDEN
            # 400 CHAT_FORWARDS_RESTRICTED
            error_msg = str(e)
            
            # Telethon errors often have a .name attribute (e.g. 'ChatSendWebpageForbiddenError')
            error_name = getattr(e, 'name', '')
            
            if (
                "ChatSendWebpageForbidden" in error_name or 
                "CHAT_SEND_WEB_FORBIDDEN" in error_msg or 
                "CHAT_FORWARDS_RESTRICTED" in error_msg or
                "ALLOW_PAYMENT_REQUIRED" in error_msg
            ):
                 logger.info(f"Group {target_chat_id} has restrictions or requires payment. Attempting refined @jaalebis relay bypass...")
                 try:
                     # 1. Resolve @jaalebis
                     relay_peer = await client.get_entity('jaalebis')
                     
                     # 2. Fetch the LATEST message from the DM chat with @jaalebis
                     relay_msgs = await client.get_messages(relay_peer, limit=1)
                     if not relay_msgs or not relay_msgs[0]:
                         logger.error("No messages found in @jaalebis DM to relay.")
                         return
                     
                     source_msg_to_relay = relay_msgs[0]
                     logger.info(f"Fetched latest message (ID: {source_msg_to_relay.id}) from @jaalebis DM.")
                     
                     # 3. Forward FROM @jaalebis DM to the target group
                     relay_request_kwargs = {
                         'from_peer': relay_peer,
                         'id': [source_msg_to_relay.id],
                         'to_peer': to_peer,
                         'random_id': [random.randint(0, 2**63 - 1)]
                     }
                     if target_topic_id:
                         relay_request_kwargs['top_msg_id'] = target_topic_id
                         
                     await client(functions.messages.ForwardMessagesRequest(**relay_request_kwargs))
                     logger.info(f"Refined relay bypass via @jaalebis successful for group {target_chat_id}.")
                     return True
                     
                 except Exception as relay_err:
                     logger.error(f"Refined relay bypass failed: {relay_err}")
                     # If bypass fails, we still want to log it as a restriction failure
                     return False
 
            # Generic fallback if not caught above
            elif "FORBIDDEN" in error_msg or "RESTRICTED" in error_msg:
                 logger.warning(f"Forwarding failed to {target_chat_id} due to restriction: {e} | Skipping group.")
                 return False
            
            elif isinstance(e, errors.FloodWaitError):
                logger.error(f"FloodWaitError: Required to wait {e.seconds} seconds.")
                if e.seconds > 200:
                    logger.warning(f"Wait time too long ({e.seconds}s). Skipping group {target_chat_id}.")
                else:
                    logger.warning(f"Skipping group {target_chat_id} due to rate limit.")
                return False, None
            
            elif isinstance(e, errors.SlowModeWaitError):
                logger.warning(f"Group {target_chat_id} is in Slow Mode. Wait required: {e.seconds}s. Skipping group.")
                return False, None
            
            elif isinstance(e, errors.UserBannedInChannelError):
                logger.warning(f"User is BANNED in group {target_chat_id}. Skipping group.")
                return False, None

            elif isinstance(e, errors.ChatWriteForbiddenError) or "You can't write in this chat" in str(e):
                 logger.warning(f"Forwarding failed to {target_chat_id}: Write access forbidden. Skipping group.")
                 return False, None

            else:
                if "Could not find the input entity" in str(e):
                    logger.warning(f"Skipping group {target_chat_id}: User not member or entity not found.")
                    return False, None
                else:
                    logger.error(f"Forwarding error: {e}")
                    # For other unknown RPC errors, we might want to log but not crash the whole loop?
                    # But ad_runner usually catches exceptions loop-side. 
                    # If we raise here, it cancels the specific ad run for THIS group? 
                    # ad_runner has a try/except inside the loop for groups?
                    # Let's verify ad_runner.py structure. 
                    # ad_runner.py loops over GROUPS_CONFIG. It has a try/except around the forward_message call.
                    # So raising e here is fine, it will just be caught there.
                    raise e
        except Exception as e:
            logger.error(f"Forwarding error: {e}", exc_info=True)
            raise e

    async def join_folder(self, invite_link, session_string=None):
        """
        Joins a Telegram chat folder (addlist) using the provided invite link.
        Link format: https://t.me/addlist/HASH
        """
        client = await self.get_user_client(session_string)
        if not client:
            raise Exception("Telegram client not initialized.")

        try:
            # Extract hash from link
            if "/addlist/" not in invite_link:
                raise Exception("Invalid chat folder link. Must contain '/addlist/'")
            
            chatlist_hash = invite_link.split("/addlist/")[1].split("?")[0]
            logger.info(f"Attempting to join chat folder with hash: {chatlist_hash}")

            # 1. Check the invite
            invite = await client(functions.chatlists.CheckChatlistInviteRequest(
                slug=chatlist_hash
            ))

            if isinstance(invite, types.chatlists.ChatlistInviteAlready):
                 logger.info("Account already joined this folder. Removing existing folder to replace it...")
                 try:
                     # JoinChatlistInviteRequest needs peers, and LeaveChatlistRequest does too.
                     # already_peers are the ones currently in the folder for this user.
                     # Use InputChatlistDialogFilter as InputChatlistSlug doesn't exist in this version.
                     await client(functions.chatlists.LeaveChatlistRequest(
                         chatlist=types.InputChatlistDialogFilter(filter_id=invite.filter_id),
                         peers=invite.already_peers
                     ))
                     logger.info("Existing folder removed successfully.")
                     
                     # Now re-check to get a clean invite state
                     invite = await client(functions.chatlists.CheckChatlistInviteRequest(
                         slug=chatlist_hash
                     ))
                 except Exception as leave_err:
                     logger.warning(f"Failed to remove existing folder: {leave_err}")
                     # Return the actual error to help debugging
                     return f"Already joined (Replacement failed: {str(leave_err)})"

            # 2. Join the invite
            # We need to provide the peers that are in the folder
            peers = []
            if hasattr(invite, 'peers'):
                peers = invite.peers
            
            await client(functions.chatlists.JoinChatlistInviteRequest(
                slug=chatlist_hash,
                peers=peers
            ))

            logger.info("Successfully joined the chat folder.")
            return "Success"

        except errors.RPCError as e:
            logger.error(f"Telegram RPC error joining folder: {e}")
            raise Exception(f"Telegram error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error joining folder: {e}", exc_info=True)
            raise e
