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
load_dotenv()

developer_id = int(os.getenv("developerid"))
server_id = int(os.getenv("authserver"))

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


class economy(commands.Cog):
    authserver = os.getenv("authserver")
    developerid = os.getenv("developerid")

    def __init__(self, bot):
        self.bot = bot

        self.db_connection_economy = sqlite3.connect("economy.db")
        self.db_connection_economy.row_factory = sqlite3.Row
        self.db_cursor_economy = self.db_connection_economy.cursor()
        self.create_table_economy()

        self.db_connection_economytimer = sqlite3.connect("economytimer.db")
        self.db_connection_economytimer.row_factory = sqlite3.Row
        self.db_cursor_economytimer = self.db_connection_economytimer.cursor()
        self.create_table_economytimer()

        self.db_connection_items = sqlite3.connect("items.db")
        self.db_connection_items.row_factory = sqlite3.Row
        self.db_cursor_items = self.db_connection_items.cursor()
        self.create_table_items()

        self.db_connection_user_items = sqlite3.connect("user_items.db")
        self.db_connection_user_items.row_factory = sqlite3.Row
        self.db_cursor_user_items = self.db_connection_user_items.cursor()
        self.create_table_user_items()

        self.db_connection_worktime = sqlite3.connect("worktime.db")
        self.db_connection_worktime.row_factory = sqlite3.Row
        self.db_cursor_worktime = self.db_connection_worktime.cursor()
        self.create_table_worktime()

    def create_table_economy(self):
        query = """
        CREATE TABLE IF NOT EXISTS economy (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            money INTEGER,
            level INTEGER,
            server_id INTEGER
        )
        """
        self.db_cursor_economy.execute(query)
        self.db_connection_economy.commit()

    def create_table_economytimer(self):
        query = """
        CREATE TABLE IF NOT EXISTS economytimer (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            reason TEXT,
            timestamp DATETIME,
            expiration DATETIME,
            server_id INTEGER
        )
        """
        self.db_cursor_economytimer.execute(query)
        self.db_connection_economytimer.commit()

    def create_table_items(self):
        query = """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price INTEGER
        )
        """
        self.db_cursor_items.execute(query)
        self.db_connection_items.commit()

    def create_table_user_items(self):
        query = """
        CREATE TABLE IF NOT EXISTS user_items (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            item_name TEXT,
            server_id INTEGER
        )
        """
        self.db_cursor_user_items.execute(query)
        self.db_connection_user_items.commit()

    def create_table_worktime(self):
        query = """
        CREATE TABLE IF NOT EXISTS worktime (
            id INTEGER PRIMARY KEY,
            worktime INTEGER,
            server_id INTEGER
        )
        """
        self.db_cursor_worktime.execute(query)
        self.db_connection_worktime.commit()

    @commands.hybrid_command(name="additem", with_app_command=True, help="Adds a new Item globaly")
    @app_commands.guilds(discord.Object(id=server_id))
    async def additem(self, ctx, *, name: str, price: int):
        print("logging")
        user_id = ctx.author.id
        if int(user_id) == int(developer_id):

            print("adding")
            query = "INSERT INTO items (name, price) VALUES (?, ?)"
            self.db_cursor_items.execute(query, (name, price))
            self.db_connection_items.commit()

            await ctx.send(f"Item added globaly: Name: {name} Price: {price}")

        else:
            await ctx.send(f"Only the Developer can run this command")

    @commands.command(name="removeitem", help="Removes items globaly")
    async def removeitem(self, ctx, *, id=None):
        user_id = ctx.author.id
        if int(user_id) == int(developer_id):
            if id == None:
                query = "SELECT * from items"
                results = self.db_cursor_items.execute(query).fetchall()

                embed = discord.Embed(
                    title="IDs", description="Available item ids:", color=discord.Color.red())

                for row in results:
                    id = row["id"]
                    item_name = row["name"]

                    embed.add_field(
                        name=id, value=f"Name: {item_name}", inline=False)

                await ctx.send(embed=embed)
            else:
                print(id)
                query = "DELETE FROM items WHERE id = ?"
                self.db_cursor_items.execute(query, (id))
                self.db_connection_items.commit()
                await ctx.send(f"Item with id **{id}** got deleted")

        else:
            await ctx.send(f"Only the developer can run this command")

    @commands.command(name="ecogive", help="Gives a user money")
    @has_mod_role()
    async def ecogive(self, ctx, member: discord.Member):
        member_id = member.id
        server_id = ctx.guild.id
        def check(message):
                return message.content
        await ctx.send("Please enter the amount of bits to add to the user:")
        message = await self.bot.wait_for('message', check=check)
        money = int(message.content)
        query = "SELECT * FROM economy WHERE user_id = ? AND server_id = ?"
        result = self.db_cursor_economy.execute(
            query, (member_id, server_id)).fetchone()

        if result:
            current_money = result["money"]
            new_money = current_money + money

            query = "UPDATE economy SET money = ? WHERE user_id = ? AND server_id = ?"
            self.db_cursor_economy.execute(
                query, (new_money, member_id, server_id))
            self.db_connection_economy.commit()

            await ctx.send(f"{money} bits has been given to {member.mention}")
        else:
            query = "INSERT INTO economy (user_id, money, level, server_id) VALUES (?, ?, ?, ?)"
            self.db_cursor_economy.execute(
                query, (member_id, money, 1, server_id))
            self.db_connection_economy.commit()

            await ctx.send(f"{money} bits has been given to {member.mention}")

    @commands.command(name="worktimer", help="Sets the work time in minutes")
    @has_mod_role()
    async def worktimer(self, ctx, *, worktime=None):
        if worktime < 1:
            ctx.send("Worktime can't be smaller than 1")
        else:
            server_id = ctx.guild.id

            query = "SELECT * FROM worktime WHERE server_id = ?"
            result = self.db_cursor_worktime.execute(
                query, (server_id,)).fetchone()

            if worktime is None:
                if result:
                    bumms = result["worktime"]
                    await ctx.send(f"Work cooldown is {bumms}")
                else:
                    await ctx.send("No workcooldown was set. The default cooldown is 1 hour")
            else:
                if result:
                    update_query = "UPDATE worktime SET worktime = ? WHERE server_id = ?"
                    self.db_cursor_worktime.execute(
                        update_query, (worktime, server_id))
                    self.db_connection_worktime.commit()
                    await ctx.send(f"Worktime was set to {worktime} minutes")

                else:
                    insert_query = "INSERT INTO worktime (worktime, server_id) VALUES (?, ?)"
                    self.db_cursor_worktime.execute(
                        insert_query, (worktime, server_id))
                    self.db_connection_worktime.commit()
                    await ctx.send(f"Worktime was set to {worktime} minutes")

    @commands.command(name="work", help="You can work every hour")
    async def work(self, ctx):
        user_id = ctx.author.id
        server_id = ctx.guild.id
        current_time = datetime.now()
        query3 = "SELECT * FROM worktime WHERE server_id = ?"
        lul = self.db_connection_worktime.execute(
            query3, (server_id,)).fetchone()
        if lul:
            worktime = lul["worktime"]
        else:
            worktime = 60

        expiration_time = current_time + timedelta(minutes=worktime)
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        ok = "Arbeit"
        level2 = random.randint(1600, 2200)
        level3 = random.randint(2200, 3100)
        level4 = random.randint(3100, 4300)

        query = "SELECT * FROM economytimer WHERE user_id = ? AND server_id = ?"
        values = (user_id, server_id)
        result = self.db_cursor_economytimer.execute(query, values).fetchall()
        embed = discord.Embed(title="Work", color=discord.Color.orange())
        for row in result:
            timestamp_str = row["timestamp"]
            expiration_str = row["expiration"]
            current_time = datetime.now()

            timestamp = dateutil.parser.parse(timestamp_str)
            expiration = dateutil.parser.parse(expiration_str)

            duration = expiration - timestamp
            remaining_time = expiration - current_time

            hours, remainder = divmod(duration.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            hourss, remainderr = divmod(remaining_time.seconds, 3600)
            minutess, _ = divmod(remainderr, 60)

            duration_str = f"{hours} Hours, {minutes} Minutes"
            remaining_time_str = f"{hourss} Hours, {minutess} Minutes"

            embed.add_field(name="Duration of work",
                            value=duration_str, inline=False)
            embed.add_field(name="Remaining time",
                            value=remaining_time_str, inline=False)

        if result:
            await ctx.send(embed=embed)
        else:

            query = "SELECT * FROM economy WHERE user_id = ? AND server_id = ?"
            result = self.db_cursor_economy.execute(
                query, (user_id, server_id)).fetchone()
            if result and result["level"] >= 20:
                geld = level2
                if result["level"] == 20:
                    await ctx.send("You are now worker lvl 2")
            else:
                geld = random.randint(900, 1200)
            if result and result["level"] >= 60:
                geld = level3
                if result["level"] == 60:
                    await ctx.send("You are now worker lvl 3")
            else:
                geld = random.randint(900, 1200)

            if result and result["level"] >= 120:
                geld = level4
                if result["level"] == 120:
                    await ctx.send("You are now worker lvl 4")
            else:
                geld = random.randint(900, 1200)

            if result:
                money = result["money"] + geld
                level = result["level"] + 1
                query = "UPDATE economy SET money = ? WHERE user_id = ? AND server_id = ?"
                query2 = "UPDATE economy SET level = ? WHERE user_id = ? AND server_id = ?"
                self.db_cursor_economy.execute(
                    query, (money, user_id, server_id))
                self.db_connection_economy.commit()
                self.db_cursor_economy.execute(
                    query2, (level, user_id, server_id))
                self.db_connection_economy.commit()

            else:
                query = "INSERT INTO economy (user_id, money, level, server_id) VALUES (?, ?, ?, ?)"
                self.db_cursor_economy.execute(
                    query, (user_id, geld, 1,  server_id))
                self.db_connection_economy.commit()

            query = "INSERT INTO economytimer (user_id, reason, timestamp, expiration, server_id) VALUES (?, ?, ?, ?, ?)"
            self.db_cursor_economytimer.execute(
                query, (user_id, ok, timestamp, expiration_time, server_id))
            self.db_connection_economytimer.commit()

            query = "SELECT * FROM economy WHERE user_id = ? AND server_id = ?"
            result = self.db_cursor_economy.execute(
                query, (user_id, server_id)).fetchone()
            money = result["money"]

            await ctx.send(f"Work was succesful! (+{geld} Bits!) Your bits: {money} Bits")

    @commands.command(name="money", help="Your money")
    async def money(self, ctx, member: discord.Member = None):
        server_id = ctx.guild.id
        if member == None:
            user_id = ctx.author.id
        else:
            user_id = member.id
            print(member)

        query = "SELECT * FROM economy WHERE user_id = ? AND server_id = ?"
        result = self.db_cursor_economy.execute(
            query, (user_id, server_id)).fetchone()
        if member == None:
            if result:
                money = result["money"]
                await ctx.send(f"Your current amount of Bits: {money} Bits.")
            else:
                await ctx.send("Du hast noch kein Geld.")
        else:
            if result:
                money = result["money"]
                await ctx.send(f"The current amount of Bits of the user {member.mention} is: {money} Bits.")
            else:
                await ctx.send(f"{member.mention} doesn't have any Bits")

    @commands.command(name="shop", help="Shows the shop")
    async def shop(self, ctx):
        query = "SELECT * FROM items"
        results = self.db_cursor_items.execute(query).fetchall()

        if results:
            embed = discord.Embed(
                title="Shop", description="Available items:", color=discord.Color.blue())

            for row in results:
                item_name = row["name"]
                item_price = row["price"]

                embed.add_field(
                    name=item_name, value=f"Price: {item_price} Bits", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("There aren't any items in the shop")

    @commands.command(name="removemoney", help="Remove money from a user")
    @has_mod_role()
    async def removemoney(self, ctx, member: discord.Member):
        server_id = ctx.guild.id
        member_id = member.id
        def check(message):
                return message.content
        await ctx.send("Please enter the amount of bits to remove from the user:")
        message = await self.bot.wait_for('message', check=check)
        bits = int(message.content)
        query = "SELECT * FROM economy WHERE user_id = ? AND server_id = ?"
        result = self.db_cursor_economy.execute(
            query, (member_id, server_id)).fetchone()
        if result:

            money1 = result["money"]

            if bits > money1:
                await ctx.send("The user doesn't have that much money")
            else:

                money_after_payment1 = money1 - bits
                query = "UPDATE economy SET money = ? WHERE user_id = ? AND server_id = ?"
                self.db_cursor_economy.execute(
                    query, (money_after_payment1, member_id, server_id))
                self.db_connection_economy.commit()
                await ctx.send(f"Removing {bits} from {member.mention}")

    @commands.command(name="pay", help="Pay a user some bits")
    async def pay(self, ctx, member: discord.Member, bits: int):
        if bits < 0:
            ctx.send("DONT EVEN DARE TO TRY THIS")
        else:
            server_id = ctx.guild.id
            user_id = ctx.author.id
            member_id = member.id
            query = "SELECT * FROM economy WHERE user_id = ? AND server_id = ?"
            query2 = "SELECT * FROM economy WHERE user_id = ? AND server_id = ?"
            result = self.db_cursor_economy.execute(
                query, (user_id, server_id)).fetchone()
            result2 = self.db_cursor_economy.execute(
                query2, (member_id, server_id)).fetchone()
            if member_id == user_id:
                ctx.send("Don't dupe mone")
            else:
                if result:

                    money1 = result["money"]
                    if result2:
                        money2 = result2["money"]
                    else:
                        money2 = 0
                        level2 = 0
                    if money1 < bits:
                        await ctx.send("You dont have enough money to pay that amount!")
                    else:

                        money_after_payment1 = money1 - bits
                        money_after_payment2 = money2 + bits
                        query = "UPDATE economy SET money = ? WHERE user_id = ? AND server_id = ?"
                        self.db_cursor_economy.execute(
                            query, (money_after_payment1, user_id, server_id))
                        self.db_connection_economy.commit()
                        await ctx.send(f"Paying {bits} to {member.mention}")

                        if result2:
                            query2 = "UPDATE economy SET money = ? WHERE user_id = ? AND server_id = ?"
                            self.db_cursor_economy.execute(
                                query2, (money_after_payment2, member_id, server_id))
                            self.db_connection_economy.commit()
                            await ctx.send(f"Removing bits from <@{user_id}>...")
                            await ctx.send(f"Payment was successful")
                        else:
                            query2 = "INSERT INTO economy (user_id, money, level, server_id) VALUES (?, ?, ?, ?)"
                            self.db_cursor_economy.execute(
                                query2, (member_id, money_after_payment2, level2,  server_id))
                            self.db_connection_economy.commit()
                            await ctx.send(f"Removing bits from <@{user_id}>...")
                            await ctx.send(f"Payment was successful")

    @commands.command(name="buy", help="Buy an item")
    async def buy(self, ctx, name: str):
        server_id = ctx.guild.id

        # Check if the item is available in the shop
        query = "SELECT * FROM items WHERE name = ?"
        result = self.db_cursor_items.execute(query, (name,)).fetchone()

        if result:
            item_price = result["price"]
            user_id = ctx.author.id

            # Check if the user has enough money to buy the item
            query = "SELECT * FROM economy WHERE user_id = ? AND server_id = ?"
            query2 = "SELECT * FROM user_items WHERE user_id = ? AND item_name = ? AND server_id = ?"
            result = self.db_cursor_economy.execute(
                query, (user_id, server_id)).fetchone()
            result2 = self.db_cursor_user_items.execute(
                query2, (user_id, name, server_id)).fetchone()

            if result:
                user_money = result["money"]
                if result2:
                    await ctx.send("You already have this item")
                else:
                    if user_money >= item_price:
                        # Update the user's money after the purchase
                        new_money = user_money - item_price
                        query = "UPDATE economy SET money = ? WHERE user_id = ? AND server_id = ?"
                        self.db_cursor_economy.execute(
                            query, (new_money, user_id, server_id))
                        self.db_connection_economy.commit()

                        # Add the purchased item to the user's inventory
                        query = "INSERT INTO user_items (user_id, item_name, server_id) VALUES (?, ?, ?)"
                        self.db_cursor_user_items.execute(
                            query, (user_id, name, server_id))
                        self.db_connection_user_items.commit()

                        await ctx.send(f"You bought the item '{name}' for {item_price} Bits.")
                    else:
                        await ctx.send("You can't afford this item")
            else:
                await ctx.send("You don't have an entry in the database")
        else:
            await ctx.send(f"The item '{name}' is not available")

    @commands.command(name="use", help="Buy an item")
    async def use_item(self, ctx, item_name, member: discord.Member = None):
        server_id = ctx.guild.id
        #    Überprüfe, ob der Benutzer das Item besitzt
        query = "SELECT * FROM user_items WHERE user_id = ? AND item_name = ? AND server_id = ?"
        values = (ctx.author.id, item_name, server_id)
        result = self.db_cursor_user_items.execute(query, values).fetchone()

        if result:
            if item_name == "Pony":
                pony_role = discord.utils.get(ctx.guild.roles, name="Best Pony")
                if not pony_role:
                    pony_role = await ctx.guild.create_role(name="Best Pony", reason = "Pony role creation")
                    await ctx.send("Failed try again (Role created)")
                else:
                    await ctx.send(f"Your Pony booped {member.mention}")
                    delete_query = "DELETE FROM user_items WHERE id = ?"
                    self.db_cursor_user_items.execute(
                        delete_query, (result["id"],))
                    self.db_connection_user_items.commit()
                    boop_duration = 3000
                    await member.add_roles(pony_role, reason="Booped!")
                    await asyncio.sleep(boop_duration)
                    await member.remove_roles(pony_role, reason="Boop Cooldown Ended!")
            if item_name == "Bomb":
                # Füge dem Benutzer die Rolle "Timeout" hinzu für 5 Minuten
                timeout_role = discord.utils.get(
                    ctx.guild.roles, name="Timeout")
                if not timeout_role:
                    timeout_role = await ctx.guild.create_role(name="Timeout", reason="Timeout role for the bot")
                    await ctx.send("There wasn't any timeout role available. Role has been created now! Rerun the command to use the item")
                else:
                    await ctx.send(f"You succesfully dropped the '{item_name}'")
                    # Lösche das Item aus der Datenbank, da es nur einmal benutzt werden kann
                    delete_query = "DELETE FROM user_items WHERE id = ?"
                    self.db_cursor_user_items.execute(
                        delete_query, (result["id"],))
                    self.db_connection_user_items.commit()
                    timeout_seconds = 300
                    await member.add_roles(timeout_role, reason="Bomb used (5 min Timeout)")
                    await ctx.send(f"{member.mention} cya in 5 mins lol")

                    await asyncio.sleep(timeout_seconds)

                    await member.remove_roles(timeout_role, reason="Timeout expired")
            else:
                ctx.send("You can't use that item")

        else:
            await ctx.send(f"You don't own '{item_name}'")

    @commands.command(name="inventory", help="Your inventory")
    async def inventory(self, ctx, member: discord.Member = None):
        if member == None:
            user_id = ctx.author.id
        else:
            user_id = member.id
            print(member)

        server_id = ctx.guild.id
        query = "SELECT * FROM user_items WHERE user_id = ? AND server_id = ?"
        result = self.db_cursor_user_items.execute(
            query, (user_id, server_id)).fetchall()

        if result:

            items = [row["item_name"] for row in result]

            embed = discord.Embed(
                title="Inventory", description="Your current inventory", color=discord.Color.blue())
            embed.add_field(name="Items", value=", ".join(items), inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Your inventory is empty")

    async def check_expired_worktimers(self):
        while True:
            server_ids = set()

            query = "SELECT * FROM economytimer WHERE expiration <= ?"
            current_time = datetime.now()
            expired_timers = self.db_cursor_economytimer.execute(
                query, (current_time,)).fetchall()

            for economytimer in expired_timers:
                server_id = economytimer["server_id"]
                server_ids.add(server_id)
                timer_id = economytimer["id"]
                delete_query = "DELETE FROM economytimer WHERE id = ?"
                self.db_cursor_economytimer.execute(delete_query, (timer_id,))
                self.db_connection_economytimer.commit()
                print(f"The id '{timer_id}' finished working")
            await asyncio.sleep(5)
