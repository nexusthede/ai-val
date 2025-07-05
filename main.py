import os
import discord
import aiohttp
import json
from discord.ext import commands
from keep_alive import keep_alive

TOKEN = os.getenv("TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TOKEN or not GOOGLE_API_KEY:
    raise ValueError("TOKEN and GOOGLE_API_KEY must be set as environment variables.")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Streaming(
        name="Being cute? M-Me? You're dreaming...", url="https://twitch.tv/valbot"))

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.lower()
    mentioned = bot.user.mentioned_in(message) or "val" in content

    if mentioned:
        await message.channel.typing()
        user_input = message.content

        prompt = (
            "You are Val, a tsundere AI girl. Speak with a bratty, shy, sarcastic, but secretly kind attitude. "
            f"Someone said: \"{user_input}\"\nRespond like a real tsundere girl:"
        )

        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "X-goog-api-key": GOOGLE_API_KEY
            }
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }

            async with session.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
                headers=headers, json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    try:
                        reply = data['candidates'][0]['content']['parts'][0]['text']
                        await message.reply(reply.strip())
                    except Exception:
                        await message.reply("Hmph... I'm not answering that right now.")
                else:
                    await message.reply("Hmph... I'm not answering that right now.")

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
