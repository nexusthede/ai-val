import os
import discord
import aiohttp
from discord.ext import commands
from keep_alive import keep_alive  # if you use uptime monitor

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
        name="love my nonchalant king Nexus ❤️",
        url="https://twitch.tv/valbot"
    ))

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.lower()
    mentioned = bot.user.mentioned_in(message) or "val" in content

    if mentioned:
        async with message.channel.typing():
            user_input = message.content

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {HF_TOKEN}",
                    "Content-Type": "application/json"
                }
                payload = {"inputs": f"User: {user_input}\nVal:"}

                async with session.post(
                    "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                    headers=headers, json=payload
                ) as resp:

                    if resp.status == 200:
                        data = await resp.json()
                        # The response is usually a dict with 'generated_text' key or list, so check both
                        if isinstance(data, dict) and "generated_text" in data:
                            reply = data["generated_text"].split("Val:")[-1].strip()
                        elif isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                            reply = data[0]["generated_text"].split("Val:")[-1].strip()
                        else:
                            reply = ""

                        if reply:
                            await message.reply(reply)
                        else:
                            await message.reply("Hmph... whatever.")
                    else:
                        await message.reply(f"Hmph... I’m not answering that. (HuggingFace Error {resp.status})")
        return  # THIS stops double replies

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
