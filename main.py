import os
import discord
from discord.ext import commands
import openai
from flask import Flask
from threading import Thread

# Keep‑alive web server for Render
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

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load OpenAI API key from env
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("❌ ERROR: OPENAI_API_KEY environment variable not found! AI responses disabled.")
else:
    openai.api_key = openai_api_key

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Short tsundere streaming status
    await bot.change_presence(activity=discord.Streaming(
        name="Hmph... What do you want? Go annoy someone else.",
        url="https://twitch.tv/nexus"
    ))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Respond if bot is mentioned or "val" in message
    if bot.user.mentioned_in(message) or "val" in message.content.lower():
        if not openai_api_key:
            await message.channel.send("⚠️ OpenAI API key missing or invalid. Can't respond.")
            return

        async with message.channel.typing():
            prompt = (
                "Val is a tsundere girl who is shy, a bit rude but secretly kind. "
                "She talks naturally and bratty.\n"
                f"User: {message.content}\nVal:"
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
            except openai.error.AuthenticationError:
                reply = "⚠️ OpenAI API key invalid or unauthorized."
            except Exception as e:
                print(f"OpenAI API error: {e}")
                reply = "Hmph... I’m not answering that. (OpenAI Error)"

            await message.channel.send(reply)

    await bot.process_commands(message)

# Start keep-alive server and run bot
keep_alive()
bot.run(os.getenv("TOKEN"))
