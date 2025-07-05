import os
import discord
from discord.ext import commands
import openai
from flask import Flask
from threading import Thread

# Keep-alive server
app = Flask('')

@app.route('/')
def home():
    return "✅ Val is awake!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# OpenAI key
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key
else:
    print("⚠️ No OpenAI API Key set.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Streaming(
        name="Hmph... What do you want? Go annoy someone else.",
        url="https://twitch.tv/nexus"
    ))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user.mentioned_in(message) or "val" in message.content.lower():
        if not openai_api_key:
            await message.channel.send("⚠️ OpenAI API key missing or invalid.")
            return

        async with message.channel.typing():
            prompt = (
                "Val is a tsundere girl. She acts bratty and shy, but she's secretly sweet and kind. "
                "She talks like a real person.\n"
                f"User: {message.content.strip()}\nVal:"
            )
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=150,
                    temperature=0.7,
                    stop=["User:", "Val:"]
                )
                reply = response.choices[0].text.strip()
            except openai.OpenAIError:
                reply = "⚠️ OpenAI API key invalid or unauthorized. (401)"
            except Exception as e:
                print(f"OpenAI Error: {e}")
                reply = "Hmph... I’m not answering that. (OpenAI Error)"

            await message.channel.send(reply)

    await bot.process_commands(message)

# Run
keep_alive()
bot.run(os.getenv("TOKEN"))
