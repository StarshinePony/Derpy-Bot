import discord
from discord.ext import commands
import json


class logger(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message):
        server_id = str(message.guild.id)
        member = message.author
        user_roles = [role.id for role in message.author.roles]
        with open('setup_data.json', 'r') as file:
            setup_data = json.load(file)
            if setup_data:
                channel_id = setup_data.get(
                str(server_id), {}).get("logging_channel_id")
                channel = self.bot.get_channel(channel_id)
                pony_id = setup_data.get(
                str(server_id), {}).get("new_pony_role_id")

                
                if pony_id in user_roles:
                    embed = discord.Embed(color=discord.Color.magenta())
                    embed.add_field(name="Message Content", value=message.content)
                    embed.set_author(name=member.name, icon_url=member.avatar.url)
                    embed.set_footer(text=f"USER ID: {member.id} | Message ID: {message.id}")
                    await channel.send(embed=embed)