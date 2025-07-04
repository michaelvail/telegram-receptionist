# 🧑‍💻 Telegram Receptionist

This is a friendly AI-powered receptionist bot for Telegram. It uses [Ollama](https://ollama.com/) to generate short, engaging replies. I created this bot because I receive a lot of spam and messages from scammers, and engaging with them brings whimsy to my life.

## Features

- 🧠 Uses a rotating set of strategies to guide responses
- 🤝 Replies only to users **not in your Telegram contacts**
- 💬 Keeps responses under **200 characters**
- 🔌 Runs locally using [Ollama](https://ollama.com/) — no OpenAI key required

## Requirements

- Python 3.8+
- Telegram API credentials
- [Ollama](https://ollama.com/) installed and running locally
- The `mistral` model pulled via Ollama

## Setup

### Get Telegram API credentials
1. Go to https://my.telegram.org and sign in.
2. Find API development tools and create a new application (the info doesn't matter).

### Set up Ollama
1. Install [Ollama](https://ollama.com/).
2. Open a command prompt and run `ollama pull mistral`.
3. Run `ollama run mistral`.

### Installation (Windows)
1. Download the latest release `.exe` from Releases and run it.
2. Follow the instructions.
