import discord
import os
import aiohttp
from keep_alive import keep_alive
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CHANNELS = []  # Can leave empty for all channels

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name="Tch... I hate ducks 🦆", url="https://twitch.tv/tsundereval"))
    print(f"💖 Val is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if CHANNELS and message.channel.id not in CHANNELS:
        return

    if "val" in message.content.lower() or bot.user in message.mentions:
        await message.channel.typing()
        prompt = message.content.strip()
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": f"{prompt}\nTsundere girl Val:"}

        async with aiohttp.ClientSession() as session:
            async with session.post("https://api-inference.huggingface.co/models/facebook/blenderbot-3B", headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data.get("generated_text", "Hmph... I don’t feel like talking.")
                else:
                    reply = f"Hmph... I’m not answering that. (Hugging Face Error {resp.status})"

        await message.reply(reply)

    await bot.process_commands(message)
