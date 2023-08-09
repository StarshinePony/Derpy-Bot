import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import json
load_dotenv()
developerid = 1014344645020495942
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
                await ctx.send("You do not have the required moderation permissions to run this command!")
        else:
            await ctx.send("Pls run d!setup first!")

        return False

    return commands.check(predicate)
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

        embed = discord.Embed(title="Derpy Bot User Commands", color=discord.Color.orange())
        
        embed.add_field(name="Economy", value="work\nmoney\npay\nshop\nbuy\nuse\ninventory\n", inline=False)
        embed.add_field(name="Fun Commands", value="manebooru\nderpybooru\n", inline=False)
        embed.add_field(name="Music Commands", value="play\npause\nresume\nskip\nqueue\nclear\nleave\n", inline=False)

        adminembed = discord.Embed(title="Derpy Bot Admin Commands", color=discord.Color.magenta())
        adminembed.add_field(name="Setup", value="setup", inline=False)
        adminembed.add_field(name="Economy Management", value="ecogive\nremovemoney\nworktimer\n", inline=False)
        adminembed.add_field(name="Fun for Admins", value="echo\n", inline=False)
        adminembed.add_field(name="Warn Module", value="warn\nlistwarn\ndelwarn\n", inline=False)
        adminembed.add_field(name="Spam Module", value="ignore_channel\nignore_member\nunignore_channel\nunignore_member\n")

        devembed = discord.Embed(title="Developer Only Commands", color=discord.Color.blurple())
        devembed.add_field(name="INFO", value="All dev commands are slash based commands!\nATTENTION! Commands cause global change to databases!", inline=False)
        devembed.add_field(name="Economyshop", value="additem\nremoveitem\n", inline=False)

        await ctx.send(embed=embed)

        if server_id in setup_data:
            mod_role_id = setup_data[server_id].get('mod_role_id')
            if mod_role_id and str(mod_role_id) in user_roles:
                await ctx.send(embed=adminembed)
        if developerid == user_id:
            await ctx.send(embed=devembed)

            
