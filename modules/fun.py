from discord.ext import commands
import discord
import requests
import random
from dotenv import load_dotenv
import json
def has_mod_role():
    async def predicate(ctx):
        # Load the setup data from JSON file
        with open('setup_data.json', 'r') as file:
            setup_data = json.load(file)

        guild_id = ctx.guild.id
        setup_info = setup_data.get(str(guild_id))

        if setup_info:
            mod_role_id = setup_info.get("mod_role_id")
            if mod_role_id:
                mod_role = discord.utils.get(ctx.guild.roles, id=mod_role_id)
                return mod_role is not None and mod_role in ctx.author.roles
        else:
            await ctx.send("Pls run d!setup first!")
            

        return False

    return commands.check(predicate)
class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="manebooru", help = "Search for pictures on Manebooru")
    async def manebooru(self, ctx, search_query: str):
        url = f'https://manebooru.art/api/v1/json/search/images?q={search_query}'

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'images' in data and len(data['images']) > 0:
                image = random.choice(data['images'])
                image_url = image['representations']['full']
                author = image['uploader']
                await ctx.send(f'This Image is from {author}. This person is {random.randint(1, 100)}% gay')
                await ctx.send(image_url)
            else:
                await ctx.send('No picture was found')
        else:
            await ctx.send('Error occured while searching for pictures')

    @commands.command(name="derpybooru", help = "Search for pictures on Derpybooru")
    async def derpybooru(self, ctx, search_query: str):
        url = f'https://derpibooru.org/api/v1/json/search/images?q={search_query}'

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'images' in data and len(data['images']) > 0:
                image = random.choice(data['images'])
                image_url = image['representations']['full']
                author = image['uploader']
                await ctx.send(f'This Image is from {author}. This person is {random.randint(1, 100)}% gay')
                await ctx.send(image_url)
            else:
                await ctx.send('No picture was found')
        else:
            await ctx.send('Error occured while searching for pictures')

       
    @commands.command(name="echo", help = "Let the bot say something in a given channel")
    @has_mod_role()
    async def echo(self, ctx, channel: discord.TextChannel, message):
        await channel.send(message)
        await ctx.send(f"{message} was sent in the channel: {channel}")

    