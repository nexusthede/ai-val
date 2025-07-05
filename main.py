import os
import discord
import aiohttp
from discord.ext import commands
from keep_alive import keep_alive

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TOKEN = os.getenv("TOKEN")

if not GOOGLE_API_KEY or not TOKEN:
    raise ValueError("GOOGLE_API_KEY and TOKEN environment variables must be set!")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": GOOGLE_API_KEY,
}

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateMessage"

TSUNDERE_SYSTEM_PROMPT = (
    "You are Val, a tsundere AI assistant. "
    "You are shy and a little mean but secretly kind and caring. "
    "Speak with playful irritation and affection, teasing but sweet."
)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Streaming(
        name="Being cute? M-Me? You're dreaming..", url="https://twitch.tv/valbot"
    ))

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.lower()
    mentioned = bot.user.mentioned_in(message) or "val" in content

    if mentioned:
        await message.channel.typing()

        # Google Gemini expects a 'messages' list of dicts with 'author' and 'content'
        payload = {
            "prompt": {
                "messages": [
                    {"author": "system", "content": TSUNDERE_SYSTEM_PROMPT},
                    {"author": "user", "content": message.content}
                ]
            },
            "temperature": 0.7,
            "candidateCount": 1,
            "maxOutputTokens": 200,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=HEADERS, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    try:
                        reply = data["candidates"][0]["content"].strip()
                        if reply:
                            await message.reply(reply)
                        else:
                            await message.reply("Hmph... whatever.")
                    except Exception:
                        await message.reply("Hmph... I’m not answering that right now.")
                else:
                    await message.reply(f"Hmph... I’m not answering that right now. (HF Error {resp.status})")

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
