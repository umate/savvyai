import os
import logging
from dotenv import load_dotenv
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )

from telegram.ext import Updater, CommandHandler, Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Updater, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("/start command received")
    user = update.effective_user
    await update.message.reply_text(f"""Hey {user.first_name}!
I'm Savvy, your new chatbot buddy. Need a funny joke or a random fact? Just ask! I'm here to be your digital assistant, your AI pal, your pocket-sized problem solver. So, what can I do for you today?"""
                                    )


def main():
    logging.info("Starting SavvyAI Bot")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    application.run_polling()


if __name__ == '__main__':
    main()
