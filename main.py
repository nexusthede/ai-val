import os
import discord
import aiohttp
from discord.ext import commands
from keep_alive import keep_alive  # Optional, if you want an HTTP server for uptime monitoring

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
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Streaming(
        name="love my nonchalant king Nexus ❤️",
        url="https://twitch.tv/valbot"
    ))

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content_lower = message.content.lower()
    # Trigger if bot is mentioned or if "val" is in message content anywhere
    if bot.user.mentioned_in(message) or "val" in content_lower:
        async with message.channel.typing():
            user_input = message.content
            headers = {
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {"inputs": f"User: {user_input}\nVal:"}
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                    headers=headers,
                    json=payload
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # The response format might vary; adjust if needed
                        if isinstance(data, list) and len(data) > 0:
                            reply = data[0].get("generated_text", "")
                            reply = reply.split("Val:")[-1].strip() if reply else ""
                            if reply:
                                await message.reply(reply)
                            else:
                                await message.reply("Hmph... whatever.")
                        else:
                            await message.reply("Hmph... not in the mood.")
                    else:
                        await message.reply(f"Hmph... I’m not answering that. (HuggingFace Error {resp.status})")

    await bot.process_commands(message)

if __name__ == "__main__":
    keep_alive()  # Remove if you don't use keep_alive server
    bot.run(TOKEN)
