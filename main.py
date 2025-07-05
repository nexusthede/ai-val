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
        name="love my nonchalant king nexus ❤️", url="https://twitch.tv/valbot"))

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.lower()
    mentioned = bot.user.mentioned_in(message) or "val" in content

    if mentioned:
        async with message.channel.typing():
            user_input = message.content

            headers = {
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {"inputs": user_input}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
                    headers=headers, json=payload) as resp:

                    if resp.status == 200:
                        data = await resp.json()
                        # The response is a dict with 'generated_text'
                        reply = data.get("generated_text", "").strip()
                        if reply:
                            # Avoid repeating user's message
                            if reply.lower() == user_input.lower():
                                reply = "Hmph... whatever."
                            await message.reply(reply)
                        else:
                            await message.reply("Hmph... not in the mood.")
                    else:
                        await message.reply(f"Hmph... I’m not answering that. (HuggingFace Error {resp.status})")

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
