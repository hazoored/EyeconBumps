import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD_ID = 1454150964968820816


# Telegram configuration (API ID and Hash from my.telegram.org)
# USING GENERIC PUBLIC KEYS (Fallback)
TELEGRAM_API_ID = 2040
TELEGRAM_API_HASH = 'b18441a1ff607e10a989891a5462e627'

# Telegram Proxy Configuration
# Format: ('socks5', '127.0.0.1', 9050) or ('http', 'proxy_host', 8080)
# MTProto Format: ('host', port, 'secret')
# Set to None to disable proxy.
TELEGRAM_PROXY = None

# Telegram Admin Session (The account that talks to BotFather)
# This can be a session string or a path to a session file
ADMIN_SESSION_STRING = os.getenv('ADMIN_SESSION_STRING', '1BJWap1wBu2rvaMLoyM_27h8dHi3z4U2aun3fWZOrPvsINz6V5aqnvph_1CwSEfwoyleX6SYr_thpITpJOOcCr9h-gny1V8abpAjcFwFf82y_hO3qASs_633xRTDqzw4hjiEgIiwcY2LN3ezTF_CWuyPgsZU5QfBZBg7koiZPRcNUi-1nPL7OOsp9oNW650LviwprGZ7IzLnJnXqTB5Xctr4vlo5uda0uNNPW0bqVKDmm8HCvmPT2QhZH8l1gO-pdoUXa9ELEi81t6rH4HXD1C-iW7lvFli3R7EqZzTa27IBavrCIiJUGaYEJsULVI9ET45jc4qvu8WAvdbfAqoggcHFGdSx5HBM=')
# Database config
DB_PATH = 'data/campaigns.db'

# Platform Constants
INSTAGRAM = "Instagram"
TIKTOK = "TikTok"
TWITTER = "Twitter"
TELEGRAM = "Telegram"
YOUTUBE = "YouTube"
DISCORD = "Discord"
SNAPCHAT = "Snapchat"
TWITCH = "Twitch"
FACEBOOK = "Facebook"
WHATSAPP = "WhatsApp"
STEAM = "Steam"
XBOX = "Xbox"
PLAYSTATION = "PlayStation"
PLAYSTATION = "PlayStation"
ROBLOX = "Roblox"
# Safety & Delay Configuration
# ------------------------------
# Time (in seconds) to wait between forwarding to the next group for the SAME account.
# Randomized between MIN and MAX.
# SUGGESTED: 30 to 90 seconds for safety.
AD_FORWARD_DELAY_MIN = 5
AD_FORWARD_DELAY_MAX = 60

# Time (in seconds) to wait after SKIPPING a group (or failing).
# This prevents rapid-fire looping through invalid groups (Safety).
AD_SKIP_DELAY_MIN = 3
AD_SKIP_DELAY_MAX = 7

# Time (in seconds) to wait between starting different account/campaign tasks.
# This prevents all accounts from waking up at the exact same second.
CAMPAIGN_STAGGER_DELAY = 5

# Telemetry Spoofing: List of device models to rotate through safely.
# Each session will be deterministically assigned one of these based on its hash.
DEVICE_MODELS = [
    {'device_model': 'iPhone 15 Pro Max', 'system_version': 'iOS 17.2.1', 'app_version': '10.3.1', 'lang_code': 'en', 'system_lang_code': 'en-US'},
    {'device_model': 'iPhone 14 Pro', 'system_version': 'iOS 16.6', 'app_version': '10.2.0', 'lang_code': 'en', 'system_lang_code': 'en-US'},
    {'device_model': 'iPhone 13', 'system_version': 'iOS 15.5', 'app_version': '9.6.4', 'lang_code': 'en', 'system_lang_code': 'en-GB'},
    {'device_model': 'Samsung S24 Ultra', 'system_version': 'Android 14', 'app_version': '10.5.1', 'lang_code': 'en', 'system_lang_code': 'en-US'},
    {'device_model': 'Pixel 8 Pro', 'system_version': 'Android 14', 'app_version': '10.4.5', 'lang_code': 'en', 'system_lang_code': 'en-US'},
    {'device_model': 'Samsung S23', 'system_version': 'Android 13', 'app_version': '10.1.0', 'lang_code': 'en', 'system_lang_code': 'en-US'},
    {'device_model': 'Xiaomi 13T', 'system_version': 'Android 13', 'app_version': '9.7.0', 'lang_code': 'en', 'system_lang_code': 'en-GB'},
    {'device_model': 'OnePlus 11', 'system_version': 'Android 14', 'app_version': '10.0.0', 'lang_code': 'en', 'system_lang_code': 'en-US'},
]

# Rich Log Bot Configuration
# Maps Campaign Group Names -> (Bot Token, Log Channel ID)
# IMPORTANT: Replace 'REPLACE_WITH_CHANNEL_ID' with the actual destination channel ID (e.g., -10012345678)
LOG_STRATEGY = {
    'Eyecon': {
        'token': '8237137634:AAFCcUxQorR3kP0bpZTlGFLSvrNBzq1bxAU',
        'channel_id': 'REPLACE_WITH_CHANNEL_ID' 
    },
    'Khan': { # Assuming Khan uses Wizard logs? Or same as Wizard? Defaulting to Wizard for others.
        'token': '8504440953:AAH0XiZ2t0Ze9GxIor-9-9f9kxVwux7ybto',
        'channel_id': 'REPLACE_WITH_CHANNEL_ID'
    },
     'Hashim': {
        'token': '8504440953:AAH0XiZ2t0Ze9GxIor-9-9f9kxVwux7ybto',
        'channel_id': 'REPLACE_WITH_CHANNEL_ID'
    },
     # catch-all default
    'DEFAULT': {
        'token': '8504440953:AAH0XiZ2t0Ze9GxIor-9-9f9kxVwux7ybto',
        'channel_id': 'REPLACE_WITH_CHANNEL_ID'
    }
}

OTHER = "Other"

# Aliases for input normalization (Lowercase keys)
ALIASES = {
    # Instagram
    "ig": INSTAGRAM,
    "insta": INSTAGRAM,
    "instagram": INSTAGRAM,
    
    # TikTok
    "tt": TIKTOK,
    "Tiktok": TIKTOK,
    "tiktok": TIKTOK,
    
    # Twitter / X
    "tw": TWITTER,
    "twt": TWITTER,
    "twitter": TWITTER,
    "x": TWITTER,
    
    # YouTube
    "yt": YOUTUBE,
    "youtube": YOUTUBE,
    "Youtube": YOUTUBE,
    
    # Telegram
    "tg": TELEGRAM,
    "tele": TELEGRAM,
    "telegram": TELEGRAM,
    
    # Discord
    "dc": DISCORD,
    "disc": DISCORD,
    "discord": DISCORD,
    
    # Snapchat
    "snap": SNAPCHAT,
    "sc": SNAPCHAT,
    "snapchat": SNAPCHAT,
    
    # Twitch
    "tv": TWITCH,
    "twitch": TWITCH,
    
    # Facebook
    "fb": FACEBOOK,
    "face": FACEBOOK,
    "facebook": FACEBOOK,
    
    # WhatsApp
    "wa": WHATSAPP,
    "Whatsapp": WHATSAPP,
    "whatsapp": WHATSAPP,
    
    # Gaming
    "steam": STEAM,
    "xbox": XBOX,
    "ps": PLAYSTATION,
    "ps4": PLAYSTATION,
    "ps5": PLAYSTATION,
    "playstation": PLAYSTATION,
    "roblox": ROBLOX,
}

GROUPS_CONFIG = {
    -1002212302600: {
        'TikTok': 8,
        'Instagram': 2,
        'Telegram': 5,
        'Discord': 10,
        'Chats': 30,
        'General': 1,
        'Twitter': 4,
        'Facebook': 6,
        'WhatsApp': 3,
        'YouTube': 9,
        'Exchange': 150864,
        'New flips group here join now': 174746,
        'Snapchat': 7,
        'Middleman': 197097,
    },
    -1002403320794: {
        'Joining List': 1,
        'Information': 477091,
        'Rules and Regulations!': 156220,
        'Buying #Anything': 5418,
        'TikTok': 7,
        'Instagram': 2,
        'Snapchat': 5823,
        'Selling #Anything': 5419,
        "Join Log's & Verification": 522692,
        'Discord': 6,
        'Telegram': 5,
        'WhatsApp': 8,
        'Twitter': 477078,
        'Crypto': 4,
        'Threads': 72,
        'Facebook': 3,
    },
    -1002861227345: {
        'General': 1,
        'TOS': 4,
        'Directory': 2,
        'Middleman': 9263,
        'Muted': 77971,
        'Instagram': 6,
        'Telegram': 5,
        'Other': 8,
        'Twitter': 6636,
        'Exchange': 7,
    },
    -1003254168777: None,
    -1002000383834: {
        '️': 1,
        'Ad': 999280,
        'Rules': 8271,
        'Important': 97067,
        'TikTok': 8270,
        'Discord': 8264,
        'Twitter': 8265,
        'Instagram': 8266,
        'Telegram': 8263,
        'Other': 8268,
        'Exchange': 8269,
        'YouTube': 8665,
        'Join Logs': 268850,
    },
    -1002270409535: {
        'General': 1,
        'Unknown Network': 5,
        'Rules': 3,
        'Middleman': 6,
        'Instagram': 10,
        'Discord': 16,
        'Telegram': 13,
        'Other': 19,
        'TikTok': 11,
        'YouTube': 18,
        'Snapchat': 12,
        'Twitter': 17,
        'Currency Exchange': 14,
    },
    -1002387132758: {
        'General': 1,
        'Rainbet.com': 1588010,
        'Telegram': 6,
        'YouTube': 10,
        'Discord': 18,
        'TikTok': 14,
        'Snapchat': 20,
        'Exchanges': 16,
        'Twitter': 4,
        'PlayStation': 28,
        'Xbox': 26,
        'Twitch': 22,
        'Steam': 30,
        'Instagram': 24,
    },
    -1002948708578: {
        'General': 1,
        'Instagram': 9,
        'Other': 44,
        'Discord': 8,
        'TikTok': 14,
        'YouTube': 21,
        'Twitter': 39,
        'Exchange': 35,
        'WhatsApp': 12,
        'Twitch': 19,
        'Snapchat': 37,
        'Telegram': 23,
        'Rules': 5,
    },
    -1001741213429: {
        'Muslimah Fashion': 13701,
        'Skin & Personal Care': 13697,
        'Headscarves & Inner': 13731,
        'Food & Beverage': 13704,
        'Cosmetics & Fragrance': 13695,
        'Instagram': 13748,
    },
    -1002400377837: {
        'Instagram': 9,
        'Twitter': 5,
        'YouTube': 3,
        'Discord': 8,
        'TikTok': 6,
        'Other': 7,
        'Telegram': 10,
        'WhatsApp': 11,
        '𝐆𝐞𝐧𝐞𝐫𝐚𝐥': 1,
        'Snapchat': 187,
        '𝐆𝐀𝐌𝐈𝐍𝐆': 4,
    },
    -1002060897480: {
        'General': 1,
        'Other': 8,
        'Telegram': 15,
        'Instagram': 17,
        'currency exchanges': 9,
        'Discord': 14,
        'Snapchat': 3769,
        'TikTok': 13,
        'Twitter': 16,
        'YouTube': 12,
    },
    -1002011482119: {
        'Instagram': 79,
        'Other': 83,
        'Discord': 5732,
        'Snapchat': 5735,
        'Telegram': 85,
        'TikTok': 272,
        'Facebook': 82,
        'Twitter': 273,
        'YouTube': 5737,
        'Kick Handles': 5729,
        'General': 1,
    },
    -1002909912210: {
        'OGUsers Network': 2,
        'Middlemen': 3,
        'Report Scammers': 6,
        'Telegram': 5,
        'Other': 10,
        'Gaming': 17,
        'Discord': 9,
        'Instagram': 15,
        'YouTube': 12,
        'TikTok': 11,
        'Exchange': 14,
        'Twitter': 8,
        'Snapchat': 13,
        'Twitch': 22,
        'Fortnite': 19,
        'Steam': 21,
        'Kick': 23,
        'Minecraft': 20,
        'Gamertags': 24,
        'General': 1,
        'TOS': 4,
    },
    -1002148536458: {
        '𝙘𝙧𝙞𝙨𝙜𝙖𝙡𝙖𝙭𝙮 𝙚𝙙𝙞𝙩𝙞𝙣𝙜 𝙯𝙤𝙣𝙚': 131744,
        '𝘾𝙧𝙞𝙨𝙜𝙖𝙡𝙖𝙭𝙮𝙫𝙤𝙪𝙘𝙝𝙚𝙨': 2255,
        'ℂ𝕣𝕚𝕤𝕘ᵃ𝕝𝕒𝕩𝕪 𝕡𝕠𝕣𝕥𝕒𝕝': 2259,
        'Instagram': 6,
        'TIK TOK': 325,
        'Telegram': 324,
        'Discord': 1246,
        'Facebook': 1245,
        'Snapchat': 1247,
        'For editors promotion': 131832,
        'WhatsApp': 7,
        'YouTube': 1424,
        'BAN AND UNBANS': 323,
        'META SUPPORT': 1248,
        'GOOGLE': 1426,
        'General': 1,
        'SPOTIFY': 1425,
        'Agent': 3994,
        '𝘾𝙧𝙞𝙨𝙜𝙖𝙡𝙖𝙭𝙮 𝙨𝙚𝙧𝙫𝙞𝙘𝙚𝙨': 1239,
        'ANNOUNCEMENTS': 2950,
        'SCAMMER EXPOSE': 266,
        'MIDDLE MAN': 8,
    },
    -1002035477675: {
        'General': 1,
        'Chat': 14574,
        'Graphics': 15491,
        'Instagram': 14577,
        'Telegram': 14616,
        'Tik Tok': 14585,
        'Twitter': 14583,
        'Snapchat': 14579,
        'WhatsApp': 14575,
        'YouTube': 14581,
    },
    -1001940074224: {
        'Sellers Bay': 57,
        'Buyers Community': 18,
        "Buyer's Bay": 38,
        'Exchange - Convert 💲': 39,
        'Vouch': 17,
        'Escrow - M.M Service': 56,
        'Instagram': 1,
    },
    -1002100850001: {
        'TikTok': 3,
        'Instagram': 4,
        'General': 1,
        'Telegram': 9,
        'Snapchat': 8,
        'Twitter': 10,
        'Exchange': 5,
        'TOS': 12,
        'Fortnite': 7,
        'Roblox': 56,
        'Gamertags': 6,
    },
    -1001624196878: {
        'P2P арбитраж': 936,
        'Поиск новых проектов': 513,
        'ICO/IDO': 514,
        'NFT': 517,
        'Обсуждение рынка': 512,
        'Scam alert': 520,
        'Instagram': 1,
    },
    -1001594164440: None,
    -1003494087656: {
        'General': 1,
        'Announcements': 190,
        'Advertising': 6,
        'Information': 4,
        'Instagram': 92,
        'YouTube': 13,
        'Telegram': 8,
        'Other': 14,
        'Discord': 11,
        'TikTok': 12,
        'Twitter': 9,
        'Exchanges': 10,
        "Join Log's & Verification": 16,
    },
    -1002489262783: {
        'General': 1,
        'Middleman Tos': 17415,
        'Rules': 10,
        'Report scammers': 12,
        'Discord': 37,
        'Instagram': 21,
        'Telegram': 41,
        'Snapchat': 62,
        'Other': 20,
        'TikTok': 46,
        'Twitter': 50,
        'Exchange service': 32,
        'YouTube': 54,
        'Kick': 66,
        'Fortnite': 70,
        'Development': 58,
    },
    -1002164367927: {
        'TikTok': 12,
        'Instagram': 21,
        'WhatsApp': 20,
        'Other': 14,
        'GFX Services': 15,
        'Gamer-Tags': 18,
        'Snapchat': 10,
        'Telegram': 19,
        'Twitter': 11,
        'Discord': 9,
        'Crypto Exchanges': 16,
        'YouTube': 13,
        'General': 24,
    },
    -1002191594970: {
        'General': 1,
        'TIK TOK': 6,
        'WhatsApp': 10,
        'Instagram': 3,
        'Telegram': 4,
        'Discord': 9,
        'Snapchat': 8,
        'Facebook': 11,
        'Other': 16,
        'Twitter': 5,
        'EXCHANGE': 12,
        'YouTube': 7,
        'BAN & UNBANS': 22,
        'EDITS': 13,
    },
    -1001268293786: None,
    -1002434461534: {
        'Plugger': 185992,
        'TikTok': 56737,
        'Other': 7,
        'Instagram': 8,
        'Snapchat': 390814,
        'Facebook': 3,
        'Telegram': 6303,
        'General': 1,
        'Twitter': 2,
        'Exchange crypto/bank': 4,
        'Discord': 410363,
        'YouTube': 5,
    },
    -1001676369027: {
        'Telegram': 120084,
        'Instagram': 120080,
        'Anycomment': 1,
        'Snapchat': 120075,
        'TikTok': 120071,
        'Auctions': 120088,
    },
    -1002069748765: {
        'General': 1,
        'Instagram': 11,
        'Telegram': 17,
        'TIK TOK': 24,
        'Snapchat': 21,
        'Other': 23,
        'WhatsApp': 37,
        'YouTube': 22,
        'OTT': 42,
        'CHATS': 30,
        'GAMES': 13,
    },
    -1001976519716: {
        'Exchange': 11,
        '-': 1,
        'Discord': 22,
        'Other': 28,
        'WhatsApp': 33,
        'Instagram': 20,
        'TikTok': 30,
        'Telegram': 16,
        'Kick': 18,
    },
    -1001836523109: {
        'General': 1,
        'Scammers': 20,
        'TOS': 11,
        'Instagram': 28,
        'Other': 32,
        'TikTok': 30,
        'Exchange': 31,
        'Telegram': 29,
        'Chatroom': 25,
    },
    -1002178340194: {
        'General': 1,
        'Chat Group': 12,
        'Telegram': 4,
        'Instagram': 5,
        'TikTok': 31,
        'Other': 32,
        'Discord': 10,
        'WhatsApp': 11,
        'Twitter': 9,
        'YouTube': 6,
    },
    -1001505780126: None,
    -1001825295385: None,
    -1001876591816: None,
    -1002262118444: {
        'General': 1,
        'LizardSwap 0.2%': 422241,
        'Alert': 254191,
        'Middleman': 334,
        'Rules': 342663,
        'VIP': 385760,
        'TikTok': 383361,
        'Instagram': 319,
        'Snapchat': 320,
        'Telegram': 325,
        'Twitter': 328,
        'Other': 331,
        'Discord': 383423,
        'Roblox': 372987,
        'Exchange': 383283,
        'Minecraft': 394127,
    },
    -1002258810204: {
        'STOCKS CHANNEL': 1238646,
        'Instagram': 31,
        'Discord': 20,
        'TikTok': 33,
        'Exchange Services': 30,
        'Other': 39,
        'Twitter': 23,
        'Telegram': 21,
        'Snapchat': 27,
        'Facebook': 35,
        'Roblox': 42,
        'YouTube': 22,
        'welcome': 1,
        'Steam': 32,
        'Gfx Services': 36,
        'Xbox': 29,
        'Twitch': 24,
        'Web Development': 37,
        'Minecraft': 26,
    },
    -1002256623070: {
        'Exchange': 10,
        'Instagram': 11992,
        'Other': 12018,
        'Gaming': 22,
        'Telegram': 2,
        'Discord': 4,
        'TikTok': 8,
        'Snapchat': 12,
        'Twitter': 17,
        'YouTube': 15,
        'Steam': 12001,
        'Minecraft': 19,
        'Fortnite': 11,
        'Twitch': 46,
        'Gamertags': 11995,
        'Kick': 11985,
    },
    -1002260640904: {
        'Chatting group': 2345,
        'Instagram': 17,
        'Other': 13,
        'Snapchat': 14,
        'General chatting': 1,
        'TikTok': 7,
        'Telegram': 15,
        'Discord': 9,
        'WhatsApp': 10,
        'YouTube': 6,
        'Facebook': 8,
        'Twitter': 5,
        'Gaming 🥂': 4,
        'EDITING': 12,
        'Ott platforms': 11,
    },
    -1002199697522: {
        'General': 1,
        'Information': 23,
        'Other': 13,
        'Telegram': 21,
        'Instagram': 22,
        'YouTube': 16,
        'TikTok': 20,
        'Snapchat': 17,
        'Twitter': 19,
        'Discord': 475247,
        'Mutual': 68316,
    },
    -1002359309381: {
        '@Bump Adverts': 788386,
        'Telegram': 8,
        'Other': 21,
        'TikTok': 23,
        'Discord': 10,
        'Instagram': 15,
        'YouTube': 19,
        'Twitter': 17,
        'Exchange - https://swap.my': 6,
        'Snapchat': 25,
        'General': 1,
    },
    -1002458836454: None,
    -1001978115617: {
        'TOS': 51,
        'General': 1,
        'Instagram': 3,
        'TikTok': 8,
        'Telegram': 6,
        'Twitter': 9,
        'Snapchat': 5,
        'YouTube': 4,
    },
    -1002066254327: {
        'Other': 99,
        'General': 1,
        'Instagram': 94,
        'Telegram': 95,
        'Deals nd Courses': 98,
        'Snapchat': 96,
        'AI SERVICES': 97,
    },
    -1001987613424: {
        'General': 1,
        'Instagram': 2,
        'TikTok': 8,
        'Other': 6,
        'Snapchat': 5,
        'Telegram': 3,
        'YouTube': 10,
        'Twitter': 4,
        'Gaming': 9,
    },
    -1002146109894: {
        'Directory': 1402689,
        'Middleman': 1403447,
        'TOS': 1402678,
        'Instagram': 39,
        'Other': 54,
        'Telegram': 45,
        'Snapchat': 50,
        'YouTube': 41,
        'TikTok': 671752,
        'Twitter': 43,
        'WhatsApp': 38,
        'Facebook': 671753,
    },
    -1002528685086: {
        'Telegram': 3,
        'Instagram': 24,
        'Currency Exchanges': 9,
        'WhatsApp': 647047,
        'TikTok': 4,
        'Snapchat': 25,
        'Discord': 7,
        'YouTube': 6,
        'Twitter': 5,
        'Facebook': 92,
    },
    -1001896085289: {
        'Instagram': 127873,
        'Telegram': 127882,
        'Discord': 127884,
        'YouTube': 127875,
        'TikTok': 127877,
        'Twitter': 127880,
        'Snapchat': 127872,
    },
    -1001687199609: {
        'MARKET CHAT': 1,
        'Other': 71899,
        'Instagram': 71892,
        'TikTok': 71894,
        'Discord': 74299,
        'Telegram': 74145,
        'Snapchat': 71922,
        'EXCHANGE SERVICE': 878160,
        'Twitter': 71893,
        'WhatsApp': 107245,
        'PlayStation': 878296,
        'YouTube': 377367,
        'MINI GAMES': 878393,
    },
    -1002442347480: {
        'Instagram': 4,
        'Telegram': 2,
        'Services': 6,
        'Discord': 3,
        'Other': 5,
        'General': 1,
    },
    -1002399624593: None,
    -1002179489939: None,
    -1002587251219: {
        'General': 1,
        'Instagram': 25,
        'Discord': 12,
        'Telegram': 15,
        'YouTube': 16,
        'Snapchat': 14,
        'Scammer Alert': 5901,
        'Rules': 5897,
    },
    -1001219270722: None,
    -1001776653386: None,
    -1001640434189: None,
    -1002096664082: None,
    -1001657821116: None,
    -1001577883958: None,
    -1002102940196: None,
    -1002052287634: None,
    -1001836335934: None,
}