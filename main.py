import os
import discord
import aiohttp
from discord.ext import commands
from flask import Flask
from threading import Thread

TOKEN = os.getenv("TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TOKEN or not GOOGLE_API_KEY:
    raise ValueError("TOKEN and GOOGLE_API_KEY environment variables must be set!")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Flask keep alive
app = Flask("")

@app.route("/")
def home():
    return "Val is alive!"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Streaming(
        name="love my nonchalant king Nexus ❤️", url="https://twitch.tv/valbot"))

async def query_google_ai(user_input):
    url = "https://generativelanguage.googleapis.com/v1beta2/models/chat-bison-001:generateMessage"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GOOGLE_API_KEY}",
    }
    # Tsundere personality prompt with user input
    prompt = (
        "You are Val, a tsundere AI bot. "
        "You act prickly, sarcastic, but secretly kind and caring. "
        "Reply to the user in a tsundere style.\n"
        f"User: {user_input}\n"
        "Val:"
    )
    payload = {
        "prompt": {
            "messages": [
                {"author": "system", "content": "You are a helpful assistant."},
                {"author": "user", "content": prompt}
            ]
        },
        "temperature": 0.7,
        "candidate_count": 1,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                try:
                    return data["candidates"][0]["content"].strip()
                except (KeyError, IndexError):
                    return None
            else:
                return None

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content_lower = message.content.lower()
    mentioned = bot.user.mentioned_in(message) or "val" in content_lower

    if mentioned:
        async with message.channel.typing():
            response = await query_google_ai(message.content)
            if response:
                await message.reply(response)
            else:
                await message.reply("Hmph... I'm not answering that right now.")

    await bot.process_commands(message)

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
