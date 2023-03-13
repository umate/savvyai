![](/assets/readme-bot-intro.png)

<div align="center">

[Play with a hosted SavvyAI Bot](https://t.me/savvyai_bot)

</div>

# SavvyAI Telegram Bot

SavvyAI is an open source Telegram bot that let's non-technical people play with the latest LLMs available.
SavvyAI is intended to be a non-profit project aiming to give people access to recently released OpenAI GPT-3.5-turbo model in a form a of a [Telegram](https://telegram.org/) bot.

The project can be run locally, or you can try a cloud version that I am running on Render (http://render.com/) [here](https://t.me/savvyai_bot). Each user is given 10,000 free tokens per day to try out the bot, along with 3 minutes of voice transcription.

Please note that the bot is still in development, and it may not work as expected all the time. We are doing our best to ensure that the bot does not store any user data on your end, but please do not send any sensitive data just to be safe.

## Features

[x] Chat completion using gpt-3.5-turbo model
[x] Voice transcription using Whisper API and completion
[x] Daily rate limiting for both completion and Whisper API endpoints
[ ] Ability to keep context between interaction. The bot is only able to process atomic requests now.

## Getting Started

To SavvyAI locally, follow these steps:

1. Clone the repository
2. Install [pipenv](https://pipenv.pypa.io/en/latest/index.html) and run `pipenv install` to install dependencies
3. Create a a new bot on Telegram and get the API token from [BotFather](https://t.me/botfather)
4. Create an OpenAI Account and get the API key from [OpenAI Dashboard](https://platform.openai.com/account/api-keys)
5. `cp .env.sample .env` and fill in the required values
6. Make sure you have running [Redis](https://redis.io/) server, the default url is `redis://localhost:6379`
7. Start the bot with `pipenv run python src/bot.py`

## Usage

Just type any questions or query you want to ask the assistant and it will try to answer it.
You can also use the bot to transcribe your voice messages and complete them using a voice recording feature in Telegram located in the bottom right corner of the chat.

## Contributing

Contributions to SavvyAI are welcome! To contribute, follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them
4. Push your changes to your fork
5. Create a pull request

## License

SavvyAI is released under the [MIT License](https://opensource.org/licenses/MIT).
