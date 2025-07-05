import os
import discord
import aiohttp
from discord.ext import commands
from keep_alive import keep_alive  # if you want uptime monitoring via keep_alive.py

TOKEN = os.getenv("TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

if not TOKEN or not HF_TOKEN:
    raise ValueError("TOKEN and HF_TOKEN environment variables must be set!")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Streaming(
        name="love my nonchalant king Nexus ❤️", url="https://twitch.tv/valbot"))

async def query_hf_model(user_input):
    url = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"inputs": user_input}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                # data is usually a list with generated text
                if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                    return data[0]["generated_text"]
                else:
                    return None
            else:
                return f"Hmph... I’m not answering that. (HuggingFace Error {resp.status})"

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.lower()
    mentioned = bot.user.mentioned_in(message) or "val" in content

    if mentioned:
        async with message.channel.typing():
            reply = await query_hf_model(message.content)
            if reply:
                await message.reply(reply)
            else:
                await message.reply("Hmph... not in the mood.")

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
