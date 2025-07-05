import os
import discord
from discord.ext import commands
import openai

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

openai.api_key = os.getenv("OPENAI_API_KEY")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Streaming(
        name="Ugh... I really *hate* that Duck guy... D-Don’t ask why!",
        url="https://twitch.tv/nexus"
    ))

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()
    if bot.user.mentioned_in(message) or 'val' in content:
        async with message.channel.typing():
            prompt = (
                f"Val is a tsundere girl who is shy but a bit rude and really hates Duck (the person). "
                f"Reply naturally and bratty:\nUser: {message.content}\nVal:"
            )
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=150,
                    temperature=0.7,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0.6,
                    stop=["User:", "Val:"]
                )
                reply = response.choices[0].text.strip()
            except Exception as e:
                reply = "Hmph... I’m not answering that. (OpenAI Error)"
                print(f"OpenAI API error: {e}")

            await message.channel.send(reply)

    await bot.process_commands(message)

bot.run(os.getenv("TOKEN"))
