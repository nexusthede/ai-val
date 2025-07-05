from keep_alive import keep_alive
keep_alive()

import discord
import os
import aiohttp
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🌸 Val is online as {bot.user}!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions or "val" in message.content.lower():
        async with message.channel.typing():
            response = await get_val_response(message.content)
            await message.reply(response)

    await bot.process_commands(message)

async def get_val_response(user_input):
    prompt = [
        {
            "role": "system",
            "content": "You are Val, a bratty tsundere anime girl. You act annoyed and smug, but you're secretly kind. Respond casually like a human girl, not a robot."
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": prompt
    }

    async with aiohttp.ClientSession() as session:
        async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"Hmph... I’m not answering that. (OpenAI Error {resp.status})"

bot.run(os.getenv("TOKEN"))
