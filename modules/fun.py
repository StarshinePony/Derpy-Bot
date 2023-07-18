from discord.ext import commands
import discord
import requests
import random
from dotenv import load_dotenv

class fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="manebooru", description = "Search for pictures on Manebooru")
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

    @commands.command(name="derpybooru", description = "Search for pictures on Derpybooru")
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

       
    @commands.command(name="echo", description = "Let the bot say something in a given channel")
    @commands.has_permissions(kick_members = True)
    async def echo(self, ctx, channel: discord.TextChannel, message):
        await channel.send(message)
        await ctx.send(f"{message} was sent in the channel: {channel}")

    