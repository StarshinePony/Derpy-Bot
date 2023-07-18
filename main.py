import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

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
bot = commands.Bot(command_prefix='$', intents=intents)


#remove the default help command so that we can write out own


#register the class with the bot
@bot.event
async def on_ready():
    await bot.add_cog(music(bot))
    await bot.add_cog(fun(bot))
    await bot.add_cog(warn(bot))
    await bot.add_cog(economy(bot))
    await bot.tree.sync(guild = discord.Object(id=authserver))
    print("Bot is ready")

    

    

#start the bot with our token
bot.run(DISCORD_TOKEN)