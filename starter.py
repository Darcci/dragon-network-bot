from typing import Optional, List, NoReturn
import discord
from discord.ext import commands
from os.path import isfile, join
from logging import exception
from os import listdir
from functions import *
from config import BOT_CONFIG, GUILD_IDS, ALLOWED_GUILDS
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

log_dir: Path = Path("logs")
log_dir.mkdir(exist_ok=True)

# Logger Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File Handler
file_handler = RotatingFileHandler(
    filename=log_dir / "bot.log",
    maxBytes=2_000_000,
    backupCount=3,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

intents: discord.Intents = discord.Intents.all()
intents.message_content = True

bot: commands.Bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(BOT_CONFIG["prefix"]),
    help_command=None,
    intents=intents,
    application_id=BOT_CONFIG["application_id"]
)

async def load_extensions() -> None:
    """Lädt alle Extensions aus dem Extensions-Ordner."""
    path: str = "Extensions"
    try:
        extensions: List[str] = [
            f for f in listdir(path) 
            if f.endswith('.py')
        ]
        
        for extension in extensions:
            try:
                extension_name: str = f"{path}.{extension[:-3]}"
                await bot.load_extension(extension_name)
                logger.info(f"Extension geladen: {extension_name}")
            except Exception as e:
                logger.error(
                    f"Fehler beim Laden der Extension {extension}: {str(e)}", 
                    exc_info=True
                )
    except Exception as e:
        logger.critical(f"Fataler Fehler beim Laden der Extensions: {str(e)}", exc_info=True)
        sys.exit(1)

@bot.event
async def on_ready() -> None:
    try:
        # Lade zuerst alle Extensions
        await load_extensions()
        
        # Sync die Commands mit Discord - mit Entry Point Handling
        for guild_name, guild_id in GUILD_IDS.items():
            try:
                guild = discord.Object(id=int(guild_id)) 
                bot.tree.copy_global_to(guild=guild)
                await bot.tree.sync(guild=guild)
                logger.info(f"Commands erfolgreich zu Guild '{guild_name}' (ID: {guild_id}) gesynct!")
            except Exception as e:
                logger.error(f"Fehler beim Syncen der Commands für Guild '{guild_name}': {str(e)}", exc_info=True)
        
        await bot.change_presence(
            status=discord.Status.online, 
            activity=discord.Activity(
                type=discord.ActivityType.playing, 
                name=BOT_CONFIG["status"]
            )
        )
    except Exception as e:
        logger.error(f"Fehler in on_ready: {str(e)}", exc_info=True)

def main() -> NoReturn:
    try:
        bot.run(BOT_CONFIG["token"])
    except Exception as e:
        logger.critical(f"Bot konnte nicht gestartet werden: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
