import os
import discord
from discord.ext import commands
import aiohttp

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

HF_TOKEN = os.getenv("HF_TOKEN")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Hating Duck 💢"))
    print("Status set: Hating Duck 💢")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Respond only if bot is mentioned or name 'val' in message (case-insensitive)
    if bot.user in message.mentions or "val" in message.content.lower():
        await message.channel.trigger_typing()
        prompt = message.content.replace(f"<@!{bot.user.id}>", "").replace("val", "").strip()
        if not prompt:
            prompt = "..."

        async with aiohttp.ClientSession() as session:
            try:
                payload = {"inputs": prompt}
                async with session.post(HF_API_URL, headers=HEADERS, json=payload, timeout=30) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # BlenderBot returns a list with dict: [{"generated_text": "..."}]
                        reply = data[0]["generated_text"]
                        # Add tsundere flavor:
                        tsundere_replies = [
                            f"Hmph... {reply} (Not that I care or anything!)",
                            f"Whatever... {reply}",
                            f"Geez, don't get the wrong idea! {reply}",
                            f"I-I'm only replying because you asked... {reply}"
                        ]
                        import random
                        await message.channel.send(random.choice(tsundere_replies))
                    else:
                        await message.channel.send("Hmph... I’m not answering that right now. (API error)")
            except asyncio.TimeoutError:
                await message.channel.send("Ugh, you're too slow. Try again.")
            except Exception as e:
                print(f"Error: {e}")
                await message.channel.send("Hmph... Something went wrong.")

    await bot.process_commands(message)

if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    if not TOKEN or not HF_TOKEN:
        print("Error: TOKEN and HF_TOKEN environment variables must be set!")
        exit(1)
    bot.run(TOKEN)
