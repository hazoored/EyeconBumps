import sys
from unittest.mock import MagicMock

# PATCH: Mock audioop for Python 3.13 if environment prevents loading the C extension (audioop-lts).
# This MUST happen before anything imports discord.
try:
    import audioop
except ImportError:
    sys.modules["audioop"] = MagicMock()

import discord
from discord import app_commands
import os
import asyncio
import datetime
import random
from config import DISCORD_TOKEN, DISCORD_GUILD_ID, TELEGRAM_API_ID, TELEGRAM_API_HASH
from telethon import TelegramClient, errors
from telethon.sessions import StringSession

from database import init_db, add_campaign, delete_campaign, update_campaign_status, get_campaign, update_campaign_post, get_all_campaigns, update_campaign_last_run, get_campaigns_by_group
from telegram_manager import TelegramManager
from ad_runner import AdRunner

from utils.logger import bot_logger as logger

# Discord Intents
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Telegram Manager Instance
tg_manager = TelegramManager()
# Ad Runner Instance (passed tg_manager and client)
ad_runner = AdRunner(tg_manager, client)

# Stores Telethon clients for session generation: {user_id: {'client': client, 'phone': phone, 'hash': hash}}
pending_auths = {}

@client.event
async def on_ready():
    # Set presence immediately
    await client.change_presence(
        status=discord.Status.dnd,
        activity=discord.Game(name="#1 ADs Service ● User Account Mode")
    )
    
    await init_db()
    
    # Sync commands
    if DISCORD_GUILD_ID:
        guild = discord.Object(id=DISCORD_GUILD_ID)
        tree.copy_global_to(guild=guild)
        await tree.sync(guild=guild)
        logger.info(f'Slash commands synced to guild ID: {DISCORD_GUILD_ID}')
    else:
        await tree.sync()
        logger.info('Slash commands synced globally')

    await tg_manager.start()
    await ad_runner.start()

    logger.info(f'Logged in as {client.user} (ID: {client.user.id})')
    logger.info('AdRunner started and slash commands synced')

@tree.command(name="ping", description="Check if the bot is alive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latency: {round(client.latency * 1000)}ms")

# --- UI Components ---

class CampaignSetupModal(discord.ui.Modal, title='Create New Ad Campaign'):
    campaign_name = discord.ui.TextInput(label='Campaign Name (Unique)', placeholder='Unique ID', min_length=3, max_length=50)
    session_id = discord.ui.TextInput(label='Telegram Session ID', placeholder='StringSession...', min_length=10, max_length=1000)
    post_link = discord.ui.TextInput(label='Telegram Post Link', placeholder='https://t.me/c/1234/567 or t.me/user/123', min_length=10, max_length=200)
    topic_keyword = discord.ui.TextInput(label='Target Topic Name', placeholder='e.g. Instagram', min_length=1, max_length=50)

    def __init__(self, duration: int, group_name: str = None):
        super().__init__()
        self.duration_val = duration
        self.group_name_val = group_name

    async def on_submit(self, interaction: discord.Interaction):
        if await get_campaign(self.campaign_name.value):
            await interaction.response.send_message(f"Campaign '{self.campaign_name.value}' already exists!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # Validate Link
        try:
            source_chat_id, source_message_id = await tg_manager.get_message_from_link(self.post_link.value, session_string=self.session_id.value)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to resolve link: {e}\nEnsure the link is correct and the Session ID has access to it.", ephemeral=True)
            return

        # Calculate times
        start_time = datetime.datetime.now()
        duration_days = self.duration_val
        end_time = start_time + datetime.timedelta(days=duration_days)

        # Save campaign
        await add_campaign(
            name=self.campaign_name.value,
            status='ACTIVE',
            owner_id=interaction.user.id,
            bot_token='', # No longer used
            bot_username='', # No longer used
            bot_id=0, # No longer used
            session_string=self.session_id.value,
            target_post_link=self.post_link.value,
            target_topic_keyword=self.topic_keyword.value,
            duration_days=duration_days,
            start_time=start_time,
            end_time=end_time,
            source_chat_id=source_chat_id,
            source_message_id=source_message_id,
            group_name=self.group_name_val
        )

        await interaction.followup.send(
            f"✅ Campaign **{self.campaign_name.value}** Created & Active!\n"
            f"**Topic**: {self.topic_keyword.value}\n"
            f"**Source**: {self.post_link.value}\n"
            f"**Method**: Via Provided Session ID",
            ephemeral=True
        )


    @tree.command(name="updategroups", description="Auto-fetch Telegram Groups, update Config, and Push to GitHub.")
    @app_commands.describe(folder="The Telegram Folder name to scan (Default: 'Marketplaces')")
    async def updategroups(self, interaction: discord.Interaction, folder: str = "Marketplaces"):
        # Check permissions (Owner only)
        # Assuming permissions are handled by role or generic check, but for safety adding ID check
        if interaction.user.id != 6926297956 and interaction.user.id != int(os.getenv('DISCORD_OWNER_ID', 0)):
             if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
                return

        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send(f"🔄 **Updating Groups...**\nScanning folder: `{folder}`\n_This may take a few seconds..._")

        try:
            # 1. Run the Python Script
            script_path = "tools/setup/get_group_info.py"
            # Use sys.executable to ensure we use the same python env
            cmd = [sys.executable, script_path, "--folder", folder, "--write"]
            
            logger.info(f"Running command: {cmd}")
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                err_msg = stderr.decode().strip() or stdout.decode().strip()
                await interaction.followup.send(f"❌ **Script Failed**\n```\n{err_msg[-1900:]}\n```")
                return

            await interaction.followup.send("✅ **Config Updated Locally.**\nPushing to GitHub...")

            # 2. Git Push
            push_cmd = "git add config.py && git commit -m 'Config: Auto-Update Groups via Discord' && git push origin main"
            
            proc_git = await asyncio.create_subprocess_shell(
                push_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_git, stderr_git = await proc_git.communicate()

            if proc_git.returncode != 0:
                err_git = stderr_git.decode().strip()
                if "nothing to commit" in stdout_git.decode():
                     await interaction.followup.send("✅ **Already Up-to-Date!** (No changes detected).")
                else:
                     await interaction.followup.send(f"⚠️ **Git Push Failed**\n```\n{err_git[-1900:]}\n```")
            else:
                await interaction.followup.send("🚀 **Success!**\nGroups updated and pushed to GitHub.\n*Restart the server to apply changes.*")

        except Exception as e:
            logger.error(f"Update Groups Error: {e}")
            await interaction.followup.send(f"❌ **Internal Error**: {str(e)}")

@tree.command(name="createad", description="Start a new ad campaign")
@app_commands.describe(
    duration="Duration of the campaign in days (e.g. 7)",
    group_name="Optional: Unique Group ID for account interleaving"
)
async def create_ad(interaction: discord.Interaction, duration: int, group_name: str = None):
    await interaction.response.send_modal(CampaignSetupModal(duration=duration, group_name=group_name))

@tree.command(name="stopad", description="Stop an ad campaign")
@app_commands.describe(campaign_name="The name of the campaign")
async def stop_ad(interaction: discord.Interaction, campaign_name: str):
    await update_campaign_status(campaign_name, 'PAUSED')
    await interaction.response.send_message(f"Campaign {campaign_name} paused.", ephemeral=True)

@tree.command(name="deletead", description="Delete an ad campaign permanently")
@app_commands.describe(campaign_name="The name of the campaign")
async def delete_ad(interaction: discord.Interaction, campaign_name: str):
    row = await get_campaign(campaign_name)
    if not row:
        await interaction.response.send_message("Campaign not found.", ephemeral=True)
        return
        
    await delete_campaign(campaign_name)
    await interaction.response.send_message(f"Ad campaign {campaign_name} deleted.", ephemeral=True)

@tree.command(name="blitz", description="⚡ FORCE RUN an ad campaign immediately (Bypasses Timer)")
@app_commands.describe(campaign_name="The name of the campaign to blitz")
async def blitz_ad(interaction: discord.Interaction, campaign_name: str):
    # 1. Fetch Campaign
    row = await get_campaign(campaign_name)
    if not row:
        await interaction.response.send_message(f"Campaign '{campaign_name}' not found!", ephemeral=True)
        return

    # Check validation
    if row['status'] != 'ACTIVE':
         await interaction.response.send_message(f"Campaign '{campaign_name}' is not ACTIVE (Status: {row['status']}). Enable it first.", ephemeral=True)
         return

    await interaction.response.defer(ephemeral=False) # Public Blitz!
    
    try:
        # 2. Run Ad immediately
        # We need to manually trigger the logic.
        # Check if ad_runner is available
        if ad_runner:
            await interaction.followup.send(f"⚡ **BLITZ INITIATED** for `{campaign_name}`! Sending to all groups now...")
            
            # Run the ad logic directly
            await ad_runner.run_ad(row)
            
            # Update last run to now so it doesn't run again immediately by the automatic loop
            await update_campaign_last_run(campaign_name, datetime.datetime.now())
            
            await interaction.followup.send(f"✅ **BLITZ COMPLETE** for `{campaign_name}`.")
        else:
            await interaction.followup.send("❌ AdRunner service is not initialized.", ephemeral=True)
            
    except Exception as e:
        await interaction.followup.send(f"❌ Blitz Failed: {e}", ephemeral=True)

@tree.command(name="changead", description="Change the post link for one, a GROUP, or ALL active campaigns")
@app_commands.describe(
    new_post_link="The new Telegram post link",
    campaign_name="Optional: Specific campaign to update",
    group_name="Optional: Update ALL campaigns in this specific group"
)
async def change_ad(interaction: discord.Interaction, new_post_link: str, campaign_name: str = None, group_name: str = None):
    await interaction.response.defer(ephemeral=True)

    target_campaigns = []
    
    if campaign_name:
        # 1. Specific Campaign
        row = await get_campaign(campaign_name)
        if not row:
            await interaction.followup.send(f"❌ Campaign '{campaign_name}' not found!", ephemeral=True)
            return
        target_campaigns = [row]
    elif group_name:
        # 2. Specific Group
        target_campaigns = await get_campaigns_by_group(group_name)
        if not target_campaigns:
            await interaction.followup.send(f"❌ No campaigns found in group '{group_name}'.", ephemeral=True)
            return
    else:
        # 3. ALL Active
        from database import get_active_campaigns
        target_campaigns = await get_active_campaigns()
        if not target_campaigns:
            await interaction.followup.send("❌ No active campaigns found to update.", ephemeral=True)
            return

    # Process Updates
    success_count = 0
    fail_reports = []
    
    for row in target_campaigns:
        c_name = row['name']
        try:
            session_id = row['session_string']
            source_chat_id, source_message_id = await tg_manager.get_message_from_link(new_post_link, session_string=session_id)
            await update_campaign_post(c_name, new_post_link, source_chat_id, source_message_id)
            success_count += 1
        except Exception as e:
            fail_reports.append(f"• `{c_name}`: {e}")

    # Summary
    if campaign_name and success_count == 1:
        await interaction.followup.send(f"✅ Campaign **{campaign_name}** post updated!", ephemeral=True)
    else:
        scope = f"group `{group_name}`" if group_name else "all active campaigns"
        report = f"🔄 **Update Summary ({scope})**\nSuccessfully updated **{success_count}/{len(target_campaigns)}** campaigns."
        if fail_reports:
            report += "\n\n**Failures:**\n" + "\n".join(fail_reports)
        await interaction.followup.send(report, ephemeral=True)


# --- Session String Generator Components ---

class PhoneModal(discord.ui.Modal, title="Telegram Session: Phone Number"):
    phone = discord.ui.TextInput(label="Phone Number", placeholder="+1234567890", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        phone_val = self.phone.value.strip()
        
        try:
            client_gen = TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH)
            await client_gen.connect()
            
            # Send code request
            code_request = await client_gen.send_code_request(phone_val)
            
            # Store in pending auths
            pending_auths[interaction.user.id] = {
                'client': client_gen,
                'phone': phone_val,
                'phone_code_hash': code_request.phone_code_hash
            }
            
            view = OTPView()
            await interaction.followup.send("📲 A code has been sent to your Telegram. Please click the button below to enter it.", view=view, ephemeral=True)
            
        except Exception as e:
            logging.error(f"Error in PhoneModal: {e}")
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

class OTPModal(discord.ui.Modal, title="Telegram Session: Enter OTP"):
    otp = discord.ui.TextInput(label="OTP Code", placeholder="12345", min_length=5, max_length=6, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        
        if user_id not in pending_auths:
            await interaction.followup.send("❌ Session expired or not found. Please restart the process.", ephemeral=True)
            return
            
        auth_data = pending_auths[user_id]
        client_gen = auth_data['client']
        phone = auth_data['phone']
        phone_code_hash = auth_data['phone_code_hash']
        otp_val = self.otp.value.strip()

        try:
            await client_gen.sign_in(phone, otp_val, phone_code_hash=phone_code_hash)
            
            # Success!
            session_str = client_gen.session.save()
            await client_gen.disconnect()
            del pending_auths[user_id]
            
            await interaction.followup.send(f"✅ **Login Successful!**\n\nYour session string is:\n```\n{session_str}\n```\n\n**Keep this string private!** It gives full access to your account.", ephemeral=True)
            
        except errors.SessionPasswordNeededError:
            # 2FA required
            view = PasswordView()
            await interaction.followup.send("🔐 2FA is enabled on your account. Please click the button below to enter your password.", view=view, ephemeral=True)
        except Exception as e:
            logging.error(f"Error in OTPModal: {e}")
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

class PasswordModal(discord.ui.Modal, title="Telegram Session: 2FA Password"):
    password = discord.ui.TextInput(label="2FA Password", placeholder="Your password", required=True, style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_id = interaction.user.id
        
        if user_id not in pending_auths:
            await interaction.followup.send("❌ Session expired or not found. Please restart the process.", ephemeral=True)
            return
            
        auth_data = pending_auths[user_id]
        client_gen = auth_data['client']
        password_val = self.password.value.strip()

        try:
            await client_gen.sign_in(password=password_val)
            
            # Success!
            session_str = client_gen.session.save()
            await client_gen.disconnect()
            del pending_auths[user_id]
            
            await interaction.followup.send(f"✅ **Login Successful!**\n\nYour session string is:\n```\n{session_str}\n```\n\n**Keep this string private!** It gives full access to your account.", ephemeral=True)
            
        except Exception as e:
            logging.error(f"Error in PasswordModal: {e}")
            await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

class SessionStartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Start Login", style=discord.ButtonStyle.primary)
    async def start_login(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PhoneModal())

class OTPView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Enter OTP", style=discord.ButtonStyle.success)
    async def enter_otp(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(OTPModal())

class PasswordView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Enter 2FA Password", style=discord.ButtonStyle.success)
    async def enter_password(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PasswordModal())

@tree.command(name="sessionstring", description="Generate a Telegram session string for your account")
async def sessionstring(interaction: discord.Interaction):
    """Initiates the session string generation flow."""
    try:
        embed = discord.Embed(
            title="🔑 Telegram Session Generator",
            description=(
                "Click the button below to start the session generation process.\n\n"
                "**Why generate a session?**\n"
                "This allows the bot to use your account to forward ads safely."
            ),
            color=0x4285f4
        )
        view = SessionStartView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    except Exception as e:
        logger.error(f"Error in sessionstring command: {e}")
        await interaction.response.send_message(f"❌ Failed to start session generator: {e}", ephemeral=True)

@tree.command(name="structure", description="View the project structure, groups, and campaign details.")
async def structure(interaction: discord.Interaction):
    """Displays a formatted markdown overview of all groups and campaigns."""
    await interaction.response.defer(ephemeral=True)
    try:
        campaigns = await get_all_campaigns()
        
        if not campaigns:
            await interaction.followup.send("❌ No campaigns found in the database.", ephemeral=True)
            return

        # Group data
        groups_data = {}
        for row in campaigns:
            g_name = row['group_name'] or "Standalone / Ungrouped"
            if g_name not in groups_data:
                groups_data[g_name] = []
            groups_data[g_name].append(row)

        content = "# 📊 Project Structure Overview\n\n"
        
        for g_name, members in groups_data.items():
            content += f"### 📁 Group: `{g_name}`\n"
            content += "| Campaign Name | Status | Topic | Ends In | Last Run | Post Link |\n"
            content += "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            
            for m in members:
                # Calculate time remaining
                end_time = m['end_time']
                if end_time:
                    try:
                        if isinstance(end_time, str):
                            end_dt = datetime.datetime.fromisoformat(end_time)
                        else:
                            end_dt = end_time
                        
                        remaining = end_dt - datetime.datetime.now()
                        if remaining.total_seconds() > 0:
                            days = remaining.days
                            hours, remainder = divmod(remaining.seconds, 3600)
                            time_str = f"{days}d {hours}h"
                        else:
                            time_str = "Expired"
                    except:
                        time_str = "Unknown"
                else:
                    time_str = "Forever"

                # Format last run
                last_run = m['last_run_at']
                if not last_run or (isinstance(last_run, int) and last_run == 0):
                    last_run_str = "Never"
                else:
                    last_run_str = "Recent" # Keep it short for table

                # Status emoji
                status = m['status']
                status_emoji = "🟢" if status == "ACTIVE" else "🟡" if status == "PAUSED" else "🔴"
                
                row_dict = dict(m)
                post_link = row_dict.get('target_post_link', 'No Link')
                content += f"| {m['name']} | {status_emoji} {status} | `{m['target_topic_keyword']}` | {time_str} | {last_run_str} | [Link]({post_link or 'No Link'}) |\n"
            
            content += "\n"

        # Split content if it's too long for a single message
        if len(content) > 1900:
            # For simplicity, if it's too long, we send as multiple blocks or just summarize
            # Here we'll just send the first 1900 chars for now, or a file if needed.
            # But usually it fits.
            await interaction.followup.send(content[:1900] + "... (truncated)", ephemeral=True)
        else:
            await interaction.followup.send(content, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in structure command: {e}", exc_info=True)
        await interaction.followup.send(f"❌ Failed to generate structure report: {e}", ephemeral=True)

@tree.command(name="join", description="Make accounts join a Telegram folder (addlist).")
@app_commands.describe(
    link="The t.me/addlist/... invite link.",
    campaign_name="Specific campaign/account to join.",
    group_name="Join for ALL accounts in this group.",
    all="Join ALL campaigns/accounts (ignores campaign_name and group_name)."
)
async def join(interaction: discord.Interaction, link: str = "https://t.me/addlist/yvd6lEjAPV0wODFk", campaign_name: str = None, group_name: str = None, all: bool = False):
    """Makes one or more accounts join a Telegram chat folder."""
    if not all and not campaign_name and not group_name:
        await interaction.response.send_message("❌ You must provide either `campaign_name`, `group_name`, or set `all=True`.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    
    try:
        targets = []
        
        if all:
            # Join ALL campaigns
            targets = await get_all_campaigns()
            if not targets:
                await interaction.followup.send("❌ No campaigns found in the database.", ephemeral=True)
                return
            scope_msg = f"**ALL {len(targets)} campaigns**"
        elif campaign_name:
            c = await get_campaign(campaign_name)
            if c: 
                targets.append(c)
                scope_msg = f"campaign `{campaign_name}`"
            else:
                await interaction.followup.send(f"❌ Campaign '{campaign_name}' not found.", ephemeral=True)
                return
        elif group_name:
            targets = await get_campaigns_by_group(group_name)
            if not targets:
                await interaction.followup.send(f"❌ No accounts found in group '{group_name}'.", ephemeral=True)
                return
            scope_msg = f"group `{group_name}` ({len(targets)} accounts)"

        await interaction.followup.send(f"⏳ Starting join process for {scope_msg}. Please wait...", ephemeral=True)
        
        results = []
        success_count = 0
        for i, acc in enumerate(targets):
            try:
                # Use the session string from the campaign
                status = await tg_manager.join_folder(link, session_string=acc['session_string'])
                results.append(f"✅ `{acc['name']}`: {status}")
                success_count += 1
            except Exception as e:
                results.append(f"❌ `{acc['name']}`: {str(e)}")
            
            # Randomized delay between account joins in a group for safety
            if i < len(targets) - 1:
                delay = random.randint(10, 30)
                await asyncio.sleep(delay)

        # Build a summary message
        report = f"### 📂 Folder Join Report\n**Scope**: {scope_msg}\n**Link**: {link}\n**Success**: {success_count}/{len(targets)}\n\n" + "\n".join(results)
        
        if len(report) > 1900:
            await interaction.followup.send(f"✅ Join process finished! **{success_count}/{len(targets)}** accounts joined successfully. (Full report too long, check bot logs for details).", ephemeral=True)
        else:
            await interaction.followup.send(report, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in join command: {e}", exc_info=True)
        await interaction.followup.send(f"❌ Logic error in join command: {e}", ephemeral=True)

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
