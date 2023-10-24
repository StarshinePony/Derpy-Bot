from discord import app_commands
from discord.ext import commands
import discord
import random
import asyncio
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from datetime import datetime, timedelta
from modules.backend import has_mod_role, timed_input
load_dotenv()

developer_id = int(os.getenv("developerid"))
server_id = int(os.getenv("authserver"))


class economy(commands.Cog):
    authserver = os.getenv("authserver")
    developerid = os.getenv("developerid")
    FIRST_HOUR_SLOT = 452558
    UPDATE_SLOT = 460970
    def __init__(self, bot):
        self.bot = bot
        slot_data = {
            "current_hour_slot": 452558,
            "update_slot": 460970
        }
        init_data = {
            "economy": [],
            "economytimer": [],
            "items": [],
            "user_items": [],
            "worktime": [],
            "stocks":  []
        }
        
        

                    
        with open("slot_data.json", "w") as json_file:
                json.dump(slot_data, json_file)
                self.slot_data = slot_data
                print("created slot_data.json")
            
        try:

            #tests to ensure all categories are here
            with open("economy_data.json", "r") as json_file:
                data = json.load(json_file)
                if (("economy" in data) and ("economytimer" in data) and ("items" in data) and ("user_items" in data) and ("worktime" in data) and ("stocks" in data)):
                    self.data = data
                    return
                else:
                    #triggers when a category is missing
                    user_input = timed_input("\033[31melements missing from economy_data.json: reset database? y/n\033[0m", 15)
                    while (user_input != "y" and user_input != "n" and user_input != None):
                        user_input = input("\033[31mreset database? y/n\n\033[0m")
                    if user_input == "y":
                        with open("economy_data.json", "w") as json_file:
                            json.dump(init_data, json_file)
                        self.data = init_data
                        print("\033[30;42mdatabase was reset\033[0m")
                    else:
                        print("\033[101mdatabse will have to be fixed manually or reset during next restart\033[0m")
        except (FileNotFoundError):
            #triggers when file doesn't exist
            with open("economy_data.json", "w") as json_file:
                json.dump(init_data, json_file)
            self.data = init_data
            print("created economy_data.json")
        except (json.decoder.JSONDecodeError):
            #triggers when file is invalid
            user_input = timed_input("\033[31merror reading from economy_data.json, file might be corrupted or mistyped: reset database? y/n\033[0m", 15)
            while (user_input != "y" and user_input != "n" and user_input != None):
                user_input = input("\033[31mreset database? y/n\033[0m")
            if user_input == "y":
                with open("economy_data.json", "w") as json_file:
                    json.dump(init_data, json_file)
                self.data = init_data
                print("\033[30;42mdatabase was reset\033[0m")
            else:
                print("\033[101mdatabse will have to be fixed manually or reset during next restart\033[0m")
    def save_slot(self):
        with open('slot_data.json', 'w') as file:
            json.dump(self.slot_data, file)

    def load_slot(self):
        try:
            with open('slot_data.json', 'r') as file:
                self.slot_data = json.load(file)
        except (json.decoder.JSONDecodeError, FileNotFoundError):
            pass
    def save_json(self):
        with open("economy_data.json", "w") as json_file:
            json.dump(self.data, json_file)

    def load_data(self):
        with open("economy_data.json", "r") as json_file:
            self.data = json.load(json_file)
    async def update_hour_slot(self):
        while True:
            self.load_slot()
            current_hour = self.slot_data['current_hour_slot']
            reset = self.slot_data['update_slot']
            if current_hour == reset:
                print("Reset")
                self.slot_data['current_hour_slot'] = reset
            else:
                next_hour_slot = current_hour + 1
                print(next_hour_slot)
                self.slot_data['current_hour_slot'] = next_hour_slot
            self.save_slot()
            await asyncio.sleep(0.5)
            
    async def calculate_price_change(self, value, starting_price):
        with open('slot_data.json', 'r') as file:
            slot = json.load(file)
            if slot:
                print("All there")
            hour_slot: int = slot['current_hour_slot']
            update_slot: int = slot['update_slot']
            multi = 1.0 - abs(random.gauss(0, 0.025))
        
            if hour_slot <= update_slot:
                if random.choice([True, False]):
                    multi = 1.0 / multi
            else:
                threshold = 0.52 if value > starting_price else 0.48
                if random.random() > threshold:
                    multi = 1.0 / multi
            
            value = float(value) 
            multi = float(multi)           
            return value * multi
    async def update_stock_prices(self):
        while True:
            self.load_data()  
            for stock in self.data.get("stocks", []):
                value: int = stock['current_price']
                starting_price: int = stock["avg_price"]
                price_change = await self.calculate_price_change(value=value, starting_price=starting_price)
                stock['current_price'] = price_change
                stock['history'].append(stock['current_price'])
                print(price_change)
                if len(stock['history']) > 240000:
                    stock['history'].pop(1)
                    print("Worked")
                else:
                    gugu: int = len(stock['history'])
                    
                    print("Didn't work")
                    print(gugu)

            self.save_json() 
            await asyncio.sleep(0.2)  
    
    @commands.hybrid_command(name="addstock", with_app_command=True, help="Adds a new stock to the marked")
    async def add_stock(self, ctx, name: str, avg_price: float):
    
        for stock in self.data["stocks"]:
            if stock['name'] == name:
                await ctx.send(f"A stock with the name '{name}' already exists.")
                return

    
        self.data["stocks"].append({
            'name': name,
            'avg_price': avg_price,
            'current_price': avg_price,
            'history': [avg_price] * 24 
        })
        self.save_json()
        await ctx.send(f"New stock '{name}' with an average price of {avg_price} has been added.")
    @commands.command(name="market", help = "Shows the share market")
    async def market(self, ctx):
        self.load_data()
        results = [values for values in self.data['stocks']]

        if results:
            embed = discord.Embed(
                title="Share Market", description="Available companies:", color=discord.Color.blue())

            for row in results:
                item_name = row["name"]
                item_price = row["current_price"]

                embed.add_field(
                    name=item_name, value=f"Price: {item_price} Bits", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("There aren't any items in the shop")
    @commands.command(name="share_info", help="Get information about a share")
    async def stock_info(self, ctx, stock_name = None):
        self.load_data()
        user_id = ctx.author.id
        server_id = ctx.guild.id
        user_entry = next((values for values in self.data['economy'] if values['user_id'] == user_id and values['server_id'] == server_id), None)
        owned_shares = user_entry.get('stocks', {})
        print(owned_shares)
        try:
            stocks = self.data.get("stocks", [])  
            if stock_name == None:
                await ctx.send("Please provide a stock type")
            else:
                


           
                for stock in stocks:
                    share_current_price = stock['current_price']
                    
                    if stock_name in owned_shares:
                    # Get the number of shares owned by the user for the specified stock type
                        shares_owned = owned_shares[stock_name]
                        total = shares_owned * share_current_price
                        await ctx.send(f"You own {shares_owned} shares of {stock_name} for a total worth of {total} bits.")
                    else:
                        await ctx.send(f"You don't own any shares of {stock_name}.")
                    if stock["name"] == stock_name:
                        history = stock.get("history", [])
                
                    
                        past_7_days = history

                        if not past_7_days:
                            
                            price = stock.get("avg_price", 0)
                            await ctx.send(f"No price history available for stock '{stock_name}'. Using average price: {price}")
                            return

                    
                        x = np.arange(len(past_7_days))
                        y = np.array(past_7_days)

                    
                        plt.plot(x, y)
                        plt.xlabel("Hours")
                        plt.ylabel("Share Price")
                        plt.title(f"Share Price History for {stock_name}")

                    
                        plt.savefig("stock_graph.png")
                        plt.close()

                    
                        name = stock['name']
                        share_price = stock['current_price']
                        await ctx.send(f"Current Price of '{name}': {share_price} bits.")
                        with open("stock_graph.png", "rb") as image_file:
                            await ctx.send(file=discord.File(image_file))

                    
                        os.remove("stock_graph.png")

                        return

            
            await ctx.send(f"Stock '{stock_name}' not found.")
        except Exception as e:
            print(e)
            await ctx.send("An error occurred while fetching stock data.")

    @commands.command(name="sell_share", help="Sell shares of a stock")
    async def sell_share(self, ctx, stock_name: str, shares_to_sell: int):
        self.load_data()

        server_id = ctx.guild.id
        user_id = ctx.author.id

        
        stock = [values for values in self.data['stocks'] if values['name'] == stock_name]

        if not stock:
            await ctx.send("Company not found.")
            return

        stock = stock[0] 

        
        user_entry = [values for values in self.data['economy'] if values['user_id'] == user_id and values['server_id'] == server_id]

        if not user_entry:
            await ctx.send("You don't have an economy entry. Please work first.")
            return

        user_entry = user_entry[0] 

        if 'stocks' not in user_entry or stock_name not in user_entry['stocks']:
            await ctx.send(f"You don't own any shares of {stock_name}.")
            return

        owned_shares = user_entry['stocks'][stock_name]

        if shares_to_sell <= 0:
            await ctx.send("Please enter a valid number of shares to sell.")
            return

        if shares_to_sell > owned_shares:
            await ctx.send(f"You don't have enough shares of {stock_name} to sell {shares_to_sell} shares.")
            return

        
        stock_price = stock['current_price']
        sale_amount = shares_to_sell * stock_price

        
        user_entry['money'] += sale_amount
        user_entry['stocks'][stock_name] -= shares_to_sell
        
        self.save_json()

        await ctx.send(f"You have sold {shares_to_sell} shares of {stock_name} for {sale_amount:.2f} bits. Your balance is now {user_entry['money']:.2f} bits.")

    @commands.command(name="buy_share", help="Buy some shares")
    async def buy_stock_gpt(self, ctx, name: str, shares: int):
        
        self.load_data()

        server_id = ctx.guild.id
        user_id = ctx.author.id

        
        stock = [values for values in self.data['stocks'] if values['name'] == name]

        if not stock:
            await ctx.send("Stock not found.")
            return

        stock = stock[0]  

        stock_price = stock['current_price']

        if shares <= 0:
            await ctx.send("Please enter a valid number of shares to buy.")
            return

        total_cost = shares * stock_price

    
        user_entry = [values for values in self.data['economy'] if values['user_id'] == user_id and values['server_id'] == server_id]

        if not user_entry:
            await ctx.send("You don't have an economy entry. Please set up an economy first.")
            return

        user_entry = user_entry[0]  
        user_balance = user_entry['money']

        if user_balance < total_cost:
            await ctx.send("Insufficient bits.")
            return

       
        user_entry['money'] -= total_cost

        
        if 'stocks' not in user_entry:
            user_entry['stocks'] = {}

        if name not in user_entry['stocks']:
            user_entry['stocks'][name] = shares
        else:
            user_entry['stocks'][name] += shares
       
        
        self.save_json()

        await ctx.send(f"You have bought {shares} shares of {name} for {total_cost:.2f} bits. Your balance is now {user_entry['money']:.2f} bits.")
    
    @commands.hybrid_command(name="additem", with_app_command=True, help="Adds a new Item globaly")
    @app_commands.guilds(discord.Object(id=server_id))
    async def additem(self, ctx, name: str, price: int):
        self.load_data()
        print("logging")
        user_id = ctx.author.id
        if int(user_id) == int(developer_id):

            print("adding")
            free_id = 1
            ids = set()
            for item in self.data["items"]:
                ids.add(item['id'])
            while free_id in ids:
                free_id += 1
            self.data["items"].append({
                "id" : free_id,
                "name" : name,
                "price" : price
            })
            self.save_json()
            
            await ctx.send(f"Item added globaly: Name: {name} Price: {price}")

        else:
            await ctx.send(f"Only the Developer can run this command")

    @commands.command(name="removeitem", help="Removes items globaly")
    async def removeitem(self, ctx, *, id=None):
        self.load_data()
        user_id = ctx.author.id
        if int(user_id) == int(developer_id):
            if id == None:
                elements = self.data["items"]

                embed = discord.Embed(
                    title="IDs", description="Available item ids:", color=discord.Color.red())

                for row in elements:
                    id = row["id"]
                    item_name = row["name"]

                    embed.add_field(
                        name=id, value=f"Name: {item_name}", inline=False)

                await ctx.send(embed=embed)
            else:
                print(id)
                print(self.data['items'])
                for value in self.data['items']:
                    if value['id'] == int(id):
                        self.data['items'].remove(value)
                print(self.data['items'])
                self.save_json()
                await ctx.send(f"Item with id **{id}** got deleted")

        else:
            await ctx.send(f"Only the developer can run this command")

    @commands.command(name="ecogive", help="Gives a user money")
    @has_mod_role()
    async def ecogive(self, ctx, member: discord.Member):
        self.load_data()
        member_id = member.id
        server_id = ctx.guild.id
        def check(message):
                return message.content
        await ctx.send("Please enter the amount of bits to add to the user:")
        message = await self.bot.wait_for('message', check=check)
        money = int(message.content)
        user = [values for values in self.data['economy'] if values['user_id'] == member_id and values['server_id'] == server_id]

        if user:
            user[0]["money"] += money
            self.save_json()

            await ctx.send(f"{money} bits has been given to {member.mention}")
        else:
            self.data["economy"].append({
                "user_id": member_id,
                "money": money,
                "level": 1,
                "server_id": server_id
            })
            self.save_json()

            await ctx.send(f"{money} bits has been given to {member.mention}")

    @commands.command(name="worktimer", help="Sets the work time in minutes")
    @has_mod_role()
    async def worktimer(self, ctx, *, worktime: int = 0):
        self.load_data()
        if worktime < 1:
            await ctx.send("Worktime can't be smaller than 1")
        else:
            server_id = ctx.guild.id
            server = [values for values in self.data['worktime'] if values['server_id'] == server_id]

            if worktime is None:
                if server:
                    bumms = server[0]["worktime"]
                    await ctx.send(f"Work cooldown is {bumms}")
                else:
                    await ctx.send("No workcooldown was set. The default cooldown is 1 hour")
            else:
                if server:
                    server[0]['worktime'] = int(worktime)
                    self.save_json()
                    await ctx.send(f"Worktime was set to {worktime} minutes")

                else:
                    self.data["worktime"].append({
                        "worktime": int(worktime),
                        "server_id": server_id
                    })
                    self.save_json()
                    await ctx.send(f"Worktime was set to {worktime} minutes")

    @commands.command(name="work", help="You can work every hour")
    async def work(self, ctx):
        self.load_data()
        user_id = ctx.author.id
        server_id = ctx.guild.id
        current_time = datetime.now()
        lul = [values for values in self.data['worktime'] if values['server_id'] == server_id]
        if lul:
            worktime = lul[0]["worktime"]
        else:
            worktime = 60

        expiration_time = current_time + timedelta(minutes=worktime)
        export_timestamp = current_time.timestamp()
        ok = "work"
        level2 = random.randint(1600, 2200)
        level3 = random.randint(2200, 3100)
        level4 = random.randint(3100, 4300)

        values = [values for values in self.data['economytimer'] if values['user_id'] == user_id and values['server_id'] == server_id]
        embed = discord.Embed(title="Work", color=discord.Color.orange())
        for row in values:
            current_time = datetime.now()
            timestamp = datetime.fromtimestamp(row["timestamp"])
            expiration = datetime.fromtimestamp(row["expiration"])

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

        if values:
            await ctx.send(embed=embed)
        else:

            values = [values for values in self.data['economy'] if values['user_id'] == user_id and values['server_id'] == server_id]
            if values:
                values = values[0]
            if values and values["level"] >= 20:
                geld = level2
                if values and values["level"] >= 60:
                    geld = level3
                    if values and values["level"] >= 120:
                        geld = level4
                        
            else:
                geld = random.randint(900, 1200)
            if values["level"] == 20:
                await ctx.send("You are now worker lvl 2")
            if values["level"] == 60:
                await ctx.send("You are now worker lvl 3")
            if values["level"] == 120:
                await ctx.send("You are now worker lvl 4")
            if values:
                values["money"] += geld
                values["level"] += 1
                self.save_json()

            else:
                self.data["economy"].append({
                    "user_id": user_id,
                    "money": geld,
                    "level": 1,
                    "server_id": server_id
                })
                self.save_json()

            free_id = 1
            ids = set()
            for item in self.data["economytimer"]:
                ids.add(item['id'])
            while free_id in ids:
                free_id += 1
            self.data["economytimer"].append({
                "id": free_id,
                "user_id": user_id,
                "reason": ok,
                "timestamp": export_timestamp,
                "expiration": expiration_time.timestamp(),
                "server_id": server_id
            })
            self.save_json()

            values = [values for values in self.data['economy'] if values['user_id'] == user_id and values['server_id'] == server_id]
            if values:
                values = values[0]
            money = values["money"]

            await ctx.send(f"Work was successful! (+{geld} Bits!) Your bits: {money} Bits")

    @commands.command(name="money", help="Your money")
    async def money(self, ctx, member: discord.Member = None):
        self.load_data()
        server_id = ctx.guild.id
        if member == None:
            user_id = ctx.author.id
        else:
            user_id = member.id
            print(member)

        result = [values for values in self.data['economy'] if values['user_id'] == user_id and values['server_id'] == server_id]
        if result:
            result = result[0]
        if member == None:
            if result:
                money = result["money"]
                await ctx.send(f"Your current amount of Bits: {money} Bits.")
            else:
                await ctx.send("You don't have any Bits.")
        else:
            if result:
                money = result["money"]
                await ctx.send(f"The current amount of Bits of the user {member.mention} is: {money} Bits.")
            else:
                await ctx.send(f"{member.mention} doesn't have any Bits")

    @commands.command(name="shop", help="Shows the shop")
    async def shop(self, ctx):
        self.load_data()
        results = [values for values in self.data['items']]

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
    async def removemoney(self, ctx, member: discord.Member = None):
        if member == None:
            await ctx.send(f"Missing argument user: Usage: " + str(ctx.prefix) + str(ctx.command) + " @<user>")
            return
        self.load_data()
        server_id = ctx.guild.id
        member_id = member.id
        def check(message):
                return message.content
        await ctx.send("Please enter the amount of bits to remove from the user:")
        message = await self.bot.wait_for('message', check=check)
        bits = int(message.content)
        result = [values for values in self.data['economy'] if values['user_id'] == member_id and values['server_id'] == server_id]
        if result:
            result = result[0]
        if result:

            money1 = result["money"]

            if bits > money1:
                await ctx.send("The user doesn't have that much money")
            else:

                result["money"] = money1 - bits
                self.save_json()
                await ctx.send(f"Removing {bits} from {member.mention}")

    @commands.command(name="pay", help="Pay a user some bits")
    async def pay(self, ctx, member: discord.Member = None, bits: int = None):
        if member == None:
            await ctx.send(f"Missing argument user: Usage: " + str(ctx.prefix) + str(ctx.command) + " @<user> <bits>")
        elif bits == None:
            await ctx.send(f"Missing argument bits: Usage: " + str(ctx.prefix) + str(ctx.command) + " @<user> <bits>")
        else:
            self.load_data()
            if bits < 0:
                await ctx.send("DONT EVEN DARE TO TRY THIS")
            else:
                server_id = ctx.guild.id
                user_id = ctx.author.id
                member_id = member.id
                if member_id == user_id:
                    await ctx.send("Don't dupe mone")
                else:
                    result = [values for values in self.data['economy'] if values['user_id'] == user_id and values['server_id'] == server_id]
                    result2 = [values for values in self.data['economy'] if values['user_id'] == member_id and values['server_id'] == server_id]
                    if result:
                        result = result[0]
                        money1 = result["money"]
                        if result2:
                            result2 = result2[0]
                            money2 = result2["money"]
                        else:
                            money2 = 0
                            level2 = 1
                        if money1 < bits:
                            await ctx.send("You dont have enough money to pay that amount!")
                        else:

                            result["money"] = money1 - bits
                            await ctx.send(f"Removing bits from <@{user_id}>...")

                            if result2:
                                result2["money"] = money2 + bits
                                await ctx.send(f"Paying {bits} to {member.mention}")
                                await ctx.send(f"Payment was successful")
                            else:
                                self.data["economy"].append({
                                    "user_id": member_id,
                                    "money": money2 + bits,
                                    "level": level2,
                                    "server_id": server_id
                                })
                                await ctx.send(f"Paying {bits} to {member.mention}")
                                await ctx.send(f"Payment was successful")
                            self.save_json()

    @commands.command(name="buy", help="Buy an item")
    async def buy(self, ctx, name: str = None):
        if name == None:
            await ctx.send(f"Missing argument name: Usage: " + str(ctx.prefix) + str(ctx.command) + " <item_name>\ntype " + str(ctx.prefix) + "shop to see available items")
            return
        self.load_data()
        server_id = ctx.guild.id

        # Check if the item is available in the shop
        result = [values for values in self.data['items'] if values['name'] == name]
        if result:
            result = result[0]

        if result:
            item_price = result["price"]
            user_id = ctx.author.id

            # Check if the user has enough money to buy the item
            result = [values for values in self.data['economy'] if values['user_id'] == user_id and values['server_id'] == server_id]
            result2 = [values for values in self.data['user_items'] if values['user_id'] == user_id and values['server_id'] == server_id and values['item_name'] == name]
            if result:
                result = result[0]

            if result:
                user_money = result["money"]
                if result2:
                    await ctx.send("You already have this item")
                else:
                    if user_money >= item_price:
                        # Update the user's money after the purchase
                        result["money"] = user_money - item_price

                        # Add the purchased item to the user's inventory
                        self.data["user_items"].append({
                            "user_id": user_id,
                            "item_name": name,
                            "server_id": server_id
                        })
                        self.save_json()

                        await ctx.send(f"You bought the item '{name}' for {item_price} Bits.")
                    else:
                        await ctx.send("You can't afford this item")
            else:
                await ctx.send("You don't have an entry in the database, start earning bits to get one")
        else:
            await ctx.send(f"The item '{name}' is not available")

    @commands.command(name="use", help="Buy an item")
    async def use_item(self, ctx, item_name = None, member: discord.Member = None):
        if item_name == None:
            await ctx.send(f"Missing argument item_name: Usage: " + str(ctx.prefix) + str(ctx.command) + " <item_name> @<user>")
        elif member == None:
            await ctx.send(f"Missing argument user: Usage: " + str(ctx.prefix) + str(ctx.command) + " <item_name> @<user>")
        else:
            self.load_data()
            server_id = ctx.guild.id
            # Checking if the user owns the item
            result = [values for values in self.data['user_items'] if values['user_id'] == ctx.author.id and values['server_id'] == server_id and values['item_name'] == item_name]

            if result:
                result = result[0]
                if item_name == "Pony":
                    pony_role = discord.utils.get(ctx.guild.roles, name="Best Pony")
                    if not pony_role:
                        pony_role = await ctx.guild.create_role(name="Best Pony", reason = "Pony role creation")
                        await ctx.send("Failed try again (Role created)")
                    else:
                        await ctx.send(f"Your Pony booped {member.mention}")
                        self.data['user_items'].remove(result)
                        self.save_json()
                        boop_duration = 3000
                        await member.add_roles(pony_role, reason="Booped!")
                        await asyncio.sleep(boop_duration)
                        await member.remove_roles(pony_role, reason="Boop Cooldown Ended!")
                if item_name == "Bomb":
                    # Add the "Timeout" role to the user for 5 minutes
                    timeout_role = discord.utils.get(
                        ctx.guild.roles, name="Timeout")
                    if not timeout_role:
                        timeout_role = await ctx.guild.create_role(name="Timeout", reason="Timeout role for the bot")
                        await ctx.send("There wasn't any timeout role available. Role has been created now! Rerun the command to use the item")
                    else:
                        await ctx.send(f"You succesfully dropped the '{item_name}'")
                        # Delete the item from the database as it can only be used once
                        self.data['user_items'].remove(result)
                        self.save_json()
                        timeout_seconds = 300
                        await member.add_roles(timeout_role, reason="Bomb used (5 min Timeout)")
                        await ctx.send(f"{member.mention} cya in 5 mins lol")

                        await asyncio.sleep(timeout_seconds)

                        await member.remove_roles(timeout_role, reason="Timeout expired")
                else:
                    await ctx.send("You can't use that item")

            else:
                await ctx.send(f"You don't own '{item_name}'")

    @commands.command(name="inventory", help="Your inventory")
    async def inventory(self, ctx, member: discord.Member = None):
        self.load_data()
        if member == None:
            user_id = ctx.author.id
        else:
            user_id = member.id
            print(member)

        server_id = ctx.guild.id
        result = [values for values in self.data['user_items'] if values['user_id'] == user_id and values['server_id'] == server_id]

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

            current_time = datetime.now().timestamp()
            self.load_data()
            expired_timers = [values for values in self.data['economytimer'] if values['expiration'] <= current_time]

            for economytimer in expired_timers:
                server_id = economytimer["server_id"]
                server_ids.add(server_id)
                timer_id = economytimer["id"]
                for value in self.data['economytimer']:
                    if value['id'] == int(timer_id):
                        self.data['economytimer'].remove(value)
                self.save_json()
                print(f"The id '{timer_id}' finished working")
            await asyncio.sleep(5)