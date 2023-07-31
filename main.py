import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import sqlite3
from datetime import datetime, timedelta
import json

load_dotenv()
# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")
authserver = os.getenv("authserver")
developer = os.getenv("developerid")

#import all of the cogs
from modules.music import music
from modules.fun import fun
from modules.warn import warn
from modules.economy import economy
from modules.spam import spam
from modules.setup import setup
intents = discord.Intents.all()
currentprefix = 'd!'
bot = commands.Bot(command_prefix=currentprefix, intents=intents)

#register the class with the bot
@bot.event
async def on_ready():
    await bot.add_cog(music(bot))
    await bot.add_cog(fun(bot))
    await bot.add_cog(warn(bot))
    await bot.add_cog(economy(bot))
    await bot.add_cog(spam(bot))
    await bot.add_cog(setup(bot))
    print("[MAIN INFO] Bot is ready!")
    await bot.tree.sync(guild = discord.Object(id=authserver))
    await bot.loop.create_task(economy(bot).check_expired_worktimers())
    await bot.loop.create_task(warn(bot).check_expired_warnings())
@bot.event
async def on_guild_join(guild):
    if guild.me == bot.user:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                print("[MAIN INFO]: Bot joined new guild!")
                await channel.send("Thanks for adding Derpy-Bot to your server! "
                                   "First of all, run the d!setup command to set up all your roles and channels!")
                                   
                break
@bot.event
async def on_member_join(member):
    server_id = member.guild.id
    
    with open('setup_data.json', 'r') as file:
        setup_data = json.load(file)
        if setup_data:
            member_role_id = setup_data.get(str(server_id), {}).get("member_role_id")
            member_role = discord.utils.get(member.guild.roles, id=member_role_id)
            # Send the message to the mod_channel
            await member.add_roles(member_role)
            print("[Main INFO]: Member Role given")
        else:
            print("[Main ERROR]: No Setup Data available! No role was handed out!")
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