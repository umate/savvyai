import os
import logging
import openai
import uuid
import random
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from pydub import AudioSegment


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
LOADING_MESSAGES = [
    "Almost there, just a sec!",
    "Loading...please wait patiently!",
    "Sit tight, we're working hard!",
    "Processing your request, standby!",
    "Don't panic, we're on it!",
    "Just a moment, please!",
    "Hold on, we're coming through!",
    "Be patient, we'll be quick!",
    "Processing...thank you for waiting!",
    "Our elves are working diligently!"
]

# COMPLETION_RESPONSE_MARKUP = ReplyKeyboardMarkup(
#     [[KeyboardButton("👍 thanks!"), KeyboardButton("👎 let's try again")]], resize_keyboard=True, one_time_keyboard=True,
# )
INTRO_MESSAGE_MARKDOWN = """Hello! I'm Savvy, your personal AI assistant. I'm here to help answer any questions you may have, just like Google, but better with less noise. Here are a few examples of things you can ask me:

- "What's a simple recipe for tacos?"
- "What are some things to see in Kyoto?"
- “10 Ideas for a Novel by William Shakespeare”
- "How do I change a tire?"
- "How do I say 'hello' in Spanish?"

Don't hesitate to ask me anything!"""


def _get_loading_message():
    return random.choice(LOADING_MESSAGES)


def ask_for_completion(prompt: str) -> str:
    logger.info("Calling completion API")
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a very helpful assistant that makes jokes from one in a while."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.25,
        max_tokens=256,
    )

    logger.info("Completion API response: %s", response.to_dict())

    return response.choices[0].message.content


# srart command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("/start command received")
    user = update.effective_user
    await update.message.reply_markdown(INTRO_MESSAGE_MARKDOWN)

    gif_file_object = open('assets/SavvyAI-Voice-Instruction-Demo.gif', 'rb')
    await update.message.reply_animation(
        gif_file_object, caption='By the way, you can also send a voice message instead of typing.')
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
    logging.info("Text message received handler")
    if not update.message.text or update.message.text == "":
        await update.message.reply_text("Oops, my bad, I didn't get that. Please try again.")
        return COMPLETION_PROMPT_STATE

    prompt = update.message.text
    await update.message.reply_text(_get_loading_message())

    output_text = ask_for_completion(prompt)
    await update.message.reply_markdown(output_text)

    return COMPLETION_PROMPT_STATE


async def voice_prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Voice message received handler")
    voice = update.message.voice
    voice_file = await voice.get_file()

    random_uuid = uuid.uuid4()
    ogg_filename = f"{str(random_uuid)}.ogg"
    mp3_filename = f"{str(random_uuid)}.mp3"

    logging.info("Downloading voice message to disk")
    await voice_file.download_to_drive(ogg_filename)
    ogg_audio = AudioSegment.from_file(ogg_filename, format="ogg")
    ogg_audio.export(mp3_filename, format="mp3")
    await update.message.reply_text("Transcribing voice message...")

    with open(mp3_filename, "rb") as audio_mp3:
        logging.info("Transcribing voice message with Whisper API")
        transcript = openai.Audio.transcribe("whisper-1", audio_mp3)
        logging.info("DONE: Transcribing voice message with Whisper API")

        logging.info("Removing temporary files")
        os.remove(ogg_filename)
        os.remove(mp3_filename)

        if not transcript.text or transcript.text == "":
            await update.message.reply_text("Oops, my bad, I didn't get that. Please try again.")
            return COMPLETION_PROMPT_STATE

        await update.message.reply_text("You said: " + transcript.text)
        await update.message.reply_text(_get_loading_message())

    output_text = ask_for_completion(transcript.text)
    await update.message.reply_markdown(output_text)

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
                           text_prompt_handler),
            MessageHandler(filters.VOICE, voice_prompt_handler),
        ],
        states={
            COMPLETION_PROMPT_STATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               text_prompt_handler),
                MessageHandler(filters.VOICE, voice_prompt_handler),
                MessageHandler(filters.COMMAND, text_prompt_fallback_handler)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
