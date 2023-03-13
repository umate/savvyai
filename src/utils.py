
from redis import Redis
import datetime

DAILY_USER_TOKEN_LIMIT = 10_000
DAILY_USER_TRANSCRIPTION_LIMIT_SECONDS = 180
WORDS_IN_TOKEN_AVERAGE = 1/0.75


def _get_gpt_token_count_key(user_id: int) -> str:
    """Returns the key name for the token count for the given user."""
    now = datetime.datetime.now()
    return f'gpt:{user_id}:{now.date()}'


def get_token_count_estimate(promt: str) -> int:
    """Returns the number of tokens used for the given prompt."""
    return int(len(promt.split()) / WORDS_IN_TOKEN_AVERAGE)


def check_token_count_allowance(redis_client: Redis, user_id: int, new_tokens_requested: int) -> bool:
    """Checks if the user has enough token allowance to make a request."""

    key_name = _get_gpt_token_count_key(user_id)
    total_tokens = redis_client.get(key_name)
    if total_tokens is None:
        return True

    new_total_tokens = int(total_tokens) + new_tokens_requested

    return new_total_tokens <= DAILY_USER_TOKEN_LIMIT


def update_token_count_allowance(redis_client: Redis, user_id: int, new_tokens_requested: int) -> bool:
    """Checks if the user has enough tokens to make a request."""

    now = datetime.datetime.now()
    key_name = _get_gpt_token_count_key(user_id)

    total_tokens = redis_client.get(key_name)
    if total_tokens is None:
        redis_client.set(key_name, 0)
        total_tokens = 0

    new_total_tokens = int(total_tokens) + new_tokens_requested

    # increment the token count
    total_tokens = redis_client.incr(key_name, new_tokens_requested)

    # set the expiration time to the end of the day
    expiration_time = datetime.datetime.combine(now.date(), datetime.time.max)
    redis_client.expireat(key_name, int(expiration_time.timestamp()))

    return True


def _get_whisper_voice_key(user_id: int) -> str:
    """Returns the key name for the transacripted seconds count for a given user."""
    now = datetime.datetime.now()
    return f'whisper:{user_id}:{now.date()}'


def check_transcription_allowance(redis_client: Redis,  user_id: int, new_voice_in_seconds: int) -> bool:
    """Checks if the user is allowed to user Whisper API."""

    key_name = _get_whisper_voice_key(user_id)
    total_seconds = redis_client.get(key_name)
    if total_seconds is None:
        return True

    new_total_seconds = int(total_seconds) + new_voice_in_seconds

    return new_total_seconds <= DAILY_USER_TRANSCRIPTION_LIMIT_SECONDS


def update_transaction_allowance(redis_client: Redis, user_id: int, new_voice_in_seconds: int) -> bool:
    """Updates the number of seconds of voice transcribed for the user per day."""

    now = datetime.datetime.now()
    key_name = _get_whisper_voice_key(user_id)
    total_seconds = redis_client.get(key_name)
    if total_seconds is None:
        redis_client.set(key_name, 0)
        total_seconds = 0

    new_total_seconds = int(total_seconds) + new_voice_in_seconds

    # increment the token count
    redis_client.incr(key_name, new_total_seconds)

    # set the expiration time to the end of the day
    expiration_time = datetime.datetime.combine(now.date(), datetime.time.max)
    redis_client.expireat(key_name, int(expiration_time.timestamp()))

    return True
