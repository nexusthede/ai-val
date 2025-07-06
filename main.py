import os
import discord
import requests
from flask import Flask
from threading import Thread
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TOKEN or not GOOGLE_API_KEY:
    raise ValueError("Missing environment variables!")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)

@app.route("/")
def home():
    return "Val is online."

def keep_alive():
    Thread(target=lambda: app.run(host="0.0.0.0", port=8080)).start()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(
        name="Being cute? M-Me? You're dreaming..",
        url="https://twitch.tv/valbot"
    ))
    print(f"Logged in as {bot.user}")

def generate_val_response(user_input):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GOOGLE_API_KEY
    }
    data = {
        "contents": [{
            "parts": [{
                "text": f"You're Val, a naturally tsundere girl who's flustered but realistic. Reply naturally to this: {user_input}"
            }]
        }]
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=10)
        if res.status_code == 200:
            out = res.json()
            return out["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return None

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    if bot.user.mentioned_in(message) or "val" in message.content.lower():
        await message.channel.typing()
        reply = generate_val_response(message.content)
        if reply:
            await message.reply(reply)
        else:
            await message.reply("...ugh. Not answering that right now.")

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
