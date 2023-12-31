import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
load_dotenv()
developerid = os.getenv("developerid")


class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def help(self, ctx):
        try:
            with open('setup_data.json', 'r') as file:
                setup_data = json.load(file)
        except FileNotFoundError:
            setup_data = {}  # Set an empty dictionary if the file is not found

        server_id = str(ctx.guild.id)
        user_roles = [str(role.id) for role in ctx.author.roles]
        user_id = ctx.author.id

        embed = discord.Embed(title="Trixie User Commands", color=discord.Color.orange())
        
        embed.add_field(name="Economy", value="work\nmoney\npay\nshop\nbuy\nuse\ninventory\nmarket\nshare_info\nsell_share\nbuy_share\n", inline=False)
        embed.add_field(name="Fun Commands", value="manebooru\ntwibooru\nponybooru\nponerpics\n", inline=False)
        embed.add_field(name="Music Commands", value="play\npause\nresume\nskip\nqueue\nclear\nleave\n", inline=False)
        embed.add_field(name="Download Module", value="download: Only single tracks work! (For youtube: Pls use the shortened links!)")

        adminembed = discord.Embed(title="Trixie Admin Commands", color=discord.Color.magenta())
        adminembed.add_field(name="Setup", value="setup", inline=False)
        adminembed.add_field(name="Economy Management", value="ecogive\nremovemoney\nworktimer\n", inline=False)
        adminembed.add_field(name="Fun for Admins", value="echo\nderpybooru\n", inline=False)
        adminembed.add_field(name="Warn Module", value="warn\nlistwarn\ndelwarn\n", inline=False)
        adminembed.add_field(name="Spam Module", value="ignore_channel\nignore_member\nunignore_channel\nunignore_member\n")

        devembed = discord.Embed(title="Developer Only Commands", color=discord.Color.blurple())
        devembed.add_field(name="INFO", value="All dev commands are slash based commands!\nATTENTION! Commands cause global change to databases!", inline=False)
        devembed.add_field(name="Economyshop", value="additem\nremoveitem\naddstock\n", inline=False)

        await ctx.send(embed=embed)

        if server_id in setup_data:
            mod_role_id = setup_data[server_id].get('mod_role_id')
            if mod_role_id and str(mod_role_id) in user_roles:
                await ctx.send(embed=adminembed)
        if int(developerid) == int(user_id):
            await ctx.send(embed=devembed)

            
