import os
import discord
import requests
from discord.ext import commands
from keep_alive import keep_alive

TOKEN = os.getenv("TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TOKEN or not GOOGLE_API_KEY:
    raise ValueError("Missing TOKEN or GOOGLE_API_KEY.")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": GOOGLE_API_KEY
}

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_val_reply(user_message):
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"You're Val, a girl with a naturally tsundere personality — playful, sometimes flustered, but realistic. Keep your tone casual and don't overdo it. Someone said to you: \"{user_message}\" — how do you respond?"
                    }
                ]
            }
        ]
    }

    try:
        res = requests.post(API_URL, headers=headers, json=payload)
        if res.status_code == 200:
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            return "Hmph... I'm not answering that right now."
    except Exception:
        return "Hmph... I'm not answering that right now."

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Streaming(
        name="Being cute? M-Me? You're dreaming..", url="https://twitch.tv/valbot"))

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    if bot.user.mentioned_in(message) or message.content.lower().startswith("val"):
        await message.channel.typing()
        reply = get_val_reply(message.content)
        await message.reply(reply)

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
