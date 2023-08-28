from discord.ext import commands
import discord
import json
import os
import sys
import select
import time

def has_mod_role():
    async def predicate(ctx):
        # Load the setup data from JSON file
        if os.path.exists('setup_data.json'):
            try:
                with open('setup_data.json', 'r') as file:
                    setup_data = json.load(file)

                guild_id = ctx.guild.id
                setup_info = setup_data.get(str(guild_id), None)

                mod_role_id = setup_info.get("mod_role_id", None)
                if mod_role_id:
                    mod_role = discord.utils.get(ctx.guild.roles, id=mod_role_id)
                    if mod_role is not None and mod_role in ctx.author.roles:
                        return True
                    else:
                        await ctx.send("You do not have the required moderation permissions to run this command!")
                        return False
                else:
                    await ctx.send("there was a problem reading 'setup_data.json' run '" + str(ctx.prefix) + "setup' to reset it")
            except (json.decoder.JSONDecodeError, FileNotFoundError):
                await ctx.send("there was a problem reading 'setup_data.json' run '" + str(ctx.prefix) + "setup' to reset it")
        else:
            await ctx.send("Pls run " + str(ctx.prefix) + "setup first!")

        return False

    return commands.check(predicate)

def timed_input(prompt, timeout):
    print(prompt)
    start_time = time.time()

    while True:
        if time.time() - start_time > timeout:
            print(str(timeout) + " seconds timeout reached, continuing flow to not stall the bot")
            return None
        inputs = [sys.stdin]
        readable, _, _ = select.select(inputs, [], [], timeout)
    
        if sys.stdin in readable:
            return sys.stdin.readline().rstrip()