from telethon import TelegramClient, events
from telethon.tl.functions.contacts import GetContactsRequest
from dotenv import load_dotenv
from openai import OpenAI
import asyncio
import random
import os
import json
import sys

# ========== Path Utility for PyInstaller ==========
def resource_path(relative_path):
    """ Get path to resource, works for dev and PyInstaller .exe """
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)


# ========== Config and Data Files ==========
ENV_FILE = ".env"
STRATEGIES_FILE = resource_path("strategies.json")
CONVERSATIONS_FILE = "conversations.json"


# ========== Environment Setup ==========
def create_env():
    print("Let's set up your API credentials.")
    api_id = input("Enter your Telegram API ID: ").strip()
    api_hash = input("Enter your Telegram API Hash: ").strip()
    session_name = input("Enter a name for your session (default: my_session): ").strip() or "my_session"

    with open(ENV_FILE, 'w') as f:
        f.write(f"""API_ID={api_id}\nAPI_HASH={api_hash}\nSESSION_NAME={session_name}""")
    print("✅ Created .env file with your credentials.")

if not os.path.exists(ENV_FILE):
    create_env()

if not os.path.exists(CONVERSATIONS_FILE):
    with open(CONVERSATIONS_FILE, 'w') as f:
        json.dump({}, f, indent=4)

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")

ai_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)


# ========== Memory ==========
conversations = {}
contacts = set() # IDs of users you've already sent a message to

# ========== Helpers ==========
def load_json(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def load_strategies():
    if os.path.exists(STRATEGIES_FILE):
        with open(STRATEGIES_FILE, 'r') as f:
            return json.load(f)

def get_user_context(user_id):
    user_id_str = str(user_id)
    if user_id_str not in conversations:
        strategy = random.choice(load_strategies())
        strategy += "\n\nKeep the conversation going and be attentive to what the other person is saying. You must always respond in a friendly and engaging manner. Try to sound human; emojis are good, but don't overuse them. Vary the length of your replies, but you must *strictly* keep them under 200 characters."
        conversations[user_id_str] = {
            'strategy': strategy,
            'messages': [{"role": "system", "content": strategy}]
        }
        save_json(CONVERSATIONS_FILE, conversations)
    return conversations[user_id_str]

def get_ai_reply(messages):
    MAX_MESSAGES = 100
    if len(messages) > MAX_MESSAGES:
        messages = [messages[0]] + messages[-(MAX_MESSAGES - 1):]

    response = ai_client.chat.completions.create(
        model="mistral",
        messages=messages,
        temperature=1.2
    )
    return response.choices[0].message.content

async def build_contact_cache(tg_client):
    print("🧑‍💻 Loading contacts...")
    result = await tg_client(GetContactsRequest(hash=0))
    for contact in result.users:
        contacts.add(contact.id)
    print(f"🧑‍💻 Found {len(contacts)} contacts. I won't reply to messages from them!")

# ========== Main Logic ==========
async def main():
    global conversations
    conversations = load_json(CONVERSATIONS_FILE)

    tg_client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    @tg_client.on(events.NewMessage(incoming=True))
    async def handle_new_message(event):
        sender = await event.get_sender()
        user_id = sender.id

        if not event.is_private:
            return  # Ignore non-private messages
        
        if user_id in contacts:
            return  # Ignore messages from your contacts
        
        print(f"🧑‍💻 New message from user {user_id}")

        # Load or initialize conversation with a strategy
        context = get_user_context(user_id)
        messages = context['messages']
        user_text = event.raw_text.strip()
        messages.append({"role": "user", "content": user_text})

        try:
            reply_text = get_ai_reply(messages)
        except Exception as e:
            print(f"⚠️ Error generating AI reply: {e}")
            return

        messages.append({"role": "assistant", "content": reply_text})
        conversations[str(user_id)]["messages"] = messages
        save_json(CONVERSATIONS_FILE, conversations)

        await event.reply(reply_text)
        print(f"🧑‍💻 I've replied to user {user_id} for you!")
    
    await tg_client.start()
    await build_contact_cache(tg_client)
    print("🧑‍💻 Receptionist is ready to respond to messages!")
    await tg_client.run_until_disconnected()

# ========== Run ==========
if __name__ == "__main__":
    asyncio.run(main())