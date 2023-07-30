import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import sqlite3
from datetime import datetime, timedelta

load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")
authserver = os.getenv("authserver")

#import all of the cogs
from modules.music import music
from modules.fun import fun
from modules.warn import warn
from modules.economy import economy
from modules.spam import spam
intents = discord.Intents.all()
currentprefix = 'v!'
bot = commands.Bot(command_prefix=currentprefix, intents=intents)

#register the class with the bot
@bot.event
async def on_ready():
    await bot.add_cog(music(bot))
    await bot.add_cog(fun(bot))
    await bot.add_cog(warn(bot))
    await bot.add_cog(economy(bot))
    await bot.add_cog(spam(bot))
    await bot.tree.sync(guild = discord.Object(id=authserver))
    await bot.loop.create_task(economy(bot).check_expired_worktimers())
    await bot.loop.create_task(warn(bot).check_expired_warnings())

    
    
@bot.event
async def on_message(message):
    # Ignore messages sent by bots to avoid command loops
    if message.author.bot:
        return

    # Process commands in DM channels but do not add entries to the spam counter.
    if isinstance(message.channel, discord.DMChannel):
        await bot.process_commands(message)
        return

    # Process commands in guild channels
    await bot.process_commands(message)
    

#start the bot with our token
bot.run(DISCORD_TOKEN)