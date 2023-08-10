from ast import alias
from discord import app_commands
import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import asyncio
import os


class download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
   
    
    @commands.command(name="download")
    async def download(self, ctx, songlink: str):
        await ctx.send("Waiting for file download...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(songlink, download=False)
            title = info['title']
            trackid = info['id']
            audio_file = f"{title} [{trackid}].mp3"
            cover = info.get('thumbnail', None)
            uploader = info['uploader']
            duration = info['duration']
            url = info['url']

        embed = discord.Embed(title="Songfile", color=discord.Color.pink())
        embed.add_field(name="Link", value=songlink, inline=False)
        embed.add_field(name="Title", value=title, inline=False)
        embed.add_field(name="Uploader", value=uploader, inline=False)
        embed.add_field(name="Duration", value=f"{duration}s", inline=False)
        embed.add_field(name="Download URL", value=url, inline=False)
        embed.set_thumbnail(url=cover)
    
        await ctx.send(embed=embed)