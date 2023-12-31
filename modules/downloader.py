import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
import os


class download(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
   
    
    @commands.command(name="download", help="downloads a selected song from youtube")
    async def download(self, ctx, *, songlink: str = None):
        if songlink == None:
            await ctx.send(f"Missing argument songlink: Usage: " + str(ctx.prefix) + "download <songlink>")
            return
        await ctx.send("Waiting for file download...")
        
        print(songlink)
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': 'True',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                }],
            'outtmpl': os.path.join("modules/", '%(title)s [%(id)s].%(ext)s'),
        }
        if songlink[:4] != 'http':
                    ydl_opts = {
                        'default_search': 'ytsearch',
                        'format': 'bestaudio/best',
                        'noplaylist': 'True',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                        }],
                        'outtmpl': os.path.join("modules/", '%(title)s [%(id)s].%(ext)s'),
                    }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(songlink, download=True)
            if songlink[:4] != 'http':
                info = info['entries'][0]
            title = info['title']
            trackid = info['id']
            audio_file = f"{title} [{trackid}].mp3"
            cover = info.get('thumbnail', None)
            uploader = info['uploader']
            duration = info['duration']
            url = info['url']
        absolute_file_path = os.path.join(os.path.dirname(__file__), audio_file)
        file = discord.File(absolute_file_path, filename=audio_file)
        embed = discord.Embed(title="Songfile", color=discord.Color.pink())
        embed.add_field(name="INFO", value="If the songfile is too big (surpasses 25mb you only get a download url!)", inline=False)
        embed.add_field(name="Title", value=f"[{title}]({songlink})", inline=False)
        embed.add_field(name="Uploader", value=uploader, inline=False)
        embed.add_field(name="Duration", value=f"{duration}s", inline=False)
        embed.add_field(name="Download/Stream", value=f"[Stream or Download]({url})", inline=False)
        embed.set_thumbnail(url=cover)
        await ctx.send(embed=embed, file=file)
        try:
            os.remove(absolute_file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")