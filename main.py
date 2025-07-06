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

async def query_gemini_api(prompt: str):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
    }
    params = {
        "key": GOOGLE_API_KEY
    }
    json_payload = {
        "prompt": {
            "messages": [{"content": prompt, "author": "user"}]
        },
        "temperature": 0.7,
        "candidate_count": 1,
        "max_output_tokens": 256
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, params=params, json=json_payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                try:
                    return data["candidates"][0]["content"]
                except Exception:
                    return None
            else:
                return None

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.lower()
    mentioned = bot.user.mentioned_in(message) or "val" in content

    if mentioned:
        await message.channel.typing()
        prompt = message.content

        response = await query_gemini_api(prompt)
        if response:
            # Tsundere style: add some light sass randomly
            sass_phrases = [
                "Hmph! Don't get the wrong idea.",
                "Tch, what do you want now?",
                "Not that I care, but whatever.",
                "Ugh, you're so annoying sometimes.",
                "*crosses arms* Speak already."
            ]
            import random
            sass = random.choice(sass_phrases)
            reply = f"{sass}\n{response.strip()}"
            await message.reply(reply)
        else:
            await message.reply("Hmph... I'm not answering that right now.")

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
