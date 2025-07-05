import os
import discord
from discord.ext import commands
import openai
import asyncio
import random
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

openai.api_key = os.getenv("OPENAI_API_KEY")

tsundere_intros = [
    "Hmph... what do you want?",
    "Tch, you again?",
    "Ugh... I guess I’ll answer.",
    "I-I'm not doing this because I like you, okay?!",
    "S-Shut up! I’m busy... but fine."
]

@bot.event
async def on_ready():
    print(f"Val is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    lower = message.content.lower()
    if message.content.startswith(bot.user.mention) or "val" in lower:
        await message.channel.trigger_typing()
        prompt = message.content

        try:
            response = await ask_openai(prompt)
            intro = random.choice(tsundere_intros)
            reply = f"{intro}\n{response}"
            await message.reply(reply)
        except Exception as e:
            print(f"Error: {e}")
            await message.reply("Ugh, I don’t feel like talking right now...")

    await bot.process_commands(message)

async def ask_openai(prompt):
    for _ in range(3):
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are Val, a bratty but secretly sweet tsundere girl who talks like a real person. You tease, act shy, and care deeply."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.85
            )
            return completion.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            await asyncio.sleep(2)
        except Exception as e:
            print("API error:", e)
            return "Whatever... I’m not dealing with this right now."

keep_alive()
bot.run(os.getenv("TOKEN"))
