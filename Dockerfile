FROM python:3.11.1-slim

RUN apt-get update && apt-get install -y ffmpeg

# Install pipenv
RUN pip install pipenv

# Set working directory
WORKDIR /app

# Copy files into container
COPY bot.py .
COPY Pipfile .
COPY Pipfile.lock .
COPY assets assets

# Install dependencies with pipenv
RUN pipenv install --deploy

# Run bot.py with pipenv
CMD ["pipenv", "run", "python", "bot.py"]