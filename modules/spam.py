import discord
from discord.ext import commands, tasks
import json
import time


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



class spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
        ignored_roles = [str(role.id) for role in message.author.roles]
        ignored_channel_id = str(message.channel.id)

        # Check if the user has the "Timeout" role and delete their messages.
        timeout_role = discord.utils.get(message.author.roles, name='Timeout')
        if timeout_role:
            await message.delete()
            return

        # Check if the message sender is ignored by the spam module for this server.
        with open('setup_data.json', 'r') as file:
            setup_data = json.load(file)
        if setup_data:
            mod_role_id = setup_data.get(server_id, {}).get("mod_role_id")
            mod_channel_id = setup_data.get(server_id, {}).get("mod_channel_id")

            if mod_role_id and mod_role_id in ignored_roles:
                return  # Ignore messages from users with the mod role.

            if mod_channel_id and ignored_channel_id == mod_channel_id:
                return


        if server_id in self.spam_pressure and self.spam_pressure[server_id].get(user_id, {}).get('ignored'):
            return

        if server_id in self.spam_pressure and ignored_channel_id in self.spam_pressure[server_id].get('ignored_channels', []):
            return

        # Calculate spam pressure based on message length and emojis count.
        spam_pressure_value = len(message.content) + len(message.reactions) * 5

        # Retrieve the user's spam pressure from the dictionary or set it to 0 if not present.
        user_spam_data = self.spam_pressure.setdefault(
            server_id, {}).setdefault(user_id, {})
        user_spam_data['spam_pressure'] = user_spam_data.get(
            'spam_pressure', 0) + spam_pressure_value

        # Update the message counter for the user and save it back to the dictionary.
        user_spam_data['message_count'] = user_spam_data.get(
            'message_count', 0) + 1
        message_count = user_spam_data['message_count']

        # Define the threshold for spam detection.
        spam_threshold = 1000
        message_threshold = 3

        if user_spam_data['spam_pressure'] >= spam_threshold:
            # Check if the user has already been given the "Timeout" role.
            if not any(role.name == 'Timeout' for role in message.author.roles):
                timeout_role = discord.utils.get(
                    message.author.guild.roles, name='Timeout')
                if timeout_role:
                    await message.author.add_roles(timeout_role)

                    # Get the mod_channel_id from setup_data.json
                    with open('setup_data.json', 'r') as file:
                        setup_data = json.load(file)
                    mod_channel_id = setup_data.get(
                        str(server_id), {}).get("mod_channel_id")
                    mod_role_id = setup_data.get(
                        str(server_id), {}).get("mod_role_id")
                    mod_role = discord.utils.get(
                        message.guild.roles, id=mod_role_id)
                    # Send the message to the mod_channel
                    if mod_channel_id:
                        mod_channel = self.bot.get_channel(mod_channel_id)
                        if mod_channel:
                            print(
                                f"[SPAM INFO] User {message.author} got silenced")
                            await mod_channel.send(f"{mod_role.mention} ATTENTION!: {message.author.mention} got silenced: PRESSURE REACHED {spam_pressure_value}.")
                        else:
                            print("Error: Mod Channel not found.")
                    else:
                        print("Error: Mod Channel ID not found in setup_data.json.")

                else:
                    print(
                        "The 'Timeout' role does not exist. Please create it and set the proper permissions.")

        if user_spam_data['message_count'] >= message_threshold:
            if not any(role.name == 'Timeout' for role in message.author.roles):
                timeout_role = discord.utils.get(
                    message.author.guild.roles, name='Timeout')
                if timeout_role:
                    await message.author.add_roles(timeout_role)

                    # Get the mod_channel_id from setup_data.json
                    with open('setup_data.json', 'r') as file:
                        setup_data = json.load(file)
                    mod_channel_id = setup_data.get(
                        str(server_id), {}).get("mod_channel_id")
                    mod_role_id = setup_data.get(
                        str(server_id), {}).get("mod_role_id")
                    mod_role = discord.utils.get(
                        message.guild.roles, id=mod_role_id)
                    # Send the message to the mod_channel
                    if mod_channel_id:
                        mod_channel = self.bot.get_channel(mod_channel_id)
                        if mod_channel:
                            print(
                                f"[SPAM INFO] User {message.author} got silenced")
                            await mod_channel.send(f"{mod_role.mention} ATTENTION!: {message.author.mention} got silenced: PRESSURE REACHED {message_count}")
                        else:
                            print("Error: Mod Channel not found.")
                    else:
                        print("Error: Mod Channel ID not found in setup_data.json.")
                else:
                    print(
                        "Error: Timeout Role doesn't exist. Bot failed to create the role: Timeout")

        # Save the updated spam pressure data to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @tasks.loop(seconds=60)
    async def decrease_spam_pressure(self):
        # Decrement spam pressure by 50 for each user in each server.
        for server_id, server_data in self.spam_pressure.copy().items():
            for user_id, user_data in server_data.copy().items():
                if isinstance(user_data, dict):
                    self.spam_pressure[server_id][user_id]['spam_pressure'] = max(
                        0, user_data.get('spam_pressure', 0) - 1000)

        # Save the updated spam pressure data to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @tasks.loop(seconds=2)
    async def decrease_message_counter(self):
        # Decrement message counter by 3 for each user in each server.
        for server_id, server_data in self.spam_pressure.copy().items():
            for user_id, user_data in server_data.copy().items():
                if isinstance(user_data, dict):
                    self.spam_pressure[server_id][user_id]['message_count'] = max(
                        0, user_data.get('message_count', 0) - 3)

        # Save the updated spam pressure data to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @decrease_spam_pressure.before_loop
    @decrease_message_counter.before_loop
    async def before_tasks(self):
        # Wait for the bot to be ready before starting the background tasks.
        await self.bot.wait_until_ready()

    @commands.command()
    @has_mod_role()
    async def ignore_member(self, ctx, member: discord.Member):
        server_id = str(ctx.guild.id)
        user_id = str(member.id)

        ignored_members = self.spam_pressure.setdefault(
            server_id, {}).setdefault(user_id, {})
        ignored_members['ignored'] = True

        await ctx.send(f"Ignoring messages from {member.mention}")
        # Save the updated ignored members to the JSON file.
        with open('spam_pressure.json', 'w') as f:
            json.dump(self.spam_pressure, f)

    @commands.command()
    @has_mod_role()
    async def ignore_channel(self, ctx, channel: discord.TextChannel):
        server_id = str(ctx.guild.id)
        channel_id = str(channel.id)
    
        ignored_channels = self.spam_pressure.setdefault(
            server_id, {}).setdefault('ignored_channels', [])
    
        if channel_id not in ignored_channels:
            ignored_channels.append(channel_id)
            await ctx.send(f"Ignoring messages in {channel.mention}")
        else:
            await ctx.send(f"Messages in {channel.mention} are already being ignored.")
    
        # Save the updated ignored channels to the JSON file.
        with open("spam_pressure.json", "w") as f:
            json.dump(self.spam_pressure, f)

    @commands.command()
    @has_mod_role()
    async def unignore_channel(self, ctx, channel: discord.TextChannel):
        server_id = str(ctx.guild.id)
        channel_id = str(channel.id)

        ignored_channels = self.spam_pressure.setdefault(
            server_id, {}).setdefault('ignored_channels', [])
        if channel_id in ignored_channels:
            ignored_channels.remove(channel_id)
            await ctx.send(f"Messages from {channel.mention} will no longer be ignored.")
            # Save the updated ignored channels to the JSON file.
            with open('spam_pressure.json', 'w') as f:
                json.dump(self.spam_pressure, f)
        else:
            await ctx.send(f"{channel.mention} is not being ignored.")
    
    @commands.command()
    @has_mod_role()
    async def unignore_role(self, ctx, role: discord.Role):
        server_id = str(ctx.guild.id)
        role_id = str(role.id)

        ignored_roles = self.spam_pressure.setdefault(
            server_id, {}).setdefault('ignored_roles', [])
        if role_id in ignored_roles:
            ignored_roles.remove(role_id)
            await ctx.send(f"Messages from members with the role {role.mention} will no longer be ignored.")
            # Save the updated ignored roles to the JSON file.
            with open('spam_pressure.json', 'w') as f:
                json.dump(self.spam_pressure, f)
        else:
            await ctx.send(f"Messages from members with the role {role.mention} are not being ignored.")
