import discord
from discord.ext import commands
import json


class setup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.setup_data = {}

    def save_data(self):
        with open('setup_data.json', 'w') as file:
            json.dump(self.setup_data, file)

    def load_data(self):
        try:
            with open('setup_data.json', 'r') as file:
                self.setup_data = json.load(file)
        except FileNotFoundError:
            pass

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def setup(self, ctx):
        self.load_data()  # Load data from the JSON file, if available

        guild_id = ctx.guild.id
        if guild_id in self.setup_data:
            await ctx.send("Setup data already exists for this server.")
            return

        await ctx.send("Welcome to the bot setup! Please provide the required information.")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        # Mod role setup
        await ctx.send("Please mention the Mod role.")
        message = await self.bot.wait_for('message', check=check)
        mod_role = message.role_mentions[0]

        # Mod channel setup
        await ctx.send("Please mention the Mod channel.")
        message = await self.bot.wait_for('message', check=check)
        mod_channel = message.channel_mentions[0]

        # Member role setup
        await ctx.send("Please mention the Member role.")
        message = await self.bot.wait_for('message', check=check)
        member_role = message.role_mentions[0]
        # Timeout role creation
        timeout_role = discord.utils.get(ctx.guild.roles, name="Timeout")
        if not timeout_role:
            timeout_role = await ctx.guild.create_role(name="Timeout", reason="Timeout role for temporary punishments")

            # Set permissions for the Timeout role (you can adjust these permissions as needed)
            timeout_permissions = discord.PermissionOverwrite(
                send_messages=False, read_messages=True)

            for channel in ctx.guild.channels:
                await channel.set_permissions(timeout_role, overwrite=timeout_permissions)

        self.setup_data[guild_id] = {
            "mod_role_id": mod_role.id,
            "mod_channel_id": mod_channel.id,
            "member_role_id": member_role.id,
            "timeout_role_id": timeout_role.id
        }

        self.save_data()  # Save the data to the JSON file

        await ctx.send("Setup complete! Now the bot is ready to use with the provided configurations.")
