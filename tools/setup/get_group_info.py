import asyncio
import argparse
import sys
import re
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
            # print(f"  -> {name}: Simple Group (ID: {full_id})")
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
                # print(f"     -> {name}: Found {len(topics_map)} topics.")
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
    parser = argparse.ArgumentParser(description="Fetch Telegram Group/Topic Info")
    parser.add_argument("--folder", type=str, help="Name of the folder to scan (e.g. 'Marketplaces')")
    parser.add_argument("--write", action="store_true", help="Write changes to config.py automatically")
    args = parser.parse_args()

    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        print("Please check config.py for API credentials.")
        return

    if ADMIN_SESSION_STRING:
        session = StringSession(ADMIN_SESSION_STRING)
    else:
        session = 'admin_scanner_session'

    # session_display = str(session)[:20] if not isinstance(session, str) else session[:20]
    # print(f"🔍 DEBUG: Connecting with session: {session_display}...", flush=True)
    
    client_kwargs = {'proxy': TELEGRAM_PROXY}
    if TELEGRAM_PROXY and len(TELEGRAM_PROXY) == 3 and isinstance(TELEGRAM_PROXY[2], str):
        client_kwargs['connection'] = connection.ConnectionTcpMTProxyRandomizedIntermediate

    # If running non-interactively, suppress some logs or connect silently
    # But Telethon needs to connect.
    client = TelegramClient(session, TELEGRAM_API_ID, TELEGRAM_API_HASH, **client_kwargs)
    
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ ERROR: User is NOT authorized.", flush=True)
        return

    # 1. Fetch Folders
    # print("🔍 DEBUG: Fetching dialog filters...", flush=True)
    filters_result = await client(GetDialogFiltersRequest())
    
    filters = getattr(filters_result, 'filters', [])
    folder_map = {} # Name -> Filter
    
    for f in filters:
        if hasattr(f, 'title'):
            title = f.title.text if hasattr(f.title, 'text') else str(f.title)
            folder_map[title] = f

    target_filter = None
    
    if args.folder:
        # CLI Mode
        if args.folder in folder_map:
            target_filter = folder_map[args.folder]
        else:
            print(f"Error: Folder '{args.folder}' not found. Available: {list(folder_map.keys())}")
            await client.disconnect()
            sys.exit(1)
    else:
        # Interactive Mode
        print("\nAvailable Folders:")
        folders_list = list(folder_map.keys())
        for i, name in enumerate(folders_list):
            print(f"{i+1}. {name}")
        
        print("0. Manual Chat ID")
        choice = input("\nEnter choice: ").strip()
        
        if choice.isdigit() and int(choice) > 0 and int(choice) <= len(folders_list):
             target_filter = folder_map[folders_list[int(choice)-1]]
        elif choice != '0':
            print("Invalid choice")
            await client.disconnect()
            return

    target_entities = []

    if target_filter:
        print(f"Fetching chats from folder '{getattr(target_filter, 'title', 'Unknown')}'...")
        valid_peers = [p for p in target_filter.include_peers if not isinstance(p, types.InputPeerEmpty)]
        
        if valid_peers:
            try:
                # Batch Resolve
                resolved = await client.get_entity(valid_peers)
                target_entities.extend(resolved)
            except Exception as e:
                # Fallback Chunking
                chunk_size = 20
                for i in range(0, len(valid_peers), chunk_size):
                    chunk = valid_peers[i:i + chunk_size]
                    try:
                        resolved = await client.get_entity(chunk)
                        target_entities.extend(resolved)
                    except:
                        pass
    else:
        # Manual Mode (only interactive usually, or need args for target)
        target = input("Enter Username or ID: ").strip() if not args.folder else None
        if target:
            try:
                target_entities.append(await client.get_entity(target))
            except Exception as e:
                print(f"Error: {e}")
                return

    print(f"Processing {len(target_entities)} chats...")
    
    semaphore = asyncio.Semaphore(15) 
    tasks = []
    
    for entity in target_entities:
        tasks.append(get_topics_for_entity_safe(client, entity, semaphore))
    
    results = await asyncio.gather(*tasks)
    
    full_config = {}
    for gid, topics in results:
        full_config[gid] = topics

    await client.disconnect()

    # Generate Output string
    output_lines = []
    output_lines.append("GROUPS_CONFIG = {")
    for gid, topics in full_config.items():
        if topics is None:
             output_lines.append(f"    {gid}: None, # Simple Group")
        else:
            output_lines.append(f"    {gid}: {{")
            for name, tid in topics.items():
                output_lines.append(f'        "{name}": {tid},')
            output_lines.append("    },")
    output_lines.append("}")
    
    config_content = "\n".join(output_lines)

    if args.write:
        # Auto-write to config.py
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.py')
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            # Regex to replace existing GROUPS_CONFIG = { ... }
            # Must match 'GROUPS_CONFIG = {' until the matching closing brace.
            # Python dictionaries with nested braces make regex hard.
            # Assuming standard indentation and single block.
            
            # Simpler approach: Find start, find a line that starts with '}' at root level (after start).
            
            # Actually, let's use a simpler marker if possible or just precise regex
            # GROUPS_CONFIG = \{.*?^\} (multiline, dotall)
            
            new_content = re.sub(
                r'GROUPS_CONFIG = \{.*?\n\}', 
                config_content, 
                current_content, 
                flags=re.DOTALL | re.MULTILINE
            )
            
            # If regex didn't change anything (maybe format mismatch), try appending or warn
            if new_content == current_content:
                print("Warning: Could not auto-replace GROUPS_CONFIG. Check formatting.")
            else:
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Successfully updated {config_path}")
                
        except Exception as e:
            print(f"Error writing to config.py: {e}")
            sys.exit(1)

    else:
        # Print to stdout
        print("\n" + "="*40)
        print("COPY THIS INTO config.py GROUPS_CONFIG")
        print("="*40)
        print(config_content)
        print("="*40)

if __name__ == '__main__':
    asyncio.run(main())
