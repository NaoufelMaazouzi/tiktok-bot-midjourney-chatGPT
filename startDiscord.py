import discord
from discord.ext import commands
from midjourney import generateImages
from chatGPT import createScript

discord_token = "MTA5Njk2NTc0MzgzNDMwODYxOA.GN4ojj.2yGfvXjhtCtBe7X0sZw1R-Vf31dltfeLl5rMeU"
client = commands.Bot(command_prefix="*", intents=discord.Intents.all())

@client.event
async def on_ready():
    print("Bot connected")

@client.event
async def on_message(message):
    if message.content == 'automation':
        script = createScript()
        await generateImages(message)


client.run(discord_token)