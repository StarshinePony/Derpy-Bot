from discord.ext import commands
import discord
from discord import app_commands
import requests
import random
from dotenv import load_dotenv
import os
from modules.backend import has_mod_role
load_dotenv()

server_id = int(os.getenv("authserver"))


class fun(commands.Cog):
    authserver = os.getenv("authserver")
    developerid = os.getenv("developerid")
    def __init__(self, bot):
        self.bot = bot

    async def process_booru_command(self, ctx, url, images, incomplete_url):
        #main body of booru commands in separate func to avoid code repetition
        if url == None:
            await ctx.send(f"Missing argument search query: Usage: " + str(ctx.prefix) + str(ctx.command) + " <search query>")
        else:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if images in data and len(data[images]) > 0:
                    image = random.choice(data[images])
                    image_url = incomplete_url + image['representations']['full']
                    if 'uploader' in image:
                        author = image['uploader']
                    else:
                        author = 'anonymous'
                    await ctx.send(f'This Image is from {author}.')
                    await ctx.send(image_url)
                else:
                    await ctx.send('No picture was found')
            else:
                await ctx.send('Error occured while searching for pictures')
    
    @commands.command(name="manebooru", help="Search for pictures on Manebooru")
    async def manebooru(self, ctx, *, search_query: str = None):
        if search_query != None:
            search_query = f'https://manebooru.art/api/v1/json/search/images?q={search_query},-explicit,-suggestive,-*fetish&sf=random'

        await self.process_booru_command(ctx, search_query, 'images', '')


    @commands.command(name="derpibooru", help="Search for pictures on Derpibooru")
    @has_mod_role()
    async def derpybooru(self, ctx, *, search_query: str = None):
        if search_query != None:
            search_query = f'https://derpibooru.org/api/v1/json/search/images?q={search_query},-explicit,-suggestive,-*fetish&sf=random'

        await self.process_booru_command(ctx, search_query, 'images', '')


    @commands.command(name="twibooru", help="Search for pictures on Twibooru")
    async def twibooru(self, ctx, *, search_query: str = None):
        if search_query != None:
            search_query = f'https://twibooru.org//api/v3/search/posts?q={search_query},-explicit,-suggestive,-*fetish&sf=random'

        await self.process_booru_command(ctx, search_query, 'posts', '')


    @commands.command(name="ponerpics", help="Search for pictures on Ponerpics")
    async def ponerpics(self, ctx, *, search_query: str = None):
        if search_query != None:
            search_query = f'https://ponerpics.org/api/v1/json/search/images?q={search_query},-explicit,-suggestive,-*fetish&sf=random'

        await self.process_booru_command(ctx, search_query, 'images', 'https://ponerpics.org/')


    @commands.command(name="ponybooru", help="Search for pictures on Ponybooru")
    async def ponybooru(self, ctx, *, search_query: str = None):
        if search_query != None:
            search_query = f'https://ponybooru.org/api/v1/json/search/images?q={search_query},-explicit,-suggestive,-*fetish&sf=random'

        await self.process_booru_command(ctx, search_query, 'images', '')


    @commands.hybrid_command(name="echo", with_app_command=True, help="Adds a new Item globaly")
    @app_commands.guilds(discord.Object(id=server_id))
    @has_mod_role()
    async def echo(self, ctx, channel_id: discord.TextChannel, *, message: commands.clean_content):
        channel = self.bot.get_channel(channel_id.id)
        if channel:
            await channel.send(message)
            await ctx.send(f"{message} was sent in the channel: {channel.mention}")
        else:
            await ctx.send("Invalid channel ID. Please provide a valid text channel.")
