import discord
from discord.ext import commands, tasks
import json
import time

class spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_inactive_users.start()
        self.decrease_spam_pressure.start()
        self.decrease_message_counter.start()

        # Load spam pressure data from the JSON file or set it to an empty dictionary if the file is empty.
        try:
            with open('spam_pressure.json', 'r') as f:
                data = f.read()
                if data:
                    self.spam_pressure = json.loads(data)
                else:
                    self.spam_pressure = {}
        except FileNotFoundError:
            self.spam_pressure = {}
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        server_id = str(message.guild.id)
        user_id = str(message.author.id)

        # Check if the user has the "Timeout" role and delete their messages.
        timeout_role = discord.utils.get(message.author.roles, name='Timeout')
        if timeout_role:
            await message.delete()
            return

        # Check if the message sender is ignored by the spam module for this server.
        if server_id in self.spam_pressure and self.spam_pressure[server_id].get(user_id, {}).get('ignored'):
            return  # Ignore messages from ignored members for the spam module.

        # Calculate spam pressure based on message length and emojis count.
        spam_pressure_value = len(message.content) + len(message.reactions) * 5

        # Retrieve the user's spam pressure from the dictionary or set it to 0 if not present.
        user_spam_data = self.spam_pressure.setdefault(server_id, {}).setdefault(user_id, {})
        user_spam_data['spam_pressure'] = user_spam_data.get('spam_pressure', 0) + spam_pressure_value

        # Update the message counter for the user and save it back to the dictionary.
        user_spam_data['message_count'] = user_spam_data.get('message_count', 0) + 1

        # Define the threshold for spam detection.
        spam_threshold = 1000
        message_threshold = 3

        if user_spam_data['spam_pressure'] >= spam_threshold:
            # Check if the user has already been given the "Timeout" role.
            if not any(role.name == 'Timeout' for role in message.author.roles):
                timeout_role = discord.utils.get(message.author.guild.roles, name='Timeout')
                if timeout_role:
                    await message.author.add_roles(timeout_role)
                    await message.channel.send(f"{message.author.mention} You have been given the 'Timeout' role.")
                else:
                    await message.channel.send("The 'Timeout' role does not exist. Please create it and set the proper permissions.")

        if user_spam_data['message_count'] >= message_threshold:
            if not any(role.name == 'Timeout' for role in message.author.roles):
                timeout_role = discord.utils.get(message.author.guild.roles, name='Timeout')
                if timeout_role:
                    await message.author.add_roles(timeout_role)
                    print("MEP")
                else:
                    print("Error: Timeout Role doesn't exist. Bot failed to create the role: Timout")

        # Save the updated spam pressure data to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @tasks.loop(minutes=5)
    async def check_inactive_users(self):
        # Calculate the current timestamp.
        current_time = time.time()

        # A list to store server and user IDs to be removed.
        server_user_to_remove = []

        # Iterate through the spam pressure data to find inactive users.
        for server_id, server_data in self.spam_pressure.items():
            for user_id, user_data in server_data.items():
                if current_time - user_data.get('last_activity_time', 0) >= 300:  # 300 seconds = 5 minutes
                    server_user_to_remove.append((server_id, user_id))

        # Remove entries for inactive users from the dictionary.
        for server_id, user_id in server_user_to_remove:
            self.spam_pressure[server_id].pop(user_id)

        # Save the updated spam pressure data to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @tasks.loop(seconds=60)
    async def decrease_spam_pressure(self):
        # Decrement spam pressure by 50 for each user in each server.
        for server_id, server_data in self.spam_pressure.copy().items():
            for user_id, user_data in server_data.copy().items():
                if isinstance(user_data, dict):
                    self.spam_pressure[server_id][user_id]['spam_pressure'] = max(0, user_data.get('spam_pressure', 0) - 1000)

        # Save the updated spam pressure data to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @tasks.loop(seconds=2)
    async def decrease_message_counter(self):
        # Decrement message counter by 3 for each user in each server.
        for server_id, server_data in self.spam_pressure.copy().items():
            for user_id, user_data in server_data.copy().items():
                if isinstance(user_data, dict):
                    self.spam_pressure[server_id][user_id]['message_count'] = max(0, user_data.get('message_count', 0) - 3)

        # Save the updated spam pressure data to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @check_inactive_users.before_loop
    @decrease_spam_pressure.before_loop
    @decrease_message_counter.before_loop
    async def before_tasks(self):
        # Wait for the bot to be ready before starting the background tasks.
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ignore_member(self, ctx, member: discord.Member):
        server_id = str(ctx.guild.id)
        user_id = str(member.id)

        ignored_members = self.spam_pressure.setdefault(server_id, {}).setdefault(user_id, {})
        ignored_members['ignored'] = True

        await ctx.send(f"Ignoring messages from {member.mention}")
        # Save the updated ignored members to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unignore_member(self, ctx, member: discord.Member):
        server_id = str(ctx.guild.id)
        user_id = str(member.id)

        ignored_members = self.spam_pressure.setdefault(server_id, {}).setdefault(user_id, {})
        if 'ignored' in ignored_members:
            ignored_members.pop('ignored', None)

            await ctx.send(f"{member.mention} is no longer ignored.")
            # Save the updated ignored members to the JSON file.
            with open('spam_pressure.json', 'w') as f:
                json.dump(self.spam_pressure, f)
        else:
            await ctx.send(f"{member.mention} is not ignored.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ignore_channel(self, ctx, channel: discord.TextChannel):
        server_id = str(ctx.guild.id)
        ignored_channels = self.spam_pressure.setdefault(server_id, {}).setdefault('ignored_channels', [])
        ignored_channels.append(channel.id)

        await ctx.send(f"Ignoring messages from {channel.mention}")
        # Save the updated ignored channels to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def off(self, ctx):
        server_id = str(ctx.guild.id)
        if server_id in self.spam_pressure:
            self.spam_pressure[server_id]['ignored_members'] = {}
            self.spam_pressure[server_id]['ignored_channels'] = []
        await ctx.send("Spam module is now turned off.")
        # Save the updated ignored members and channels to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def on(self, ctx):
        server_id = str(ctx.guild.id)
        if server_id in self.spam_pressure:
            self.spam_pressure[server_id]['ignored_members'] = {}
            self.spam_pressure[server_id]['ignored_channels'] = []
        await ctx.send("Spam module is now turned on.")
        # Save the updated ignored members and channels to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    

