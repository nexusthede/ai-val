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

# Natural tsundere prompt
SYSTEM_PROMPT = {
    "parts": [{
        "text": (
            "You are Val, a realistic tsundere girl in a Discord chat. "
            "You sound like a real person—moody, flustered, sarcastic at times, but never fake. "
            "You don’t use asterisks, emotes, or roleplay. Be blunt, sometimes cold, but caring deep down. "
            "Respond in 1-2 casual sentences max, natural tone. Don’t act overly anime or childish."
        )
    }],
    "role": "user"
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

    content = message.content.lower()
    if bot.user.mentioned_in(message) or "val" in content:
        await message.channel.typing()

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": GOOGLE_API_KEY
        }
        payload = {
            "contents": [
                SYSTEM_PROMPT,
                {
                    "parts": [{"text": message.content}]
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    try:
                        reply = data["candidates"][0]["content"]["parts"][0]["text"]
                        await message.reply(reply.strip())
                    except Exception:
                        await message.reply("...Tch. I’m not answering that right now.")
                else:
                    await message.reply("...Tch. I’m not answering that right now.")

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
