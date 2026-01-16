import asyncio
from telethon import TelegramClient, functions, types, connection, errors
from telethon.sessions import StringSession
from telethon.tl.functions.messages import GetDialogFiltersRequest, GetForumTopicsRequest
import os
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, ADMIN_SESSION_STRING, TELEGRAM_PROXY

# CONFIGURATION
# We now use values from config.py directly

async def get_topics_for_entity_safe(client, entity, semaphore):
    """
    Fetches topics for a single entity with concurrency limits and retry logic.
    """
    async with semaphore:
        name = getattr(entity, 'title', None) or f"{getattr(entity, 'first_name', '')} {getattr(entity, 'last_name', '')}".strip() or "Unknown"
        
        # Helper to get ID consistently
        eid = entity.id
        full_id = int(f"-100{eid}")
        
        # 1. Check if Forum
        if not getattr(entity, 'forum', False):
            print(f"  -> {name}: Simple Group (ID: {full_id})")
            return full_id, None

        print(f"  -> Scanning Forum: {name} ({full_id})...")
        
        topics_map = {}
        retries = 3
        
        for attempt in range(retries):
            try:
                offset_date = 0
                offset_id = 0
                offset_topic = 0
                
                while True:
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
                            if not title and t.id == 1:
                                title = "General"
                            elif not title:
                                title = f"Topic {t.id}"
                            topics_map[title] = t.id
                    
                    if len(result.topics) < 100:
                        break
                    
                    # Pagination update would go here if needed, but for now break safely
                    break 
                
                # Success
                print(f"     -> {name}: Found {len(topics_map)} topics.")
                return full_id, topics_map

            except errors.MsgIdDecreaseRetryError:
                print(f"     ⚠️ {name}: MsgId skew error. Retrying... ({attempt+1}/{retries})")
                await asyncio.sleep(1)
            except errors.FloodWaitError as fwe:
                print(f"     ⚠️ {name}: FloodWait {fwe.seconds}s. Sleeping...")
                await asyncio.sleep(fwe.seconds)
            except Exception as e:
                print(f"     ❌ {name}: Error fetching topics: {e}")
                return full_id, None # Treat as empty/failed
        
        return full_id, None


async def main():
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        print("Please check config.py for API credentials.")
        return

    if ADMIN_SESSION_STRING:
        session = StringSession(ADMIN_SESSION_STRING)
    else:
        session = 'admin_scanner_session'

    session_display = str(session)[:20] if not isinstance(session, str) else session[:20]
    print(f"🔍 DEBUG: Connecting with session: {session_display}...", flush=True)
    
    client_kwargs = {'proxy': TELEGRAM_PROXY}
    if TELEGRAM_PROXY and len(TELEGRAM_PROXY) == 3 and isinstance(TELEGRAM_PROXY[2], str):
        client_kwargs['connection'] = connection.ConnectionTcpMTProxyRandomizedIntermediate

    client = TelegramClient(session, TELEGRAM_API_ID, TELEGRAM_API_HASH, **client_kwargs)
    
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ ERROR: User is NOT authorized.", flush=True)
        return

    # 1. Fetch Folders
    print("🔍 DEBUG: Fetching dialog filters...", flush=True)
    filters_result = await client(GetDialogFiltersRequest())
    
    filters = getattr(filters_result, 'filters', [])
    if not filters:
        print("No folders found.")
    
    folder_map = {}
    print("\nSelect a method:")
    print("0. Enter Manual Chat ID/Username")
    
    for i, f in enumerate(filters):
        if hasattr(f, 'title'):
            title = f.title.text if hasattr(f.title, 'text') else str(f.title)
            print(f"{i+1}. Folder: {title}")
            folder_map[i+1] = f

    choice = input("\nEnter choice (0-N): ").strip()
    
    target_entities = []

    if choice == '0':
        target = input("Enter Username or ID: ").strip()
        try:
             # Just one entity
             target_entities.append(await client.get_entity(target))
        except Exception as e:
            print(f"Could not find entity: {e}")
            return
            
    elif choice.isdigit() and int(choice) in folder_map:
        f = folder_map[int(choice)]
        print(f"Fetching chats from folder '{f.title}'...")
        
        # --- OPTIMIZATION 1: Batch Entity Resolution ---
        valid_peers = [p for p in f.include_peers if not isinstance(p, types.InputPeerEmpty)]
        
        if valid_peers:
            print(f"Resolving {len(valid_peers)} chats in batch... (This is fast now)")
            try:
                # get_entity can take a list!
                resolved = await client.get_entity(valid_peers)
                target_entities.extend(resolved)
            except Exception as e:
                print(f"Batch resolution failed ({e}), falling back to partial...")
                # Fallback: try chunks of 20
                chunk_size = 20
                for i in range(0, len(valid_peers), chunk_size):
                    chunk = valid_peers[i:i + chunk_size]
                    try:
                        resolved = await client.get_entity(chunk)
                        target_entities.extend(resolved)
                    except:
                        pass # Ignore individual chunk failures
    else:
        print("Invalid choice.")
        return

    print(f"\nProcessing {len(target_entities)} chats in PARALLEL...")
    
    # --- OPTIMIZATION 2: Parallel Processing with Semaphore ---
    semaphore = asyncio.Semaphore(15) # Concurrent limit
    tasks = []
    
    for entity in target_entities:
        tasks.append(get_topics_for_entity_safe(client, entity, semaphore))
    
    # Run all tasks
    results = await asyncio.gather(*tasks)
    
    # Organize Results
    full_config = {}
    for gid, topics in results:
        full_config[gid] = topics

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
