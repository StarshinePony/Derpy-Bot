from discord import app_commands
from discord.ext import commands
import discord
import random
import asyncio
import os
import sqlite3
from dotenv import load_dotenv
from datetime import datetime, timedelta
import dateutil.parser
import json


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
            await ctx.send("Pls run d!setup first!")
        return False

    return commands.check(predicate)


class warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_connection_settings = sqlite3.connect("settings.db")
        self.db_connection_settings.row_factory = sqlite3.Row
        self.db_cursor_settings = self.db_connection_settings.cursor()
        self.create_table_settings()

        self.db_connection_warnings = sqlite3.connect("warnings.db")
        self.db_connection_warnings.row_factory = sqlite3.Row
        self.db_cursor_warnings = self.db_connection_warnings.cursor()
        self.create_table_warnings()

    def create_table_settings(self):
        query = """
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            log_channel_id INTEGER,
            server_id INTEGER
        )
        """
        self.db_cursor_settings.execute(query)
        self.db_connection_settings.commit()

    def create_table_warnings(self):
        query = """
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            reason TEXT,
            timestamp DATETIME,
            expiration DATETIME,
            server_id INTEGER
        )
        """
        self.db_cursor_warnings.execute(query)
        self.db_connection_warnings.commit()

    @commands.command(name="warn", help="Warn a Member")
    @has_mod_role()
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        server_id = ctx.guild.id

        current_time = datetime.now()
        expiration_time = current_time + timedelta(hours=12)
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

        query = "INSERT INTO warnings (user_id, reason, timestamp, expiration, server_id) VALUES (?, ?, ?, ?, ?)"
        values = (member.id, reason, timestamp, expiration_time, server_id)
        self.db_connection_warnings.execute(query, values)
        self.db_connection_warnings.commit()

        num_warnings = self.get_warning_count(member, server_id)
        await ctx.send(f"{member.mention} got warned. Reason: {reason}")

        if num_warnings >= 3:
            await ctx.guild.kick(member, reason="3 warns reached")

    @commands.command(name="listwarns", help="Get a list of the warns from a user")
    @has_mod_role()
    async def listwarns(self, ctx, member: discord.Member):
        server_id = ctx.guild.id

        query = "SELECT * FROM warnings WHERE user_id = ? AND server_id = ?"
        values = (member.id, server_id)
        result = self.db_cursor_warnings.execute(query, values).fetchall()

        if not result:
            await ctx.send(f"{member.mention} doesn't have any warnings.")
            return

        embed = discord.Embed(
            title=f"Warnings for {member.display_name}", color=discord.Color.orange())

        for row in result:
            timestamp_str = row["timestamp"]
            reason = row["reason"]
            expiration_str = row["expiration"]
            current_time = datetime.now()

            timestamp = dateutil.parser.parse(timestamp_str)
            expiration = dateutil.parser.parse(expiration_str)

            duration = expiration - timestamp
            remaining_time = expiration - current_time

            days = duration.days
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            tage = remaining_time.days
            hourss, remainderr = divmod(remaining_time.seconds, 3600)
            minutess, _ = divmod(remainderr, 60)

            duration_str = f"{days} Days, {hours} Hours, {minutes} Minutes"
            remaining_time_str = f"{tage} Days, {hourss} Hours, {minutess} Minutes"

            embed.add_field(name="Duration", value=duration_str, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Remaining",
                            value=remaining_time_str, inline=False)

        await ctx.send(embed=embed)

    def get_warning_count(self, member, server_id):
        query = "SELECT COUNT(*) FROM warnings WHERE user_id = ? AND server_id = ?"
        values = (member.id, server_id)
        result = self.db_cursor_warnings.execute(query, values).fetchone()
        return result[0]

    @commands.command(name="logchannel", help="Setup command for logs")
    @has_mod_role()
    async def logchannel(self, ctx, *, channel: discord.TextChannel):
        server_id = ctx.guild.id

        query = "SELECT * FROM settings WHERE server_id = ?"
        result = self.db_cursor_settings.execute(query, (server_id,))
        existing_entry = result.fetchone()

        if existing_entry:
            query = "UPDATE settings SET log_channel_id = ? WHERE server_id = ?"
            values = (channel.id, server_id)
        else:
            query = "INSERT INTO settings (log_channel_id, server_id) VALUES (?, ?)"
            values = (channel.id, server_id)

        self.db_cursor_settings.execute(query, values)
        self.db_connection_settings.commit()

        log_message = f"Logchannel was set to {channel.mention}"
        await self.log_activity(ctx, log_message)

        await ctx.send(log_message)

    @commands.command(name="delwarns", help="Delete the warns of a user")
    @has_mod_role()
    async def delwarns(self, ctx, member: discord.Member):
        server_id = ctx.guild.id
        query = "DELETE FROM warnings WHERE user_id = ? AND server_id = ?"
        self.db_cursor_warnings.execute(query, (member.id, server_id))
        self.db_connection_warnings.commit()
        await ctx.send(f"Warnings of {member.mention} got deleted")

    async def check_expired_warnings(self):
        while True:
            server_ids = set()

            query = "SELECT * FROM warnings WHERE expiration <= ?"
            current_time = datetime.now()
            expired_warnings = self.db_cursor_warnings.execute(
                query, (current_time,)).fetchall()

            for warning in expired_warnings:
                server_id = warning["server_id"]
                server_ids.add(server_id)
                warning_id = warning["id"]
                delete_query = "DELETE FROM warnings WHERE id = ?"
                self.db_cursor_warnings.execute(delete_query, (warning_id,))
                self.db_connection_warnings.commit()
                print("Warning deleted")

            await asyncio.sleep(5)
