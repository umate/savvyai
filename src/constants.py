# telegram bot setup
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

DAILY_LIMIT_REACHED_ERROR_MESSAGE = f"""

🚨 This bot is powered by OpenAI paid API. Savvy is a non-profit project, and we try to limit the number of API calls per day to 10k tokens and 3 minutes of voice commands.

😢 Unfortunately, you have reached your daily limit, please come back tomorrow.
💚 Thank you for your understanding!
"""
