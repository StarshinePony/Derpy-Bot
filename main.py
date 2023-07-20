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
intents = discord.Intents.all()
currentprefix = '%'
bot = commands.Bot(command_prefix=currentprefix, intents=intents)

@bot.command(name="prefix", help="Change command prefix")
async def prefix(ctx, newprefix):
    global currentprefix
    currentprefix = newprefix
    await ctx.send(f"```New prefix is '{newprefix}'```")

def get_custom_prefix(bot, message):
    return commands.when_mentioned_or(currentprefix)(bot, message)
    
@bot.command(name="test", help="test")
async def test(ctx):
    await ctx.send("test")

bot.command_prefix = get_custom_prefix
class main():
    global currentprefix
    def currentprefixs():
        currentprefix
#register the class with the bot
@bot.event
async def on_ready():
    await bot.add_cog(music(bot))
    await bot.add_cog(fun(bot))
    await bot.add_cog(warn(bot))
    await bot.add_cog(economy(bot))
    await bot.tree.sync(guild = discord.Object(id=authserver))
    await bot.loop.create_task(economy(bot).check_expired_worktimers())
    await bot.loop.create_task(warn(bot).check_expired_warnings())
    print("Bot is ready")
    
    

    

#start the bot with our token
bot.run(DISCORD_TOKEN)