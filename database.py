import aiosqlite
import logging

from config import DB_PATH

logger = logging.getLogger('database')

async def init_db():
    logger.info(f"Initializing database at: {DB_PATH}")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                name TEXT PRIMARY KEY,
                status TEXT NOT NULL, -- ACTIVE, PAUSED, STOPPED
                owner_id INTEGER NOT NULL,
                group_name TEXT,
                bot_token TEXT,
                bot_username TEXT,
                bot_id INTEGER,
                session_string TEXT,
                target_post_link TEXT,
                target_topic_keyword TEXT,
                source_chat_id INTEGER,
                source_message_id INTEGER,
                duration_days INTEGER,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                last_run_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Migration: Check if session_string column exists, if not add it
        try:
            await db.execute('SELECT session_string FROM campaigns LIMIT 1')
        except aiosqlite.OperationalError:
            logger.info("Adding session_string column to campaigns table")
            await db.execute('ALTER TABLE campaigns ADD COLUMN session_string TEXT')
            await db.commit()

        # Migration: Check if group_name column exists, if not add it
        try:
            await db.execute('SELECT group_name FROM campaigns LIMIT 1')
        except aiosqlite.OperationalError:
            logger.info("Adding group_name column to campaigns table")
            await db.execute('ALTER TABLE campaigns ADD COLUMN group_name TEXT')
            await db.commit()
            
        await db.commit()
        logger.info("Database initialized successfully")

async def add_campaign(name, status, owner_id, bot_token, bot_username, bot_id, session_string, target_post_link, target_topic_keyword, duration_days, start_time, end_time, source_chat_id=None, source_message_id=None, group_name=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO campaigns (
                name, status, owner_id, bot_token, bot_username, bot_id, 
                session_string, target_post_link, target_topic_keyword, 
                duration_days, start_time, end_time, last_run_at, 
                group_name, source_chat_id, source_message_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
        ''', (
            name, status, owner_id, bot_token, bot_username, bot_id, 
            session_string, target_post_link, target_topic_keyword, 
            duration_days, start_time, end_time, group_name, 
            source_chat_id, source_message_id
        ))
        await db.commit()

async def update_campaign_last_run(name, last_run_at):
    # Ensure last_run_at is a string for consistent storage
    if hasattr(last_run_at, 'isoformat'):
        last_run_at = last_run_at.isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE campaigns SET last_run_at = ? WHERE name = ?', (last_run_at, name))
        await db.commit()

async def update_campaign_status(name, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE campaigns SET status = ? WHERE name = ?', (status, name))
        await db.commit()

async def update_campaign_post(name, target_post_link, source_chat_id, source_message_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE campaigns 
            SET target_post_link = ?, source_chat_id = ?, source_message_id = ? 
            WHERE name = ?
        ''', (target_post_link, source_chat_id, source_message_id, name))
        await db.commit()

async def get_campaign(name):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM campaigns WHERE name = ?', (name,)) as cursor:
            return await cursor.fetchone()

async def get_active_campaigns():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM campaigns WHERE status = "ACTIVE"') as cursor:
            return await cursor.fetchall()

async def get_campaigns_by_group(group_name):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM campaigns WHERE group_name = ?', (group_name,)) as cursor:
            return await cursor.fetchall()

async def delete_campaign(name):
     async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM campaigns WHERE name = ?', (name,))
        await db.commit()

async def get_all_campaigns():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM campaigns ORDER BY group_name ASC, created_at DESC') as cursor:
            return await cursor.fetchall()
