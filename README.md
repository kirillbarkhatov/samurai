# 👹 Samurai Telegram Bot
![Samurai Telegram Bot](https://i.imgur.com/S9BPDMt.jpeg "te")
Simple, yet effective **auto-moderator bot for telegram**.  
With reports, logs, profanity filter, anti-spam AI, NSFW detection, reputation system and more :3

## What samurai do?

- **Anti-Profanity**: Automatically detects and removes messages containing profanity (Russian/English)
- **Anti-Spam**: ML-based spam detection for new users
- **NSFW Detection**: Profile photo analysis for NSFW accounts
- **Reputation System**: Users gain reputation through positive participation
- **Report System**: Users can report messages to admins
- **Scheduled Announcements**: Periodic automated messages

## Code Hierarchy

```
samurai/
├── bot.py                 # Main entry point
├── config/
│   ├── __init__.py
│   ├── settings.py        # Pydantic configuration
│   └── config.toml        # Configuration file
├── core/
│   ├── __init__.py
│   └── i18n.py            # Fluent internationalization
├── db/
│   ├── __init__.py
│   ├── database.py        # Database setup
│   └── models/
│       ├── member.py      # Member model
│       └── spam.py        # Spam record model
├── filters/
│   ├── is_owner.py
│   ├── is_admin.py
│   ├── throttle.py
│   └── .. other useful filters
├── handlers/
│   ├── admin_actions.py   # Ban/unban commands
│   ├── callbacks.py       # Inline button handlers
│   ├── exceptions.py      # Error handler
│   ├── group_events.py    # Main message processing
│   ├── personal_actions.py# Ping, profanity check
│   └── user_actions.py    # Report command
├── locales/
│   ├── en/
│   │   ├── strings.ftl    # English translations
│   │   └── announcements.ftl
│   └── ru/
│       ├── strings.ftl    # Russian translations
│       └── announcements.ftl
├── middlewares/
│   ├── __init__.py
│   ├── throttling.py      # Middleware for rate limiting
│   └── i18n.py            # I18n middleware
├── services/
│   ├── announcements.py   # Scheduled announcements
│   ├── cache.py           # LRU caching
│   ├── gender.py          # Gender detection
│   ├── nsfw.py            # NSFW detection
│   ├── profanity.py       # Profanity detection
│   ├── healthcheck.py     # Healthcheck server for containers orchestration
│   ├── ml_manager.py      # Unloads unused ML models from memory after some time
│   └── spam.py            # Spam detection
├── utils/
│   ├── helpers.py         # Utility functions
│   ├── enums.py           # Some useful enums to keep the codebase consistent
│   └── localization.py    # Localization exports
├── libs/                  # External libraries (censure, gender_extractor)
├── ruspam_model/          # ML model for spam detection
├── requirements.txt
├── Dockerfile
├── config.py              # Configuration of the bot
├── db_init.py             # Use this to initialize your database tables
└── .env.example
```

## Internationalization (i18n)

The bot uses [Project Fluent](https://projectfluent.org/) for translations.

### Usage in handlers

```python
# Method 1: Import _ function directly
from core.i18n import _

async def handler(message: Message) -> None:
    text = _("error-no-reply")
    await message.reply(text)

# Method 2: Use i18n from middleware (user's locale)
async def handler(message: Message, i18n: Callable) -> None:
    text = i18n("error-no-reply")
    await message.reply(text)

# With variables
text = _("report-message", date="2024-01-01", chat_id="123", msg_id="456")
```

### Adding new translations

1. Create/edit `.ftl` files in `locales/{lang}/`
2. Use hyphenated keys: `error-no-reply`
3. Variables use `{ $var }` syntax

Example `locales/ru/strings.ftl`:
```fluent
error-no-reply = Эта команда должна быть ответом на сообщение!
report-message = 👆 Отправлено { $date }
    <a href="https://t.me/c/{ $chat_id }/{ $msg_id }">Перейти</a>
```

## Installation

### Prerequisites

- Python 3.11+ is required
- Bot token from [@BotFather](https://t.me/BotFather)

### Setup process

1. Clone the repository

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```

4. Configure `config.toml` with your group IDs and other settings how you like

5. Run the bot:
   ```bash
   python bot.py
   ```

6. Enjoy!

### Environment Variables in Production

For production deployments, you can also set environment variables directly instead of using `.env` file:

```bash
# Export variables directly
export BOT_TOKEN="your_bot_token"
export BOT_OWNER="your_user_id"
export GROUPS_MAIN="-1001234567890"
export DB_URL="sqlite:///./samurai.db"

# Or pass them inline
BOT_TOKEN="..." BOT_OWNER="..." python bot.py
```

For **systemd** services, add them to the unit file:
```ini
[Service]
Environment="BOT_TOKEN=your_token"
Environment="BOT_OWNER=123456789"
```

For **Docker**, use `-e` flags or `--env-file`:
```bash
docker run -e BOT_TOKEN="..." -e BOT_OWNER="..." samurai-bot
# or
docker run --env-file .env samurai-bot
```

### Database Initialization

`db_init.py` supports safe and destructive modes:

```bash
# Safe: only create missing tables
python db_init.py

# Destructive: drop all tables and recreate
python db_init.py --reset --yes
```

For SQLite paths, the script auto-creates parent directories and DB file.

### Docker

```bash
docker build -t samurai-bot .
docker run -d --name samurai-bot -v $(pwd)/config.toml:/app/config.toml samurai-bot
```

### Docker Compose

`docker-compose.yml` stores SQLite in a Docker named volume (`samurai_data`) and
sets `DB_URL` automatically by default:

```bash
docker compose up -d
docker compose exec samurai python db_init.py
```

Reset DB in Docker (destructive):

```bash
docker compose exec samurai python db_init.py --reset --yes
```

## RAM usage

Currently bot uses ~800mb of RAM for ML models and for data caching.  
~~Probably we could reduce ML models RAM usage by implementing ONNX runtime models, but that's plans for future updates.~~  
That ain't worked, the only viable solution would be to quantize the models :3

For now, if your server doesn't handle and the process being killed with *Out of memory (`dmesg | grep -i "killed process"`)*,
simple solution is to add swap:
```bash
# Create 2GB swap file
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram bot token |
| `BOT_OWNER` | Owner's Telegram user ID |
| `GROUPS_MAIN` | Main group chat ID __(can be a comma separated list)__ |
| `GROUPS_REPORTS` | Reports group chat ID |
| `GROUPS_LOGS` | Logs group chat ID |
| `LINKED_CHANNEL` | Linked channel ID __(can be a comma separated list)__ |
| `DB_URL` | Database URL |

## Built-in Commands

### User Commands

| Command | Description |
|---------|-------------|
| `!rules` / `/rules` | Request the chat rules |
| `!report` / `/report` | Report a message (reply) |
| `!me` / `!info` | Show user info |
| `!бу` | Fun command (bot pretends to be scared lol) |
| `@admin` | Call admin attention |

### Admin Commands

| Command | Description |
|---------|-------------|
| `!ban` | Ban user (reply) |
| `!unban` | Unban user (reply) |
| `!ping` | Check bot status |
| `!prof <text>` | Check text for profanity |

### Owner Commands

| Command | Description |
|---------|-------------|
| `!spam` | Mark message as spam (reply) |
| `!reward <points>` | Add reputation points |
| `!punish <points>` | Remove reputation points |
| `!setlvl <level>` | Set user level |
| `!rreset` | Reset user reputation |
| `!msg <text>` | Send message from bot |
| `!chatid` | Get current chat ID |
| `!reload` | Reload announcements from localization files |
| `!log <text>` | Write test log |

## External Libraries

The bot uses two external libraries in the `libs/` folder:

- **censure**: Russian/English profanity detection
- **gender_extractor**: Gender detection from names

## Credits
https://github.com/masteroncluster/py-censure - Profanity filter we used as a base  
https://github.com/MasterGroosha/telegram-report-bot - Reports system we used as a base  
https://huggingface.co/RUSpam/spam_deberta_v4 - Anti-Spam AI model we used as a base  
https://github.com/wwydmanski/gender-extractor - Gender detection we used as a base  
https://huggingface.co/prithivMLmods/siglip2-x256-explicit-content - Our current NSFW detection model

## Author of Samurai

(C) 2026 Abraham Tugalov
