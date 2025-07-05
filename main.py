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
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "⚠️ OpenAI API key not set. Please check your environment variables."

    prompt = [
        {
            "role": "system",
            "content": (
                "You are Val, a bratty tsundere anime girl. "
                "Speak casually like a real person, a bit annoyed but secretly kind."
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": prompt,
        "temperature": 0.7
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result["choices"][0]["message"]["content"].strip()
                elif resp.status == 401:
                    return "⚠️ OpenAI API key invalid or unauthorized. Please check your key."
                else:
                    return f"⚠️ OpenAI API returned error {resp.status}."
        except Exception as e:
            return f"⚠️ An error occurred contacting OpenAI: {e}"

bot.run(os.getenv("TOKEN"))
