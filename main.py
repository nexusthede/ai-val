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
        name="I’m not interested, okay?", url="https://twitch.tv/valbot"))

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    content = message.content.lower()
    mentioned = bot.user.mentioned_in(message) or "val" in content

    if mentioned:
        try:
            await message.channel.trigger_typing()
        except AttributeError:
            # fallback for discord.py versions without trigger_typing
            pass

        user_input = message.content

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            }
            # Falcon RW 1b uses the HuggingFace Inference API POST payload format
            payload = {
                "inputs": user_input,
                "parameters": {"max_new_tokens": 150, "do_sample": True, "top_p": 0.9}
            }

            async with session.post(
                "https://api-inference.huggingface.co/models/tiiuae/falcon-rw-1b",
                headers=headers, json=payload) as resp:

                if resp.status == 200:
                    data = await resp.json()
                    # Falcon RW returns text directly in 'generated_text' or just a string
                    reply = ""
                    if isinstance(data, dict) and "generated_text" in data:
                        reply = data["generated_text"]
                    elif isinstance(data, list) and len(data) > 0:
                        reply = data[0].get("generated_text", "")
                    elif isinstance(data, str):
                        reply = data

                    if reply:
                        # Tsundere style: add slight attitude
                        tsundere_reply = f"Hmph! {reply.strip()}"
                        await message.reply(tsundere_reply)
                    else:
                        await message.reply("Hmph... whatever.")
                elif resp.status == 404:
                    await message.reply("Hmph... that model doesn't exist! (HF Error 404)")
                else:
                    await message.reply(f"Hmph... I’m not answering that. (HF Error {resp.status})")

    await bot.process_commands(message)

keep_alive()
bot.run(TOKEN)
