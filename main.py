import os
import discord
import aiohttp
from discord.ext import commands
from keep_alive import keep_alive  # Make sure you have this Flask server file

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
        name="Hating everyone 💢",
        url="https://twitch.tv/valbot"
    ))

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content_lower = message.content.lower()
    # Respond if bot is mentioned or "val" in message
    if bot.user.mentioned_in(message) or "val" in content_lower:
        await message.channel.typing()

        user_input = message.content

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "inputs": user_input,
                "parameters": {"max_new_tokens": 100, "temperature": 0.7}
            }

            # Using microsoft/phi-3-mini-128k-instruct as example HF model
            api_url = "https://api-inference.huggingface.co/models/microsoft/phi-3-mini-128k-instruct"

            try:
                async with session.post(api_url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # The response is usually a dict with 'generated_text'
                        reply = data.get("generated_text", "").strip()
                        if reply:
                            # Tsundere style slight twist:
                            tsundere_reply = f"Hmph... {reply}"
                            await message.reply(tsundere_reply, mention_author=False)
                        else:
                            await message.reply("Hmph... don't expect me to say anything.", mention_author=False)
                    else:
                        await message.reply(
                            f"Hmph... I'm not answering that. (HF Error {resp.status})",
                            mention_author=False
                        )
            except Exception as e:
                await message.reply(f"Hmph... Something's wrong. ({e})", mention_author=False)

    await bot.process_commands(message)

# Keep the Flask server running for Render
keep_alive()

# Run the bot
bot.run(TOKEN)
