import os
import logging
import datetime
import openai
import redis
import math
import uuid
import random
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from pydub import AudioSegment


from telegram.ext import (CommandHandler, Application, CommandHandler,
                          ContextTypes, MessageHandler, filters, ConversationHandler)

from utils import (
    check_token_count_allowance,
    update_token_count_allowance,
    check_transcription_allowance,
    update_transaction_allowance,
    get_token_count_estimate,
)

from constants import (
    INTRO_MESSAGE_MARKDOWN,
    DAILY_LIMIT_REACHED_ERROR_MESSAGE,
    LOADING_MESSAGES,
)

COMPLETION_PROMPT_STATE = range(1)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

OPENAI_MODEL = "gpt-3.5-turbo"

# initiating services
openai.api_key = OPENAI_API_KEY
redis_client = redis.from_url(REDIS_URL)


# bot handlers
def _get_loading_message():
    return random.choice(LOADING_MESSAGES)


def ask_for_completion(prompt: str, telegram_user_id: int) -> str:
    logger.info("checking for token allowance")
    token_count_estimate = get_token_count_estimate(prompt)
    if not check_token_count_allowance(redis_client, telegram_user_id, token_count_estimate):
        logger.info("Token allowance exceeded for user ID: %s",
                    telegram_user_id)
        return DAILY_LIMIT_REACHED_ERROR_MESSAGE

    logger.info("Calling completion API for user ID: %s", telegram_user_id)
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a very helpful assistant that makes jokes from one in a while."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.25,
        max_tokens=256,
    )

    response_content = response.choices[0].message.content

    total_token = response.usage['total_tokens']
    logger.info(
        f"Completion API call completed. Tokens used: {total_token}")

    update_token_count_allowance(redis_client, telegram_user_id, total_token)

    return response_content


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

    telegram_user_id = update.message.from_user.id

    prompt = update.message.text
    await update.message.reply_text(_get_loading_message())

    output_text = ask_for_completion(prompt, telegram_user_id)
    await update.message.reply_markdown(output_text)

    return COMPLETION_PROMPT_STATE


async def voice_prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Voice message received handler")
    telegram_user_id = update.message.from_user.id
    voice = update.message.voice
    voice_file = await voice.get_file()

    random_uuid = uuid.uuid4()
    ogg_filename = f"voice/{str(random_uuid)}.ogg"
    mp3_filename = f"voice/{str(random_uuid)}.mp3"

    logging.info("Downloading voice message to disk")
    await voice_file.download_to_drive(ogg_filename)
    ogg_audio = AudioSegment.from_file(ogg_filename, format="ogg")
    duration_seconds = math.ceil(ogg_audio.duration_seconds)
    logger.info(f"Voice message duration: {duration_seconds} seconds")

    if not check_transcription_allowance(
            redis_client, telegram_user_id, duration_seconds):
        os.remove(ogg_filename)
        await update.message.reply_text(DAILY_LIMIT_REACHED_ERROR_MESSAGE)

        return COMPLETION_PROMPT_STATE

    update_transaction_allowance(
        redis_client, telegram_user_id, duration_seconds)

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

    output_text = ask_for_completion(transcript.text, telegram_user_id)
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
