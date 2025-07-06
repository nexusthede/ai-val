import os
import discord
import aiohttp
from discord.ext import commands
from keep_alive import keep_alive

TOKEN = os.getenv("TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TOKEN or not GOOGLE_API_KEY:
    raise ValueError("TOKEN and GOOGLE_API_KEY environment variables must be set!")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TSUNDERE_SYSTEM_PROMPT = (
    "You are Val, a tsundere AI assistant. "
    "You are sassy, sarcastic, and shy but secretly kind."
)

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateText"
HEADERS = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": GOOGLE_API_KEY,
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Streaming(
        name="Being cute? M-Me? You're dreaming..", url="https://twitch.tv/valbot"))

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content_lower = message.content.lower()
    if bot.user.mentioned_in(message) or "val" in content_lower:
        await message.channel.typing()

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

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, headers=HEADERS, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data.get("candidates", [{}])[0].get("content", "").strip()
                        if reply:
                            await message.reply(reply)
        except Exception:
            pass  # silently ignore errors

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
