import asyncio
from telethon import TelegramClient, functions, types, connection
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetDialogFiltersRequest, GetForumTopicsRequest
import os
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, ADMIN_SESSION_STRING, TELEGRAM_PROXY

# CONFIGURATION
# We now use values from config.py directly

async def get_topics_for_entity(client, entity):
    name = getattr(entity, 'title', None) or f"{getattr(entity, 'first_name', '')} {getattr(entity, 'last_name', '')}".strip() or "Unknown"
    print(f"Scanning: {name} ({entity.id})", flush=True)
    if not getattr(entity, 'forum', False):
         print(f"  -> Skipping (Not a forum)")
         return {}

    topics_map = {}
    try:
        offset_date = 0
        offset_id = 0
        offset_topic = 0
        
        while True:
            # We assume GetForumTopicsRequest is in messages based on previous checks
            result = await client(GetForumTopicsRequest(
                peer=entity,
                offset_date=None,
                offset_id=offset_id,
                offset_topic=offset_topic,
                limit=100
            ))
            
            if not result.topics:
                break
                
            for t in result.topics:
                if isinstance(t, types.ForumTopic):
                    title = t.title
                    # Handle empty titles (General topic sometimes has empty title, implies 'General')
                    if not title and t.id == 1:
                        title = "General"
                    elif not title:
                        title = f"Topic {t.id}"
                    topics_map[title] = t.id
            
            if len(result.topics) < 100:
                break
                
            # Naive pagination break for safety against loops, usually 100 is enough for ads
            break 
            
    except Exception as e:
        print(f"  -> Error fetching topics: {e}")
    
    return topics_map

async def main():
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        print("Please check config.py for API credentials.")
        return

    if ADMIN_SESSION_STRING:
        session = StringSession(ADMIN_SESSION_STRING)
    else:
        session = 'admin_scanner_session'

    # Use a unique session name to avoid AuthKeyDuplicatedError
    # But only if using file based session. StringSession should be fine if not reused concurrently.
    session_display = str(session)[:20] if not isinstance(session, str) else session[:20]
    print(f"🔍 DEBUG: Attempting to connect using session: {session_display}...", flush=True)
    if TELEGRAM_PROXY:
        print(f"🔍 DEBUG: Using Proxy: {TELEGRAM_PROXY}", flush=True)
    
    client_kwargs = {'proxy': TELEGRAM_PROXY}
    if TELEGRAM_PROXY and len(TELEGRAM_PROXY) == 3 and isinstance(TELEGRAM_PROXY[2], str):
        client_kwargs['connection'] = connection.ConnectionTcpMTProxyRandomizedIntermediate

    client = TelegramClient(session, TELEGRAM_API_ID, TELEGRAM_API_HASH, **client_kwargs)
    
    async def try_start():
        try:
            print("🔍 DEBUG: Calling client.connect()...", flush=True)
            await asyncio.wait_for(client.connect(), timeout=30)
            print("🔍 DEBUG: Connected. Checking authorization...", flush=True)
            if await client.is_user_authorized():
                print("Logged in successfully.", flush=True)
                return True
            else:
                print("❌ ERROR: User is NOT authorized. The session might be invalid.", flush=True)
                return False
        except Exception as e:
            print(f"❌ DEBUG: Connection/Auth error: {type(e).__name__}: {e}", flush=True)
            if "AuthKeyDuplicatedError" in str(e):
                return False
            else:
                return None

    auth_success = await try_start()
    if auth_success is False:
        # Fallback to fresh session
        client = TelegramClient('temp_scanner_session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
        if await try_start() is None:
            return
    elif auth_success is None:
        return

    # 1. Fetch Folders
    print("🔍 DEBUG: Fetching dialog filters...", flush=True)
    filters_result = await client(GetDialogFiltersRequest())
    print(f"🔍 DEBUG: Found {len(getattr(filters_result, 'filters', []))} filters.", flush=True)
    print("\nSelect a method:", flush=True)
    print("0. Enter Manual Chat ID/Username", flush=True)
    
    # filters_result is messages.DialogFilters, list is in .filters
    filters = getattr(filters_result, 'filters', [])
    if not filters:
         # It might be just a list if using a different request or layer, but usually it's an object.
         # If iterate failed, it means it's the object.
         pass

    folder_map = {}
    for i, f in enumerate(filters):
         # Filters can be DialogFilter or DialogFilterChatlist
         if hasattr(f, 'title'):
             # Title is often TextWithEntities
             title = f.title.text if hasattr(f.title, 'text') else str(f.title)
             print(f"{i+1}. Folder: {title}")
             folder_map[i+1] = f

    choice = input("\nEnter choice (0-N): ").strip()
    
    target_entities = []

    if choice == '0':
        target = input("Enter Username or ID: ").strip()
        try:
            if target.startswith('-100'):
                target_entities.append(await client.get_entity(int(target)))
            elif target.lstrip('-').isdigit():
                 target_entities.append(await client.get_entity(int(target)))
            else:
                target_entities.append(await client.get_entity(target))
        except Exception as e:
            print(f"Could not find entity: {e}")
            return
    elif choice.isdigit() and int(choice) in folder_map:
        f = folder_map[int(choice)]
        print(f"Fetching chats from folder '{f.title}'...")
        # include_peers contains InputPeers. We need to resolve them to Entities.
        # We can pass the list of input peers to get_entity/get_input_entity?
        # get_entity supports lists.
        try:
            # f.include_peers is a list of InputPeer
            # We filter out InputPeerEmpty
            valid_peers = [p for p in f.include_peers if not isinstance(p, types.InputPeerEmpty)]
            if valid_peers:
                 # get_entity might need real IDs or usernames. generic InputPeer might work.
                 # Let's try iterating and fetching.
                 for p in valid_peers:
                     try:
                         ent = await client.get_entity(p)
                         target_entities.append(ent)
                     except:
                         pass
        except Exception as e:
            print(f"Error resolving folder peers: {e}")
    else:
        print("Invalid choice.")
        return

    print(f"\nProcessing {len(target_entities)} chats...")
    
    full_config = {}

    for entity in target_entities:
        title = getattr(entity, 'title', None) or f"{getattr(entity, 'first_name', '')} {getattr(entity, 'last_name', '')}".strip() or "Unknown"
        
        # Determine if it's a channel-id compatible integer
        eid = entity.id
        full_id = int(f"-100{eid}")

        if getattr(entity, 'forum', False):
            # Try to ensure we are connected
            if not client.is_connected():
                print(f"  -> Reconnecting...")
                await client.connect()
            
            t_map = await get_topics_for_entity(client, entity)
            if t_map:
                full_config[full_id] = t_map
                print(f"  -> {title} (Forum): Found {len(t_map)} topics.")
            else:
                # Forum but no topics found (maybe just General)
                # We still might want to treat it as a forum with just "General" if possible, 
                # but get_topics_for_entity already handles General (id 1).
                # If it's empty, maybe it's restricted.
                print(f"  -> {title} (Forum): No topics or restricted.")
        else:
            # Simple group/chat
            full_config[full_id] = None
            print(f"  -> {title} (Simple Group): Saved ID.")

    print("\n\n" + "="*40)
    print("COPY THIS INTO config.py GROUPS_CONFIG")
    print("="*40)
    print("GROUPS_CONFIG = {")
    for gid, topics in full_config.items():
        if topics is None:
             print(f"    {gid}: None, # Simple Group")
        else:
            print(f"    {gid}: {{")
            for name, tid in topics.items():
                print(f'        "{name}": {tid},')
            print("    },")
    print("}")
    print("="*40)

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
