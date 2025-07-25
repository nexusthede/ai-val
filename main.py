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
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

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
    mentioned = bot.user.mentioned_in(message) or "val" in content

    if mentioned:
        await message.channel.typing()
        user_input = message.content

        async with aiohttp.ClientSession() as session:
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [{
                        "text": (
                            "You are Val, a playful tsundere girl. "
                            "Respond naturally and with subtle sass but kindness. "
                            f"User said: {user_input}"
                        )
                    }]
                }]
            }
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    try:
                        reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        # Remove repetitive or excessive sass lines manually if any
                        # You can also add filters here if needed
                        await message.reply(reply)
                    except Exception:
                        await message.reply("Ugh... that didn't make sense. Try again.")
                else:
                    await message.reply("Sorry, I'm not feeling chatty right now.")

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
