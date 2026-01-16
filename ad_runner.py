import asyncio
import random
import aiohttp
import json
from config import (
    GROUPS_CONFIG, ALIASES, OTHER, 
    AD_FORWARD_DELAY_MIN, AD_FORWARD_DELAY_MAX, 
    AD_SKIP_DELAY_MIN, AD_SKIP_DELAY_MAX,
    CAMPAIGN_STAGGER_DELAY, LOG_STRATEGY,
    STARTUP_JITTER_MAX
)
from database import get_active_campaigns, update_campaign_status, update_campaign_last_run
import datetime

from utils.logger import bot_logger as logger

class AdRunner:
    def __init__(self, telegram_manager, discord_client=None):
        self.running = False
        self._task = None
        self.tg_manager = telegram_manager
        self.discord_client = discord_client
        self.http_session = None # For log bots

    async def get_http_session(self):
        if self.http_session is None or self.http_session.closed:
            self.http_session = aiohttp.ClientSession()
        return self.http_session

    async def send_rich_log(self, campaign_group, account_name, target_group_name, target_link, ad_preview):
        """
        Sends a rich log message to the configured Log Bot for the campaign group.
        """
        # 1. Determine Strategy
        strategy = LOG_STRATEGY.get(campaign_group, LOG_STRATEGY.get('DEFAULT'))
        if not strategy or strategy['channel_id'] == 'REPLACE_WITH_CHANNEL_ID':
            return # Logging disabled or not configured

        bot_token = strategy['token']
        channel_id = strategy['channel_id']

        # Support multiple channel IDs if provided as a list
        target_ids = channel_id if isinstance(channel_id, (list, tuple)) else [channel_id]

        # 2. Construct Payload
        text = (
            f"✅ <b>Successfully forwarded to:</b> {target_group_name}\n"
            f"<b>Account:</b> {account_name}\n\n"
            f"<i>{ad_preview[:100]}...</i>" # Preview of the ad content
        )

        payload = {
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": {
                "inline_keyboard": [[
                    {"text": "VIEW MESSAGE", "url": target_link}
                ]]
            }
        }

        # 3. Send Requests
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        try:
            session = await self.get_http_session()
            for tid in target_ids:
                if tid == 'REPLACE_WITH_CHANNEL_ID' or not tid:
                    continue
                
                try:
                    logger.info(f"📤 Sending Rich Log for group '{campaign_group}' to {tid}")
                    current_payload = payload.copy()
                    current_payload["chat_id"] = tid
                    
                    async with session.post(url, json=current_payload) as resp:
                        if resp.status != 200:
                            err_text = await resp.text()
                            logger.warning(f"❌ Failed to send rich log to {tid}: {resp.status} - {err_text}")
                        else:
                            logger.info(f"✅ Rich Log sent successfully to {tid}")
                except Exception as inner_e:
                    logger.error(f"❌ Error sending rich log to {tid}: {inner_e}")
                    
        except Exception as e:
            logger.error(f"❌ Error in send_rich_log loop: {e}")

    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self.loop())
        logger.info("AdRunner started.")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("AdRunner stopped.")

    async def loop(self):
        first_run = True
        while self.running:
            try:
                if first_run:
                    jitter = random.randint(0, STARTUP_JITTER_MAX)
                    logger.info(f"Applying startup jitter: Waiting {jitter}s before first run...")
                    await asyncio.sleep(jitter)
                    first_run = False

                logger.info("--- Starting Campaign Check Loop ---")
                await self.process_campaigns()
                logger.info("--- Finished Campaign Check Loop ---")
            except Exception as e:
                logger.error(f"Error in AdRunner loop: {e}", exc_info=True)
            
            logger.info("Sleeping for 60s...")
            await asyncio.sleep(60) # Check every minute

    async def process_campaigns(self):
        campaigns = await get_active_campaigns()
        now = datetime.datetime.now()

        logger.info(f"Found {len(campaigns)} active campaigns.")

        # Group campaigns
        groups = {}
        standalone_campaigns = []

        for row in campaigns:
            group_name = row['group_name']
            if group_name and group_name.strip():
                if group_name not in groups:
                    groups[group_name] = []
                groups[group_name].append(row)
            else:
                standalone_campaigns.append(row)

        tasks = []

        # Process groups concurrently
        for group_name, members in groups.items():
            tasks.append(self.process_group(group_name, members, now))

        # Process standalone campaigns concurrently
        for row in standalone_campaigns:
            tasks.append(self.process_standalone(row, now))


        if tasks:
            logger.info(f"Executing {len(tasks)} concurrent campaign tasks with blinker stagger...")
            # Stagger the start of each task to avoid instant burst
            for t in tasks:
                 # asyncio.gather expects awaitables, but we actually called the function above which returns a coro.
                 # Actually, line 66 and 70 append coroutines. 
                 # We can't stagger them inside gather easily without wrapping them.
                 # Instead, let's just launch them as independent tasks if we want stagger? 
                 # OR, better: We can wrap the coroutines in a small stagger function.
                 pass

            # Stagger wrapper
            async def staggered_run(coro, delay):
                await asyncio.sleep(delay)
                await coro

            staggered_tasks = []
            for i, task_coro in enumerate(tasks):
                # Randomized delay for staggering
                # Base is i * CAMPAIGN_STAGGER_DELAY
                # Add/Subtract random jitter
                base_delay = i * CAMPAIGN_STAGGER_DELAY
                jittered_delay = base_delay + random.uniform(0, CAMPAIGN_STAGGER_DELAY)
                staggered_tasks.append(staggered_run(task_coro, jittered_delay))

            await asyncio.gather(*staggered_tasks)

    async def process_group(self, group_name, members, now):
        logger.info(f"Processing Group: {group_name} ({len(members)} accounts)")
        
        # Strict 62-minute interval (3720 seconds)
        STRICT_INTERVAL = 3720
        
        # Group interval = 3720 / N
        group_interval = STRICT_INTERVAL / len(members)
        
        # Sort members by last_run_at to see who is "next"
        members_sorted = sorted(members, key=lambda m: self._parse_date(m['last_run_at']))
        
        # The one who ran longest ago is the candidate
        candidate = members_sorted[0]
        last_run_candidate = self._parse_date(candidate['last_run_at'])
        time_since_last_run = (now - last_run_candidate).total_seconds()
        
        # Check group spacing: Who ran most recently in this group?
        members_last_runs = [self._parse_date(m['last_run_at']) for m in members if self._parse_date(m['last_run_at']) != datetime.datetime.min]
        if members_last_runs:
            most_recent_run = max(members_last_runs)
            time_since_any_run = (now - most_recent_run).total_seconds()
        else:
            time_since_any_run = float('inf')

        logger.info(f"Group {group_name}: Candidate {candidate['name']} last ran {time_since_last_run:.1f}s ago. Member gap: {time_since_any_run:.1f}s (Required: {group_interval:.1f}s)")

        if time_since_last_run >= STRICT_INTERVAL and time_since_any_run >= group_interval:
            logger.info(f"<blue>Group {group_name}: Running ad for {candidate['name']}...</blue>")
            await self.run_and_update(candidate, now)
        else:
            wait_time = max(STRICT_INTERVAL - time_since_last_run, group_interval - time_since_any_run)
            logger.info(f"Group {group_name}: No account ready. Next run in approx {wait_time:.1f}s")

    async def process_standalone(self, row, now):
        STRICT_INTERVAL = 3720
        c_name = row['name']
        last_run = row['last_run_at']
        
        # Check duration
        end_time = row['end_time']
        if isinstance(end_time, str):
            try:
                end_time_dt = datetime.datetime.fromisoformat(end_time)
            except:
                try:
                    end_time_dt = datetime.datetime.strptime(end_time.split('.')[0], "%Y-%m-%d %H:%M:%S")
                except:
                    end_time_dt = None
        elif isinstance(end_time, datetime.datetime):
            end_time_dt = end_time
        else:
            end_time_dt = None
        
        if end_time_dt and now > end_time_dt:
            logger.info(f"Campaign {c_name} expired. Stopping.")
            await update_campaign_status(c_name, 'STOPPED')
            return

        last_run_dt = self._parse_date(last_run)
        time_diff = (now - last_run_dt).total_seconds()
        logger.info(f"Standalone {c_name}: Last run {time_diff:.1f}s ago (Required: {STRICT_INTERVAL}s)")

        if time_diff >= STRICT_INTERVAL:
            logger.info(f"<blue>Running standalone ad for {c_name}...</blue>")
            await self.run_and_update(row, now)
        else:
            logger.info(f"Standalone {c_name}: Waiting {STRICT_INTERVAL - time_diff:.1f}s")

    def _parse_date(self, val):
        if val is None or (isinstance(val, int) and val == 0):
            return datetime.datetime.min
        if isinstance(val, datetime.datetime):
            return val
        if isinstance(val, str):
            try:
                return datetime.datetime.fromisoformat(val)
            except:
                try:
                    return datetime.datetime.strptime(val.split('.')[0], "%Y-%m-%d %H:%M:%S")
                except:
                    return datetime.datetime.min
        return datetime.datetime.min

    async def run_and_update(self, campaign, now):
        await self.run_ad(campaign)
        await update_campaign_last_run(campaign['name'], now)

    async def notify_owner_errors(self, campaign, error_reports):
        if not self.discord_client or not error_reports:
            return
        
        try:
            owner_id = campaign['owner_id']
            user = await self.discord_client.fetch_user(owner_id)
            if user:
                report_text = "\n".join([f"• Group `{gid}`: {msg}" for gid, msg in error_reports])
                await user.send(f"⚠️ **Ad Runner Summary Error Report**\nCampaign: `{campaign['name']}`\n\n{report_text}")
        except Exception as e:
            logger.error(f"Failed to send error summary DM: {e}")

    async def run_ad(self, campaign):
        source_chat_id = campaign['source_chat_id']
        source_msg_id = campaign['source_message_id']
        topic_keyword = campaign['target_topic_keyword']
        session_string = campaign['session_string'] # Get session string
        campaign_group = campaign['group_name'] # Get group (e.g. 'Eyecon', 'Khan')
        
        if not source_chat_id or not source_msg_id:
            logger.error(f"Campaign {campaign['name']} missing source info.")
            return

        # Normalize the topic keyword
        normalized_topic = ALIASES.get(topic_keyword.lower(), topic_keyword)
        
        logger.info(f"Source: Chat={source_chat_id}, Msg={source_msg_id}, TopicKeyword='{topic_keyword}' -> Normalized='{normalized_topic}'")
        
        # Iterate configured groups - SHUFFLED for each run to avoid overlap
        target_groups = list(GROUPS_CONFIG.items())
        random.shuffle(target_groups)
        
        logger.info(f"Checking {len(target_groups)} groups for potential forwarding (Randomized Order)...")
        
        failed_groups = []
        
        for group_id, topic_ids in target_groups:
            target_topic_id = None
            should_send = False
            used_topic_name = "None (Simple Group)"
            
            # GROUPS_CONFIG = { group_id: { "TopicName": topic_id } } OR { group_id: None }
            if topic_ids is None:
                # Simple Group: Always send
                should_send = True
                logger.info(f"Group {group_id} is a simple group. Forwarding directly.")
            elif isinstance(topic_ids, dict):
                # Forum: Match topic or fallback to OTHER
                # 1. Try Specific Topic
                if normalized_topic in topic_ids:
                     target_topic_id = topic_ids[normalized_topic]
                     used_topic_name = normalized_topic
                     should_send = True
                
                # 2. Fallback to OTHER if not found
                if not should_send:
                    if OTHER in topic_ids:
                        target_topic_id = topic_ids[OTHER]
                        used_topic_name = OTHER
                        should_send = True
                        logger.info(f"Group {group_id}: Topic '{normalized_topic}' not found. Falling back to '{OTHER}' (ID: {target_topic_id})")

            if should_send:
                    logger.info(f"Match found! Group {group_id} -> '{used_topic_name}' (ID: {target_topic_id})")

                    try:
                        success, message_link = await self.tg_manager.forward_message(
                            target_chat_id=group_id,
                            target_topic_id=target_topic_id,
                            source_chat_id=source_chat_id,
                            source_msg_id=source_msg_id,
                            session_string=session_string
                        )

                        if success:
                            logger.info(f"Forwarded ad {campaign['name']} to {group_id} topic {target_topic_id}")
                            
                            # --- RICH LOGGING ---
                            # Fire and forget logging
                            if message_link:
                                # Get a preview text (we don't have the message text easily here without fetching, 
                                # but we can just say 'New Ad' or pass the campaign name)
                                asyncio.create_task(
                                    self.send_rich_log(
                                        campaign_group=campaign_group,
                                        account_name=campaign['name'],
                                        target_group_name=str(group_id), # We could try to resolve name if needed
                                        target_link=message_link,
                                        ad_preview=f"Ad Campaign: {campaign['name']}"
                                    )
                                )
                            # --------------------

                            # Randomized delay config
                            sleep_time = random.randint(AD_FORWARD_DELAY_MIN, AD_FORWARD_DELAY_MAX)
                            logger.info(f"Waiting {sleep_time} seconds before next group...")
                            await asyncio.sleep(sleep_time)
                        else:
                             # Wait a small amount of time to avoid busy loops even on skips, or just continue
                             # Let's add a very small delay to be safe and avoid CPU spikes if many fail fast
                             # Safety Update: Randomized delay for skips/failures to prevent rapid looping
                             skip_delay = random.randint(AD_SKIP_DELAY_MIN, AD_SKIP_DELAY_MAX)
                             logger.info(f"Skipped/Failed. Waiting {skip_delay}s safety delay...")
                             await asyncio.sleep(skip_delay)
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Failed to forward to group {group_id}: {error_msg}")
                        
                        # Categorize errors to avoid notifying for known skips/permanent bans if they are handled in manager
                        # If forward_message returns None instead of raising, we wouldn't even be here.
                        # But it raises for unhandled or explicitly raised errors.
                        # Since I updated telegram_manager to RETURN on bans, this catch might not catch some skips.
                        # However, for unexpected ones, we collect them.
                        failed_groups.append((group_id, error_msg))

        # Send aggregated notification
        if failed_groups:
            await self.notify_owner_errors(campaign, failed_groups)

        logger.info(f"--- Finished campaign run for {campaign['name']} ---")
