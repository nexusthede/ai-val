from keep_alive import keep_alive
keep_alive()

import discord
import os
import requests

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = discord.Client(intents=intents)

HF_TOKEN = os.getenv("HF_TOKEN")
BOT_TOKEN = os.getenv("TOKEN")

async def generate_reply(message_content):
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}"
    }
    json_data = {
        "inputs": {
            "past_user_inputs": [],
            "generated_responses": [],
            "text": f"{message_content}"
        }
    }
    response = requests.post(
        "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
        headers=headers,
        json=json_data
    )

    if response.status_code == 200:
        data = response.json()
        return data.get('generated_text', "Hmph... not like I care what you say.")
    else:
        return f"Hmph... I’m not answering that. (HuggingFace Error {response.status_code})"

@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Streaming(name="Hating Duck 💢", url="https://twitch.tv/valbot")
    )
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user.mentioned_in(message) or "val" in message.content.lower():
        async with message.channel.typing():
            reply = await generate_reply(message.content)
            await message.channel.send(reply)

bot.run(BOT_TOKEN)
