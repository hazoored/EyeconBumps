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
ADMIN_SESSION_STRING = os.getenv('ADMIN_SESSION_STRING', '1BJWap1wBuzWdQTQxKjjM1zLZ5r_BaL2RNumTbBnjhAfd3mqKyPdzRVJtpfT7tPI00LITBJYCQ_WpbhwEr2iWtKXRgpc0Mqe1InWF_mLDY72xoZLr_qqUxerB2MPmIZqDtFNNmV4t75LmyUA45FhDuzelawFVaJMifOBRFBxgddiGsV38dDcNSRcJoGuG82dSSyIVicnN8_0dnSSsVtSrBZVBAQtTPYuaFaieF9QMOmIPeQJrcdDrPnM4PJ0j8FDdpOXYdg1trKYYsLbXIhS0hWPzdE7YehdDwBUZr8QneuzJHJ9__Ll1Lv74kj5s1I641TJ5Hlr6BhnkxURwqCyZAyLNIVOxCrg=')

# Database config - Use absolute path to ensure persistence across restarts
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_BASE_DIR, 'data')
# Ensure data directory exists
os.makedirs(_DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(_DATA_DIR, 'campaigns.db')

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
# You can also provide a list of IDs for multiple recipients, e.g., 'channel_id': ['ID1', 'ID2']
LOG_STRATEGY = {
    'Eyecon': {
        'token': '8237137634:AAFCcUxQorR3kP0bpZTlGFLSvrNBzq1bxAU',
        'channel_id': '6926297956' 
    },
    'Khan': {
        'token': '8221090341:AAHkVpzI-npe0FDf22EYpmhvPrMwRKH0OqY', # <--- ENTER KHAN BOT TOKEN
        'channel_id': '6926297956'
    },
     'Hashim': {
        'token': '7745783676:AAEQAV5ytzp6C0WZDn1CpN1Ffyc39UrHr2s', # <--- ENTER HASHIM BOT TOKEN
        'channel_id': ['6926297956', '7012601869']
    },
    'Wizard': {
        'token': '8504440953:AAH0XiZ2t0Ze9GxIor-9-9f9kxVwux7ybto',
        'channel_id': ['6926297956', '5521050348']
    },
     # catch-all default
    'DEFAULT': {
        'token': '', # Default to Wizard
        'channel_id': ''
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
    -1002100850001: {
        "General": 1,
        "Instagram": 4,
        "Tiktok": 3,
        "Telegram": 9,
        "Snapchat": 8,
        "Twitters": 10,
        "Exchange": 5,
        "TOS": 12,
        "Fortnite": 7,
        "Roblox": 56,
        "Gamertags": 6,
    },
    -1002434461534: {
        "Plugger": 185992,
        "General": 1,
        "Other Services": 7,
        "Instagram": 8,
        "Telegram": 6303,
        "Exchange crypto/bank": 4,
        "Twitter": 2,
        "TikTok": 56737,
        "Discord": 410363,
        "YouTube": 5,
        "facebook": 3,
        "Snapchat": 390814,
    },
    -1002199697522: {
        "General": 1,
        "Information": 23,
        "Discord": 475247,
        "Instagram": 22,
        "Other": 13,
        "Telegram": 21,
        "Tiktok": 20,
        "Youtube": 16,
        "Twitter": 19,
        "Snapchat": 17,
        "Mutual": 68316,
    },
    -1001624196878: {
        "P2P арбитраж": 936,
        "Поиск новых проектов": 513,
        "General": 1,
        "ICO/IDO": 514,
        "NFT": 517,
        "Обсуждение рынка": 512,
        "Scam alert": 520,
    },
    -1003586454504: {
        "General": 1,
        "Instagram": 236,
        "For OFM": 259,
        "Other services": 244,
        "Reddit": 243,
        "Whatsapp": 242,
        "X/twitter": 241,
        "Twitch": 240,
        "Snapchat": 239,
        "Discord": 238,
        "Tiktok": 237,
        "Telegram": 235,
    },
    -1002060897480: {
        "General": 1,
        "other accounts & services": 8,
        "instagram": 17,
        "telegram": 15,
        "discord": 14,
        "currency exchanges": 9,
        "tiktok": 13,
        "twitter / X": 16,
        "youtube": 12,
        "Snapchat": 3769,
    },
    -1002148536458: {
        "𝙘𝙧𝙞𝙨𝙜𝙖𝙡𝙖𝙭𝙮 𝙚𝙙𝙞𝙩𝙞𝙣𝙜 𝙯𝙤𝙣𝙚": 131744,
        "𝘾𝙧𝙞𝙨𝙜𝙖𝙡𝙖𝙭𝙮𝙫𝙤𝙪𝙘𝙝𝙚𝙨": 2255,
        "ℂ𝕣𝕚𝕤𝕘𝕒𝕝𝕒𝕩𝕪 𝕡𝕠𝕣𝕥𝕒𝕝": 2259,
        "DISCORD": 1246,
        "INSTAGRAM": 6,
        "TELEGRAM": 324,
        "TIK TOK": 325,
        "BAN AND UNBANS": 323,
        "WHAT'S APP": 7,
        "YOU TUBE": 1424,
        "SNAPCHAT": 1247,
        "General": 1,
        "GOOGLE": 1426,
        "SPOTIFY": 1425,
        "META SUPPORT": 1248,
        "For editors promotion": 131832,
        "FACE BOOK": 1245,
        "Agent": 3994,
        "𝘾𝙧𝙞𝙨𝙜𝙖𝙡𝙖𝙭𝙮 𝙨𝙚𝙧𝙫𝙞𝙘𝙚𝙨": 1239,
        "ANNOUNCEMENTS": 2950,
        "SCAMMER EXPOSE": 266,
        "MIDDLE MAN": 8,
    },
    -1001268293786: None, # Simple Group
    -1002260640904: {
        "Chatting group": 2345,
        "Instagram services": 17,
        "Facebook": 8,
        "Tiktok": 7,
        "Twitter": 5,
        "Telegram": 15,
        "WhatsApp": 10,
        "Discord ✌️": 9,
        "Others account": 13,
        "General chatting": 1,
        "Snapchat": 14,
        "YouTube 🤍": 6,
        "Ott platforms": 11,
        "Gaming 🥂": 4,
        "EDITING": 12,
    },
    -1002069748765: {
        "General": 1,
        "TELEGRAM": 17,
        "INSTAGRAM": 11,
        "OTHER": 23,
        "TIK TOK": 24,
        "WHATSAPP": 37,
        "YOUTUBE": 22,
        "SNAPCHAT": 21,
        "GAMES": 13,
        "OTT": 42,
        "CHATS": 30,
    },
    -1001940074224: {
        "General Chat": 1,
        "Sellers Bay": 57,
        "Buyers Community": 18,
        "Buyer's Bay": 38,
        "Vouch": 17,
        "Exchange - Convert 💲": 39,
        "Escrow - M.M Service": 56,
    },
    -1002861227345: {
        "General": 1,
        "TOS": 4,
        "Directory": 2,
        "Middleman": 9263,
        "Muted": 77971,
        "Instagram": 6,
        "Other Services": 8,
        "Telegram": 5,
        "X/Twitter": 6636,
        "Other Accounts": 9,
        "Exchange": 7,
    },
    -1002262118444: {
        "General": 1,
        "LizardSwap 0.2%": 422241,
        "Alert": 254191,
        "Middleman": 334,
        "Rules": 342663,
        "VIP": 385760,
        "Telegram": 325,
        "Instagram Services": 319,
        "Twitter X": 328,
        "Other Accounts & Services": 331,
        "TikTok": 383361,
        "Discord": 383423,
        "Exchange": 383283,
        "Snapchat": 320,
        "Instagram Usernames": 395837,
        "Roblox": 372987,
        "Minecraft": 394127,
    },
    -1002256623070: {
        "Others Accounts": 9,
        "Other Services": 12018,
        "Telegram": 2,
        "YouTube": 15,
        "Exchange": 10,
        "Discord": 4,
        "Instagram": 11992,
        "Gaming": 22,
        "X/Twitter": 17,
        "Twitch": 46,
        "TikTok": 8,
        "Minecraft": 19,
        "Steam": 12001,
        "Fortnite": 11,
        "Snapchat": 12,
        "Gamertags": 11995,
        "Kick": 11985,
    },
    -1002403320794: {
        "Joining List": 1,
        "Information": 477091,
        "Rules and Regulations!": 156220,
        "Telegram": 5,
        "Selling #Anything": 5419,
        "WhatsApp": 8,
        "Instagram": 2,
        "Snapchat": 5823,
        "TikTok": 7,
        "Crypto": 4,
        "Buying #Anything": 5418,
        "Discord": 6,
        "Join Log's & Verification": 522692,
        "Threads": 72,
        "Facebook": 3,
        "Twitter/X": 477078,
    },
    -1002909912210: {
        "OGUsers Network": 2,
        "Middlemen": 3,
        "Report Scammers": 6,
        "Telegram Premium/Stars": 5,
        "Telegram": 16,
        "Discord": 9,
        "Instagram": 15,
        "Exchange": 14,
        "Other Services": 10,
        "YouTube": 12,
        "Other Accounts": 18,
        "X/Twitter": 8,
        "Snapchat": 13,
        "TikTok": 11,
        "Twitch": 22,
        "Minecraft": 20,
        "Gaming": 17,
        "Fortnite": 19,
        "Steam": 21,
        "Kick": 23,
        "Gamertags": 24,
        "@BetterTelegram": 28901,
        "General": 1,
        "TOS": 4,
    },
    -1002191594970: {
        "OTHER SERVICE'S": 16,
        "INSTAGRAM": 3,
        "TELEGRAM": 4,
        "DISCORD": 9,
        "General": 1,
        "WHATSAPP": 10,
        "EXCHANGE": 12,
        "TWITTER [ X ]": 5,
        "TIK TOK": 6,
        "YOUTUBE": 7,
        "SNAPCHAT": 8,
        "BAN & UNBANS": 22,
        "EDITS": 13,
        "FACEBOOK": 11,
    },
    -1002400377837: {
        "𝐈𝐍𝐒𝐓𝐀𝐆𝐑𝐀𝐌": 9,
        "𝐖𝐇𝐀𝐓𝐒𝐀𝐏𝐏": 11,
        "𝐓𝐈𝐗𝐓𝐎𝐊": 6,
        "𝐃𝐈𝐒𝐂𝐎𝐑𝐃": 8,
        "𝐓𝐄𝐋𝐄𝐆𝐑𝐀𝐌": 10,
        "𝐎𝐭𝐡𝐞𝐫 𝐀𝐜𝐜𝐨𝐮𝐧𝐭𝐬 & 𝐒𝐞𝐫𝐯𝐢𝐜𝐞𝐬": 7,
        "𝐒𝐍𝐀𝐏𝐂𝐇𝐀𝐓": 187,
        "𝐘𝐎𝐔𝐓𝐔𝐁𝐄": 3,
        "𝐗 /𝐓𝐖𝐈𝐓𝐓𝐄𝐑": 5,
        "𝐆𝐞𝐧𝐞𝐫𝐚𝐥": 1,
        "𝐆𝐀𝐌𝐈𝐍𝐆": 4,
    },
    -1001876591816: None, # Simple Group
    -1001741213429: {
        "Other's": 13748,
        "Headscarves & Inner": 13731,
        "Muslimah Fashion": 13701,
        "Skin & Personal Care": 13697,
        "Cosmetics & Fragrance": 13695,
        "Food & Beverage": 13704,
    },
    -1002212302600: {
        "Instagram": 2,
        "Snapchat": 7,
        "WhatsApp": 3,
        "Telegram": 5,
        "Exchange": 150864,
        "Chats": 30,
        "General": 1,
        "Dicord": 10,
        "Twitter/X": 4,
        "TikTok": 8,
        "YouTube": 9,
        "Facebook": 6,
        "New flips group here join now": 174746,
        "Middleman": 197097,
    },
    -1002948708578: {
        "General": 1,
        "Instagram": 9,
        "Discord": 8,
        "Telegram": 23,
        "Tiktok": 14,
        "Other Services": 44,
        "Exchange": 35,
        "Snapchat": 37,
        "Youtube": 21,
        "Twitter / X": 39,
        "Whatsapp": 12,
        "Twitch": 19,
        "Rules": 5,
    },
    -1002164367927: {
        "Telegram": 19,
        "Snapchat": 10,
        "Other Accounts & Services": 14,
        "Discord": 9,
        "Instagram": 21,
        "Whatsapp": 20,
        "Crypto Exchanges": 16,
        "Twitter": 11,
        "Tiktok": 12,
        "GFX Services": 15,
        "Youtube": 13,
        "General": 24,
        "Gamer-Tags": 18,
    },
    -1002489262783: {
        "General": 1,
        "Middleman Tos": 17415,
        "Rules": 10,
        "Report scammers": 12,
        "Instagram": 21,
        "Twitter": 50,
        "Other service": 20,
        "Tiktok": 46,
        "Exchange service": 32,
        "Telegram service": 41,
        "Discord": 37,
        "Snapchat": 62,
        "Kick": 66,
        "Development": 58,
        "YouTube": 54,
        "Fortnite": 70,
    },
    -1002359309381: {
        "@Bump Adverts": 788386,
        "Exchange - https://swap.my": 6,
        "Telegram": 8,
        "Instagram": 15,
        "Discord": 10,
        "Other Accounts & Services": 21,
        "Tiktok": 23,
        "X / Twitter": 17,
        "Youtube": 19,
        "Snapchat": 25,
        "General": 1,
    },
    -1001976519716: {
        "Exchange": 11,
        "Discord": 22,
        "Telegram": 16,
        "Instagram": 20,
        "Other Services": 28,
        "TikTok": 30,
        "-": 1,
        "WhatsApp": 33,
        "Kick": 18,
    },
    -1002387132758: {
        "Rainbet.com": 1588010,
        "YouTube": 10,
        "Other Services": 24,
        "Exchanges": 16,
        "Discord": 18,
        "Other Accounts": 109,
        "TikTok": 14,
        "Telegram": 6,
        "X / Twitter": 4,
        "Snapchat": 20,
        "Playstation": 28,
        "Xbox": 26,
        "Steam": 30,
        "Twitch": 22,
    },
    -1003494087656: {
        "General": 1,
        "Announcements": 190,
        "Advertising": 6,
        "Information": 4,
        "Instagram": 92,
        "Other Service's": 15,
        "Telegram": 8,
        "Discord": 11,
        "Join Log's & Verification": 16,
        "Tiktok": 12,
        "Other Account's": 14,
        "YouTube": 13,
        "Twitter X": 9,
        "Exchanges": 10,
    },
    -1002399624593: None, # Simple Group
    -1002179489939: None, # Simple Group
    -1002587251219: {
        "General": 1,
        "Instagram": 25,
        "Discord": 12,
        "YouTube": 16,
        "Telegram": 15,
        "Snapchat": 14,
        "Scammer Alert": 5901,
        "Rules": 5897,
    },
    -1001219270722: None, # Simple Group
    -1001776653386: None, # Simple Group
    -1001640434189: None, # Simple Group
    -1002096664082: None, # Simple Group
    -1001657821116: None, # Simple Group
    -1001577883958: None, # Simple Group
    -1002102940196: None, # Simple Group
    -1002052287634: None, # Simple Group
    -1001836335934: None, # Simple Group
    -1002458836454: None, # Simple Group
    -1001978115617: {
        "TOS": 51,
        "General": 1,
        "Instagram": 3,
        "Tiktok": 8,
        "Telegram": 6,
        "Twitter": 9,
        "Snapchat": 5,
        "YouTube": 4,
    },
    -1002066254327: {
        "Instagram": 94,
        "General": 1,
        "Telegram": 95,
        "Other services": 99,
        "Snapchat": 96,
        "Deals nd Courses": 98,
        "AI SERVICES": 97,
    },
    -1001987613424: {
        "General": 1,
        "Other OG Accounts & Services": 6,
        "Telegram": 3,
        "Instagram": 2,
        "TikTok": 8,
        "Twitter": 4,
        "Youtube": 10,
        "Gaming": 9,
        "Snapchat": 5,
    },
    -1002146109894: {
        "Directory": 1402689,
        "Middleman": 1403447,
        "TOS": 1402678,
        "Other Services": 54,
        "TikTok": 671752,
        "YouTube": 41,
        "Instagram": 39,
        "Telegram": 45,
        "WhatsApp": 38,
        "X/Twitter": 43,
        "Facebook": 671753,
        "Snapchat": 50,
    },
    -1002528685086: {
        "Currency Exchanges": 9,
        "Telegram": 3,
        "TikTok": 4,
        "Instagram": 24,
        "Discord": 7,
        "YouTube": 6,
        "WhatsApp": 647047,
        "Snapchat": 25,
        "Twitter": 5,
        "Facebook": 92,
    },
    -1001896085289: {
        "Instagram Usernames": 127873,
        "Telegram Usernames": 127882,
        "Instagram": 127871,
        "Tiktok": 127877,
        "Telegram": 127870,
        "Discord": 127884,
        "Youtube": 127875,
        "Twitter / X": 127880,
        "Snapchat": 127872,
    },
    -1001687199609: {
        "MARKET CHAT": 1,
        "INSTAGRAM": 71892,
        "EXCHANGE SERVICE": 878160,
        "TELEGRAM": 74145,
        "Other services": 71899,
        "DISCORD": 74299,
        "TWITTER": 71893,
        "WHATSAPP": 107245,
        "TIKTOK": 71894,
        "YOUTUBE": 377367,
        "SNAPCHAP": 71922,
        "MINI GAMES": 878393,
        "PLAYSTATION": 878296,
    },
    -1002442347480: {
        "Discord": 3,
        "Instagram": 4,
        "Telegram": 2,
        "General": 1,
        "Services": 6,
        "Others": 5,
    },
    -1001825295385: None, # Simple Group
    -1002270409535: {
        "General": 1,
        "Unknown Network": 5,
        "Rules": 3,
        "Middleman": 6,
        "Discord": 16,
        "Telegram": 13,
        "Other accounts and Services": 19,
        "Instagram": 10,
        "Currency Exchange": 14,
        "X / Twitter": 17,
        "TikTok": 11,
        "YouTube": 18,
        "SnapChat": 12,
    },
    -1002000383834: {
        "️": 1,
        "Ad": 999280,
        "Rules": 8271,
        "Discord": 8264,
        "Instagram": 8266,
        "Exchange": 8269,
        "Telegram": 8263,
        "Other Service": 8268,
        "Tiktok": 8270,
        "Other Accounts": 28910,
        "Twitter X": 8265,
        "YouTube": 8665,
        "Join Logs": 268850,
    },
    -1002178340194: {
        "General": 1,
        "Chat Group": 12,
        "Instagram": 5,
        "WhatsApp": 11,
        "Other": 32,
        "Telegram": 4,
        "Tiktok": 31,
        "Discord": 10,
        "Twitter": 9,
        "YouTube": 6,
    },
    -1003254168777: None, # Simple Group
    -1002258810204: {
        "STOCKS CHANNEL": 1238646,
        "Telegram": 21,
        "Exchange Services": 30,
        "Tiktok": 33,
        "Discord": 20,
        "Other Services": 39,
        "Roblox": 42,
        "Instagram": 31,
        "Twitter": 23,
        "Facebook": 35,
        "Youtube": 22,
        "welcome": 1,
        "Steam": 32,
        "Snapchat": 27,
        "Gfx Services": 36,
        "Xbox": 29,
        "Twitch": 24,
        "Web Development": 37,
        "Minecraft": 26,
    },
    -1002011482119: {
        "Instagram": 79,
        "Telegram": 85,
        "Other Services": 83,
        "Discord": 5732,
        "Facebook": 82,
        "Twitter/X": 273,
        "Tiktok": 272,
        "Youtube": 5737,
        "Kick Handles": 5729,
        "Snapchat": 5735,
        "General": 1,
    },
    -1001836523109: {
        "General": 1,
        "Scammers": 20,
        "TOS": 11,
        "Tiktok": 30,
        "Other": 32,
        "Instagram": 28,
        "Telegram": 29,
        "Exchange": 31,
        "Chatroom": 25,
    },
    -1001505780126: None, # Simple Group
    -1001676369027: {
        "Anycomment": 1,
        "telegram": 120084,
        "instagram": 120080,
        "snapchat": 120075,
        "Tiktok": 120071,
        "Auctions": 120088,
    },
    -1002035477675: {
        "General": 1,
        "Chat": 14574,
        "Whatsaap": 14575,
        "Instagram": 14577,
        "Telegram": 14616,
        "Tik Tok": 14585,
        "Graphics": 15491,
        "Twitter": 14583,
        "Youtube": 14581,
        "Snapchat": 14579,
    },
    -1001594164440: None, # Simple Group
    -1001643734665: None, # Simple Group
    -1001497218938: None, # Simple Group
    -1001137547686: None, # Simple Group
    -1001255220369: None, # Simple Group
    -1001524426348: None, # Simple Group
    -1002465535730: {
        "General": 1,
        "Forum Rules": 19,
        "Expert Services": 32906,
        "Instagram": 3,
        "Other's": 16,
        "Discord": 14,
        "Telegram": 10,
        "Facebook": 892,
        "WhatsApp": 5,
        "Tik Tok": 7,
        "Twitter/X": 9,
        "Snapchat": 12,
    },
    -1001376968998: None, # Simple Group
    -1001301616226: None, # Simple Group
    -1001902360936: None, # Simple Group
    -1001535265112: None, # Simple Group
    -1001413969381: None, # Simple Group
    -1001804199224: None, # Simple Group
    -1001765993121: None, # Simple Group
    -1001260391401: None, # Simple Group
    -1001778593556: None, # Simple Group
    -1001363414411: None, # Simple Group
}