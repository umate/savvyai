import os
import logging
import openai
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup


# try:
#     from telegram import __version_info__
# except ImportError:
#     __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

# if __version_info__ < (20, 0, 0, "alpha", 1):
#     raise RuntimeError(
#         f"This example is not compatible with your current PTB version {TG_VER}. To view the "
#         f"{TG_VER} version of this example, "
#         f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
#     )

from telegram.ext import (CommandHandler, Application, CommandHandler,
                          ContextTypes, MessageHandler, filters, ConversationHandler)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

OPENAI_MODEL = "gpt-3.5-turbo"

# telegram bot setup
COMPLETION_PROMPT_STATE = range(1)


# srart command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("/start command received")
    user = update.effective_user
    await update.message.reply_text(f"""Hey {user.first_name}!
I'm Savvy, your new chatbot buddy. Need a funny joke or a random fact? Just ask! I'm here to be your digital assistant, your AI pal, your pocket-sized problem solver. So, what can I do for you today?"""
                                    )
    return COMPLETION_PROMPT_STATE


# cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


# completion prompt handler
async def text_prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("COMPLETION_PROMPT_STATE: Message received")
    prompt = update.message.text
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=256,
    )
    output_text = response.choices[0].message.content
    await update.message.reply_text(output_text)

    return COMPLETION_PROMPT_STATE


async def text_prompt_fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("COMPLETION_PROMPT_STATE: Fallback message received")
    await update.message.reply_text("Sorry, this command is not supported. Please ask me anything in text or record a voice message.")
    return COMPLETION_PROMPT_STATE


def main():
    logging.info("Starting SavvyAI Bot")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND,
                           text_prompt_handler)
        ],
        states={
            COMPLETION_PROMPT_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               text_prompt_handler),
                MessageHandler(filters.COMMAND, text_prompt_fallback_handler)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
