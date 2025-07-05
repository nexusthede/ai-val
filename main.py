import os
import discord
import aiohttp
from discord.ext import commands
from keep_alive import keep_alive

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
        name="Hating everyone 💢", url="https://twitch.tv/valbot"))

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
            headers = {
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": f"<|user|> {user_input}\n<|assistant|>",
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9
                }
            }
            async with session.post(
                "https://api-inference.huggingface.co/models/microsoft/phi-3-mini-128k-instruct",
                headers=headers, json=payload) as resp:

                if resp.status == 200:
                    data = await resp.json()
                    reply = data.get("generated_text", "").split("<|assistant|>")[-1].strip()
                    await message.reply(reply if reply else "Tch... whatever.")
                else:
                    await message.reply(f"Hmph... I’m not answering that. (HuggingFace Error {resp.status})")

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
