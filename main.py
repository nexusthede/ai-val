import os
import discord
import aiohttp
from discord.ext import commands
from keep_alive import keep_alive

TOKEN = os.getenv("TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not TOKEN or not GOOGLE_API_KEY:
    raise ValueError("TOKEN and GOOGLE_API_KEY must be set!")

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

        try:
            response = await get_gemini_response(user_input)
            await message.reply(response or "Hmph... I'm not answering that right now.")
        except Exception as e:
            print("Error:", e)
            await message.reply("Hmph... I'm not answering that right now.")

    await bot.process_commands(message)

async def get_gemini_response(user_input):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GOOGLE_API_KEY
    }
    data = {
        "contents": [{
            "parts": [{
                "text": f"You are Val, a sassy and sweet tsundere girl. Respond naturally with a playful but realistic tone. Here's what the user said: '{user_input}'"
            }]
        }]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                try:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                except:
                    return None
            else:
                return None
