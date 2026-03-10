🛡️ **Media Reporting Bot**
An asynchronous Telegram bot for structured media intake. It acts as a secure "tip-line" for newsrooms, community managers, or project leads, consolidating user reports into a single administrative channel.

🎯 **The Core**
The bot eliminates the chaos of direct messages by providing a centralized entry point for news and media.
- **Instant Forwarding:** Sends text, photos, videos, and voice messages directly to the admin.
- **User Logging:** Automatically registers users and interaction timestamps in a local SQLite3 database.
- **Media Backups:** Self-manages local directories for redundant media storage.

🛠 **Tech Stack**
**Engine:** Python 3.10+ / Aiogram 2.x (Asynchronous)
**Database:** SQLite3
**Security:** python-dotenv for environment secrets management

📦 **Quick Setup**
**Install dependencies:** pip install -r requirements.txt
**Configure environment:** Rename .env.example to .env and add your BOT_TOKEN and ADMIN_ID.
**Launch:** python main.py
