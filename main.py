import discord
import os
from dotenv import load_dotenv, dotenv_values
from discord import app_commands, Interaction, Embed
from discord.ext import commands
import pnwkit
import requests
import asyncio
from datetime import datetime, timezone
from dateutil import parser
from keep_alive import keep_alive
import db
from typing import Union
from db import DatabaseUser
import logging
load_dotenv()

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.members = True
intents.presences = True
intents.guilds = True
intents.reactions = True
bot = commands.Bot(command_prefix='|', intents=intents)
bot.help_command = None
TOKEN = os.getenv("TOKEN")
key = os.getenv('KEY')
kit = pnwkit.QueryKit(key)
db = DatabaseUser()

@bot.event
async def on_ready():
    
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="Orbis Conflicts"))
    print(f"{bot.user.name} is up and ready!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
      
    
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.tree.command(name="ping")
async def ping(interaction: Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")
    
@bot.command(name="verify", description="verify your nation")
async def verify(ctx: commands.Context, nationid: str):
    try:
        # Check if the user is already registered
        is_registered = await db.is_user_registered(ctx.author.id)
        if is_registered:
            embed = discord.Embed(
                title="Registration Error",
                description="You are already registered.",
                color=0xff0000  # Red color
            )
            await ctx.send(embed=embed)
            return

        # Query Politics and War API to fetch user information
        result = kit.query("nations", {"id": int(nationid)}, "discord nation_name").get()

        # Check if nation information is found
        if not result or not result.nations:
            embed = discord.Embed(
                title="Registration Error",
                description=f"Nation ID {nationid} not found.",
                color=0xff0000  # Red color
            )
            await ctx.send(embed=embed)
            return

        # Extract nation information
        nation = result.nations[0]
        nation_name = nation.nation_name
        # Check if Discord username matches the Discord name from the game
        if ctx.author.name != nation.discord:
            embed = discord.Embed(
                title="Registration Error",
                description=
                f"1. Go to https://politicsandwar.com/nation/edit/\n2. Scroll down to where it says Discord Username\n3. Type `{ctx.author.name}` in the adjacent field\n 4. Come back to discord type `!verify {nationid}` again",
                color=0xff0000  # Red color
            )
            await ctx.send(embed=embed)
            return

        # Store nationid in user database
        await db.add_user_nation(ctx.author.id, nationid)
        await db.add_id_user(nationid, ctx.author.id)

        embed = discord.Embed(
            title="Registration Successful",
            description=f"{nation_name} is successfully registered.",
            color=0x00ff00  # Green color
        )
        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {e}",
            color=0xff0000  # Red color
        )
        await ctx.send(embed=embed)

@bot.tree.command(name="verify", description="Register with the bot")
@app_commands.describe(nationid="Your nation ID")
async def verify(interaction: discord.Interaction, nationid: str):
    try:
        # Check if the user is already registered
        is_registered = await db.is_user_registered(interaction.user.id)
        if is_registered:
            embed = discord.Embed(
                title="Registration Error",
                description="You are already registered.",
                color=0xff0000  # Red color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Query Politics and War API to fetch user information
        result = kit.query("nations", {"id": int(nationid)}, "discord nation_name").get()

        # Check if nation information is found
        if not result or not result.nations:
            embed = discord.Embed(
                title="Registration Error",
                description=f"Nation ID {nationid} not found.",
                color=0xff0000  # Red color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Extract nation information
        nation = result.nations[0]
        nation_name = nation.nation_name

        # Check if Discord username matches the Discord name from the game
        if interaction.user.name != nation.discord:
            embed = discord.Embed(
                title="Registration Error",
                description=(
                    "1. Go to https://politicsandwar.com/nation/edit/\n"
                    "2. Scroll down to where it says Discord Username\n"
                    "3. Type `{interaction.user.name}` in the adjacent field\n"
                    "4. Come back to discord type `/verify {nationid}` again"
                ),
                color=0xff0000  # Red color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Store nationid in user database
        await db.add_user_nation(interaction.user.id, nationid)
        await db.add_id_user(nationid, interaction.user.id)

        embed = discord.Embed(
            title="Registration Successful",
            description=f"{nation_name} is successfully registered.",
            color=discord.Color.green()  # Green color
        )
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {e}",
            color=discord.Color.red()  # Red color
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
                       
@bot.command(name="unverify", description="Unregister with the bot")
async def unverify(ctx: commands.Context):
    try:
        # Check if the user is registered
        is_registered = await db.is_user_registered(ctx.author.id)
        if not is_registered:
            embed = discord.Embed(
                title="Unregistration Error",
                description="You are not registered.",
                color=0xff0000  # Red color
            )
            await ctx.send(embed=embed)
            return

        # Remove user from database
        await db.remove_user(ctx.author.id)

        embed = discord.Embed(
            title="Unregistration Successful",
            description="You have been successfully unregistered.",
            color=0x00ff00  # Green color
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        
@bot.tree.command(name="unverify", description="Unregister with the bot")
async def unverify(interaction: discord.Interaction):
    try:
        # Check if the user is registered
        is_registered = await db.is_user_registered(interaction.user.id)
        if not is_registered:
            embed = discord.Embed(
                title="Unregistration Error",
                description="You are not registered.",
                color=0xff0000  # Red color
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Remove user from database
        await db.remove_user(interaction.user.id)

        embed = discord.Embed(
            title="Unregistration Successful",
            description="You have been successfully unregistered.",
            color=discord.Color.green()  # Green color
        )
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {e}",
            color=discord.Color.red()  # Red color
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)        
    
@bot.command(name="me",
             description="Display your own registration information")
async def me(ctx: commands.Context):
    try:
        user_id = ctx.author.id
        # Check if the user is registered
        is_registered = await db.is_user_registered(user_id)
        if not is_registered:
            embed = discord.Embed(
                title="Registration Info",
                description="You are not registered.",
                color=0xff0000  # Red color
            )
        else:
            # Retrieve nation ID for the user from the database
            nation_id = await db.get_user_nation_id(user_id)
            if not nation_id:
                embed = discord.Embed(
                    title="Registration Info",
                    description="No nation details found.",
                    color=0xff0000  # Red color
                )
            else:
                # Query nation details using the nation ID
                query = kit.query(
                    "nations", {"id": int(nation_id)},
                    """nation_name, leader_name, color, num_cities, vacation_mode_turns, soldiers, tanks, aircraft, ships, alliance { name, id }, alliance_position_info { name }, date"""
                )
                result = query.get()

                if result and result.nations:
                    nation = result.nations[0]
                    # Extract creation date from the result
                    creation_date_str = nation.date

                    # Parse the creation date string into a datetime object
                    creation_date = parser.isoparse(
                        str(creation_date_str)).replace(tzinfo=timezone.utc)

                    # Get the current datetime in UTC timezone
                    current_date = datetime.now(timezone.utc)

                    # Calculate the difference between the current date and creation date
                    difference = current_date - creation_date

                    # Format the difference as "X days ago"
                    days_ago = difference.days
                    creation_message = f"{days_ago} days ago"

                    # Construct and send the embed with nation details including creation date
                    embed = discord.Embed(
                        title="Registration Info",
                        description=f"Registered with nation ID: [{nation_id}](<https://politicsandwar.com/nation/id={nation_id}>)",
                        color=discord.Color.blue()  # Orange color
                    )
                    embed.add_field(name="🇺🇳Nation Name",
                                    value=nation.nation_name,
                                    inline=True)
                    embed.add_field(name="👑Leader Name",
                                    value=nation.leader_name,
                                    inline=True)
                    embed.add_field(name="⏳Created",
                                    value=f"`{creation_message}`",
                                    inline=False)
                    embed.add_field(name="🎨Color",
                                    value=nation.color.capitalize(),
                                    inline=True)
                    embed.add_field(name="🏙️Cities",
                                    value=nation.num_cities,
                                    inline=True)
                    embed.add_field(
                        name="📴Vacation Mode",
                        value=f"{nation.vacation_mode_turns} Turns",
                        inline=True)
                    if nation.alliance:
                        embed.add_field(name="🔢Alliance Id",
                                        value=nation.alliance.id,
                                        inline=True)
                    if nation.alliance:
                        embed.add_field(name="🕍Alliance",
                                        value=nation.alliance.name,
                                        inline=True)
                    if nation.alliance_position_info:
                        embed.add_field(
                            name="💼Alliance Position",
                            value=nation.alliance_position_info.name,
                            inline=True)
                    embed.add_field(name="💂Soldiers",
                                    value=nation.soldiers,
                                    inline=True)
                    embed.add_field(name="🚜Tanks",
                                    value=nation.tanks,
                                    inline=True)
                    embed.add_field(name="🛩️Aircraft",
                                    value=nation.aircraft,
                                    inline=True)
                    embed.add_field(name="🚢Ships",
                                    value=nation.ships,
                                    inline=True)

                else:
                    embed = discord.Embed(
                        title="Registration Info",
                        description="No nation details found.",
                        color=0xff0000  # Red color
                    )
    except Exception as e:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {e}",
            color=0xff0000  # Red color
        )

    await ctx.send(embed=embed)    
    
@bot.tree.command(name="me", description="Display your own registration information")
async def me(interaction: discord.Interaction):
    try:
        user_id = interaction.user.id
        # Check if the user is registered
        is_registered = await db.is_user_registered(user_id)
        if not is_registered:
            embed = discord.Embed(
                title="Registration Info",
                description="You are not registered.",
                color=0xff0000  # Red color
            )
        else:
            # Retrieve nation ID for the user from the database
            nation_id = await db.get_user_nation_id(user_id)
            if not nation_id:
                embed = discord.Embed(
                    title="Registration Info",
                    description="No nation details found.",
                    color=0xff0000  # Red color
                )
            else:
                # Query nation details using the nation ID
                query = kit.query(
                    "nations", {"id": int(nation_id)},
                    """nation_name, leader_name, color, num_cities, vacation_mode_turns, soldiers, tanks, aircraft, ships, alliance { name, id }, alliance_position_info { name }, date"""
                )
                result = query.get()

                if result and result.nations:
                    nation = result.nations[0]
                    # Extract creation date from the result
                    creation_date_str = nation.date

                    # Parse the creation date string into a datetime object
                    creation_date = parser.isoparse(
                        str(creation_date_str)).replace(tzinfo=timezone.utc)

                    # Get the current datetime in UTC timezone
                    current_date = datetime.now(timezone.utc)

                    # Calculate the difference between the current date and creation date
                    difference = current_date - creation_date

                    # Format the difference as "X days ago"
                    days_ago = difference.days
                    creation_message = f"{days_ago} days ago"

                    # Construct and send the embed with nation details including creation date
                    embed = discord.Embed(
                        title="Registration Info",
                        description=f"Registered with nation ID: [{nation_id}](<https://politicsandwar.com/nation/id={nation_id}>)",
                        color=discord.Color.blue()  # Blue color
                    )
                    embed.add_field(name="🇺🇳Nation Name",
                                    value=nation.nation_name,
                                    inline=True)
                    embed.add_field(name="👑Leader Name",
                                    value=nation.leader_name,
                                    inline=True)
                    embed.add_field(name="⏳Created",
                                    value=f"`{creation_message}`",
                                    inline=False)
                    embed.add_field(name="🎨Color",
                                    value=nation.color.capitalize(),
                                    inline=True)
                    embed.add_field(name="🏙️Cities",
                                    value=nation.num_cities,
                                    inline=True)
                    embed.add_field(
                        name="📴Vacation Mode",
                        value=f"{nation.vacation_mode_turns} Turns",
                        inline=True)
                    if nation.alliance:
                        embed.add_field(name="🔢Alliance Id",
                                        value=nation.alliance.id,
                                        inline=True)
                    if nation.alliance:
                        embed.add_field(name="🕍Alliance",
                                        value=nation.alliance.name,
                                        inline=True)
                    if nation.alliance_position_info:
                        embed.add_field(
                            name="💼Alliance Position",
                            value=nation.alliance_position_info.name,
                            inline=True)
                    embed.add_field(name="💂Soldiers",
                                    value=f"{nation.soldiers:,}",
                                    inline=True)
                    embed.add_field(name="🚜Tanks",
                                    value=nation.tanks,
                                    inline=True)
                    embed.add_field(name="🛩️Aircraft",
                                    value=nation.aircraft,
                                    inline=True)
                    embed.add_field(name="🚢Ships",
                                    value=nation.ships,
                                    inline=True)

                else:
                    embed = discord.Embed(
                        title="Registration Info",
                        description="No nation details found.",
                        color=0xff0000  # Red color
                    )
    except Exception as e:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {e}",
            color=0xff0000  # Red color
        )

    await interaction.response.send_message(embed=embed)        
     
@bot.command(name="avg_prices", description="check the trade ppu values")
async def avg_prices(ctx):
    try:
        query = kit.query("tradeprices", {"first": 1}, "food coal oil uranium iron lead bauxite gasoline munitions aluminum steel")
        result = query.get()
        if result and result.tradeprices:
            trade = result.tradeprices[0]
            food = trade.food
            coal = trade.coal
            oil = trade.oil
            uranium = trade.uranium
            iron = trade.iron
            lead = trade.lead
            bauxite = trade.bauxite
            gasoline = trade.gasoline
            munitions = trade.munitions
            steel = trade.steel
            aluminum = trade.aluminum
            
            embed = discord.Embed(
                title="Average Prices",
                description="Average Prices Per Unit (PPU) of Resources",
                color=discord.Color.blue()
            )
            embed.add_field(name="Food", value=f"${food:,}")
            embed.add_field(name="Coal", value=f"${coal:,}")
            embed.add_field(name="Oil", value=f"${oil:,}")
            embed.add_field(name="Uranium", value=f"${uranium:,}")
            embed.add_field(name="Iron", value=f"${iron:,}")
            embed.add_field(name="Lead", value=f"${lead:,}")
            embed.add_field(name="Bauxite", value=f"${bauxite:,}")
            embed.add_field(name="Gasoline", value=f"${gasoline:,}")
            embed.add_field(name="Munitions", value=f"${munitions:,}")
            embed.add_field(name="Aluminum", value=f"${aluminum:,}")
            embed.add_field(name="Steel", value=f"${steel:,}")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("No trade price data available.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
    
@bot.tree.command(name="avg_prices", description="check the trade ppu values")
async def avg_prices(interaction: discord.Interaction):
    try:
        query = kit.query("tradeprices", {"first": 1}, "food coal oil uranium iron lead bauxite gasoline munitions aluminum steel")
        result = query.get()
        if result and result.tradeprices:
            trade = result.tradeprices[0]
            food = f"${trade.food:,}"
            coal = f"${trade.coal:,}"
            oil = f"${trade.oil:,}"
            uranium = f"${trade.uranium:,}"
            iron = f"${trade.iron:,}"
            lead = f"${trade.lead:,}"
            bauxite = f"${trade.bauxite:,}"
            gasoline = f"${trade.gasoline:,}"
            munitions = f"${trade.munitions:,}"
            steel = f"${trade.steel:,}"
            aluminum = f"${trade.aluminum:,}"
            
            embed = discord.Embed(
                title="Average Prices",
                description="Average Prices Per Unit (PPU) of Resources",
                color=discord.Color.blue()
            )
            embed.add_field(name="Food", value=food)
            embed.add_field(name="Coal", value=coal)
            embed.add_field(name="Oil", value=oil)
            embed.add_field(name="Uranium", value=uranium)
            embed.add_field(name="Iron", value=iron)
            embed.add_field(name="Lead", value=lead)
            embed.add_field(name="Bauxite", value=bauxite)
            embed.add_field(name="Gasoline", value=gasoline)
            embed.add_field(name="Munitions", value=munitions)
            embed.add_field(name="Aluminum", value=aluminum)
            embed.add_field(name="Steel", value=steel)
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("No trade price data available.")
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}")
        
@bot.command(name="who",
             description="Display nation information of a user or nation ID")
async def who(ctx: commands.Context, user_or_nation: Union[discord.Member,str]):
    try:
        user_id = user_or_nation.id if isinstance(user_or_nation,
                                                  discord.Member) else None
        nation_id = user_or_nation if isinstance(user_or_nation, str) else None

        if user_id:
            is_registered = await db.is_user_registered(user_id)
            if is_registered:
                nation_id = await db.get_user_nation_id(user_id)
            else:
                await ctx.send(
                    "User is not registered. Please provide a nation ID instead."
                )
                return

        if nation_id:
            query = kit.query(
                "nations", {"id": int(nation_id)},
                """nation_name, leader_name, color, num_cities, vacation_mode_turns, soldiers, tanks, aircraft, ships, alliance { name, id }, alliance_position_info { name }, date, score"""
            )
            result = query.get()

            if result and result.nations:
                nation = result.nations[0]
                # Extract creation date from the result
                creation_date_str = nation.date

                # Parse the creation date string into a datetime object
                creation_date = parser.isoparse(
                    str(creation_date_str)).replace(tzinfo=timezone.utc)

                # Get the current datetime in UTC timezone
                current_date = datetime.now(timezone.utc)

                # Calculate the difference between the current date and creation date
                difference = current_date - creation_date

                # Format the difference as "X days ago"
                days_ago = difference.days
                creation_message = f"{days_ago} days ago"

                # Construct and send the embed with nation details
                embed = discord.Embed(
                    title="Registration Info",
                    description=f"Details of Nation ID: [{nation_id}](<https://politicsandwar.com/nation/id={nation_id}>)",
                    color=discord.Color.blue()  # Orange color
                )
                embed.add_field(name="🇺🇳Nation Name",
                                value=nation.nation_name,
                                inline=True)
                embed.add_field(name="👑Leader Name",
                                value=nation.leader_name,
                                inline=True)
                embed.add_field(name="⏳Created",
                                value=f"`{creation_message}`",
                                inline=True)
                embed.add_field(name="💯Score",
                                value=f"{nation.score:,}",
                                inline=True)
                embed.add_field(name="🎨Color",
                                value=nation.color.capitalize(),
                                inline=True)
                embed.add_field(name="🏙️Cities",
                                value=nation.num_cities,
                                inline=True)
                embed.add_field(name="📴Vacation Mode",
                                value=f"{nation.vacation_mode_turns} Turns",
                                inline=True)
                if nation.alliance:
                        embed.add_field(name="🔢Alliance Id",
                                        value=nation.alliance.id,
                                        inline=True)
                    
                if nation.alliance:
                    embed.add_field(name="🕍Alliance",
                                    value=nation.alliance.name,
                                    inline=True)
                if nation.alliance_position_info:
                    embed.add_field(name="💼Alliance Position",
                                    value=nation.alliance_position_info.name,
                                    inline=True)
                embed.add_field(name="💂Soldiers",
                                value=nation.soldiers,
                                inline=True)
                embed.add_field(name="🚜Tanks", value=nation.tanks, inline=True)
                embed.add_field(name="🛩️Aircraft",
                                value=nation.aircraft,
                                inline=True)
                embed.add_field(name="🚢Ships", value=nation.ships, inline=True)

                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Nation with ID {nation_id} not found.")
        else:
            await ctx.send("Please provide a valid user mention or nation ID.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        
@bot.tree.command(name="who", description="Display nation information of a user or nation ID")
@app_commands.describe(nationid="Nation ID or mention the user")
async def who(interaction: Interaction, nationid: str):
    try:
        # Check if the input is a mention
        if nationid.startswith("<@") and nationid.endswith(">"):
            # Extract the user ID from the mention
            user_id = int(nationid.strip("<@!>"))
            # Retrieve nation ID for the user from the database
            nation_id = await db.get_user_nation_id(user_id)
            if not nation_id:
                embed = discord.Embed(
                    title="Nation Info",
                    description=f"No nation details found for user with ID {user_id}.",
                    color=discord.Color.red()  # Red color
                )
                await interaction.response.send_message(embed=embed)
                return
        else:
            nation_id = nationid

        # Query nation details using the nation ID
        query = kit.query(
            "nations", {"id": int(nation_id)},
            """nation_name, leader_name, color, num_cities, score, vacation_mode_turns, soldiers, tanks, aircraft, ships, alliance { name, id }, alliance_position_info { name }, date"""
        )
        result = query.get()
        if result and result.nations:
            nation = result.nations[0]
            # Extract creation date from the result
            creation_date_str = nation.date
            # Parse the creation date string into a datetime object
            creation_date = parser.isoparse(str(creation_date_str)).replace(tzinfo=timezone.utc)
            # Get the current datetime in UTC timezone
            current_date = datetime.now(timezone.utc)
            # Calculate the difference between the current date and creation date
            difference = current_date - creation_date
            # Format the difference as "X days ago"
            days_ago = difference.days
            creation_message = f"{days_ago} days ago"

            # Construct and send the embed with nation details including creation date
            embed = discord.Embed(
                title="Nation Info",
                description=f"Details for nation ID: [{nation_id}](<https://politicsandwar.com/nation/id={nation_id}>)",
                color=discord.Color.blue()  # Blue color
            )
            embed.add_field(name="🇺🇳 Nation Name", value=nation.nation_name, inline=True)
            embed.add_field(name="👑 Leader Name", value=nation.leader_name, inline=True)
            embed.add_field(name="⏳ Created", value=f"`{creation_message}`", inline=False)
            embed.add_field(name="🎨 Color", value=nation.color.capitalize(), inline=True)
            embed.add_field(name="💯 Score", value=f"{nation.score:,}", inline=True)
            embed.add_field(name="🏙️ Cities", value=f"{nation.num_cities:,}", inline=True)
            embed.add_field(name="📴 Vacation Mode", value=f"{nation.vacation_mode_turns:,} Turns", inline=True)
            if nation.alliance:
                embed.add_field(name="🔢 Alliance Id", value=f"{nation.alliance.id}", inline=True)
                embed.add_field(name="🕍 Alliance", value=nation.alliance.name, inline=True)
            if nation.alliance_position_info:
                embed.add_field(name="💼 Alliance Position", value=nation.alliance_position_info.name, inline=True)
            embed.add_field(name="💂 Soldiers", value=f"{nation.soldiers:,}", inline=True)
            embed.add_field(name="🚜 Tanks", value=f"{nation.tanks:,}", inline=True)
            embed.add_field(name="🛩️ Aircraft", value=f"{nation.aircraft:,}", inline=True)
            embed.add_field(name="🚢 Ships", value=f"{nation.ships:,}", inline=True)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Nation Info",
                description="No nation details found.",
                color=discord.Color.red()  # Red color
            )
            await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred: {e}",
            color=discord.Color.red()  # Red color
        )
        await interaction.response.send_message(embed=embed)

@bot.command(name="help", description="Shows this message")
async def help_command(ctx):
    # Get the total number of commands
    bot_commands_count = len(bot.commands)
    tree_commands_count = len(bot.tree.get_commands())
    total_commands = bot_commands_count + tree_commands_count

    # Retrieve the bot's commands and sort them alphabetically
    commands_list = sorted(bot.commands, key=lambda x: x.name)

    # Prepare the embed
    embed = discord.Embed(title="Help", description=f"Total commands: {total_commands}\nList of available commands", color=discord.Color.blue())

    for command in commands_list:
        embed.add_field(name=f"|{command.name}", value=command.description or "No description provided", inline=False)

    await ctx.send(embed=embed)
    
@bot.command(name="verify_aa", description="verify your alliance for guild")
async def verify_aa(ctx, alliance_id: str):
    db = DatabaseUser()
    
    # Check the command is used in server
    if ctx.guild is None:
        await ctx.send("This command can only be used in a server.")
        return
    
    # Check the user is an admin of the guild
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You are not an administrator of this server.")
        return

    # Check if the alliance ID is valid
    if not alliance_id.isdigit():
        await ctx.send("Invalid alliance ID. Please provide a valid alliance ID.")
        return

    # Check if the guild alliance id is already registered
    existing_alliance_id = await db.get_guild_alliance(ctx.guild.id)
    if existing_alliance_id:
        if existing_alliance_id == alliance_id:
            await ctx.send("Alliance is already registered in this server.")
        else:
            await ctx.send("Another alliance is already registered in this server.")
        return
    
    # Check the user is registered
    user_id = ctx.author.id
    is_registered = await db.is_user_registered(user_id)
    if not is_registered:
        await ctx.send("You are not registered. Please use |verify command to register your nation ID.")
        return
    
    # Get the user nation id
    nation_id = await db.get_user_nation_id(user_id)
    if nation_id is None:
        await ctx.send("You are not registered. Please use |verify command to register your nation ID.")
        return
    
    # Query for checking alliance id and alliance position
    query = kit.query("nations", {"id": int(nation_id)}, "alliance_id, alliance_position_info{leader}, alliance {name}")
    result = query.get()
    if result and result.nations:
        nation = result.nations[0]
        aa_id = nation["alliance_id"]
        alliance_position_info = nation.alliance_position_info.leader
        alliance_name = nation.alliance.name
        
        if aa_id is None:
            await ctx.send("You are not in any alliance.")
            return

        # Check the user is leader and the alliance id matches the provided alliance id
        if alliance_position_info != True :  # Compare against the correct enum string
            await ctx.send("You are not the leader of your alliance.")
            return
        
        if alliance_id != str(aa_id):  # Ensure both IDs are strings for comparison
            await ctx.send("The alliance ID provided does not match your alliance ID.")
            return
        
        # Add the guild alliance id in the database
        await db.add_guild_alliance(ctx.guild.id, alliance_id)
        await ctx.send(f"{alliance_name} has registered successfully to this server")
    else:
        await ctx.send("Unable to retrieve your nation information. Please try again later.")    
@bot.tree.command(name="verify_aa", description="Verify your alliance for the guild")
@app_commands.describe(alliance_id="The alliance ID to verify")
async def verify_aa(interaction: discord.Interaction, alliance_id: str):
    if interaction.guild is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You are not an administrator of this server.", ephemeral=True)
        return

    if not alliance_id.isdigit():
        await interaction.response.send_message("Invalid alliance ID. Please provide a valid alliance ID.", ephemeral=True)
        return

    existing_alliance_id = await db.get_guild_alliance(interaction.guild.id)
    if existing_alliance_id:
        if existing_alliance_id == alliance_id:
            await interaction.response.send_message("Alliance is already registered in this server.", ephemeral=True)
        else:
            await interaction.response.send_message("Another alliance is already registered in this server.", ephemeral=True)
        return

    user_id = interaction.user.id
    is_registered = await db.is_user_registered(user_id)
    if not is_registered:
        await interaction.response.send_message("You are not registered. Please use /verify command to register your nation ID.", ephemeral=True)
        return

    nation_id = await db.get_user_nation_id(user_id)
    if nation_id is None:
        await interaction.response.send_message("You are not registered. Please use /verify command to register your nation ID.", ephemeral=True)
        return

    query = kit.query("nations", {"id": int(nation_id)}, "alliance_id, alliance_position_info{leader}, alliance {name}")
    result = query.get()
    if result and result.nations:
        nation = result.nations[0]
        aa_id = nation["alliance_id"]
        alliance_position_info = nation.alliance_position_info.leader
        alliance_name = nation.alliance.name

        if aa_id is None:
            await interaction.response.send_message("You are not in any alliance.", ephemeral=True)
            return

        if alliance_position_info != True:
            await interaction.response.send_message("You are not the leader of your alliance.", ephemeral=True)
            return

        if alliance_id != str(aa_id):
            await interaction.response.send_message("The alliance ID provided does not match your alliance ID.", ephemeral=True)
            return

        await db.add_guild_alliance(interaction.guild.id, alliance_id)
        await interaction.response.send_message(f"{alliance_name} has registered successfully to this server")
    else:
        await interaction.response.send_message("Unable to retrieve your nation information. Please try again later.", ephemeral=True)

@bot.command(name="api", description="Set the API key for the server")
async def api(ctx, api_key: str):
    try:
        # Check if the user is the administrator 
        if ctx.author.guild_permissions.administrator:
            # Store the API key in the database
            await db.add_guild_api_key(ctx.guild.id, api_key)

            embed = discord.Embed(
                title="API Key Set",
                description=f"API key set successfully for server {ctx.guild.name}.",
                color=0x00ff00  # Green color
            )
            await ctx.send(embed=embed)
        guild_id = ctx.guild.id
        await db.add_guild_api_key(guild_id, api_key)
        await ctx.send("API key registered successfully!", ephemeral=True)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", ephemeral=True)
              
@bot.tree.command(name="api", description="Set API key")
@app_commands.describe(api_key="API key")
async def api(interaction: discord.Interaction, api_key: str):
    try:
        # Check if the user is an administrator
        if interaction.user.guild_permissions.administrator:
            # Add to database
            guild_id = interaction.guild.id
            await db.add_guild_api_key(guild_id, api_key)
            await interaction.response.send_message("API key added successfully!", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
        
@bot.tree.command(name="roles", description="Set roles with Titan")
@app_commands.describe(members="Role for your alliance members", leader="Role for your alliance leader", ia="Role for your internal affairs", ea="Role for your economic affairs", fa="Role for your foreign affairs", ma="Role for your military affairs")
async def roles(interaction: discord.Interaction, members: discord.Role, leader: discord.Role, ia: discord.Role, ea: discord.Role, fa: discord.Role, ma: discord.Role):
    try:
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        
        guild_id = interaction.guild.id
        
        await db.add_guild_members(guild_id, str(members.id))
        await db.add_guild_leader(guild_id, str(leader.id))
        await db.add_guild_internal(guild_id, str(ia.id))
        await db.add_guild_finance(guild_id, str(ea.id))
        await db.add_guild_external(guild_id, str(fa.id))
        await db.add_guild_military(guild_id, str(ma.id))
        
        await interaction.response.send_message("Roles added successfully!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
        
@bot.command(name="stockpile", description="Get the resources of the nation")
async def stockpile(ctx: commands.Context, user_or_nation: Union[discord.Member, str]):
    try:
        # Determine if user_or_nation is a Discord member or nation ID
        user_id = user_or_nation.id if isinstance(user_or_nation, discord.Member) else None
        nation_id = user_or_nation if isinstance(user_or_nation, str) else None

        if user_id:
            is_registered = await db.is_user_registered(user_id)
            if is_registered:
                nation_id = await db.get_user_nation_id(user_id)
            else:
                await ctx.send("User is not registered. Please provide a nation ID instead.")
                return
        
        # Check if the user has the required roles
        guild_id = ctx.guild.id
        user_roles = [role.id for role in ctx.author.roles]
        ia = await db.get_guild_internal(guild_id)
        ea = await db.get_guild_finance(guild_id)

        if not ia or not ea or (int(ia) not in user_roles and int(ea) not in user_roles):
            return await ctx.send("You do not have the required roles to use this command.")
        
        # Retrieve API key from the database
        api_key = await db.get_api_key(ctx.guild.id)
        if not api_key:
            await ctx.send("API key is not registered.")
            return

        if nation_id:
            # Initialize the kit with the API key
            pnw_kit = pnwkit.QueryKit(api_key)
            
            # Define the query
            query = pnw_kit.query(
                "nations", 
                {"id": int(nation_id)}, 
                "nation_name money food coal oil uranium iron bauxite lead gasoline steel munitions aluminum"
            )
            
            # Execute the query
            result = query.get()

            if result and result.nations:
                nation = result.nations[0]
                embed = discord.Embed(
                    title=f"Resources of {nation['nation_name']}",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Money", value=f"{nation['money']:,}", inline=True)
                embed.add_field(name="Food", value=f"{nation['food']:,}", inline=True)
                embed.add_field(name="Coal", value=f"{nation['coal']:,}", inline=True)
                embed.add_field(name="Oil", value=f"{nation['oil']:,}", inline=True)
                embed.add_field(name="Uranium", value=f"{nation['uranium']:,}", inline=True)
                embed.add_field(name="Iron", value=f"{nation['iron']:,}", inline=True)
                embed.add_field(name="Bauxite", value=f"{nation['bauxite']:,}", inline=True)
                embed.add_field(name="Lead", value=f"{nation['lead']:,}", inline=True)
                embed.add_field(name="Gasoline", value=f"{nation['gasoline']:,}", inline=True)
                embed.add_field(name="Steel", value=f"{nation['steel']:,}", inline=True)
                embed.add_field(name="Munitions", value=f"{nation['munitions']:,}", inline=True)
                embed.add_field(name="Aluminum", value=f"{nation['aluminum']:,}", inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send("No data found for the specified nation ID.")
        else:
            await ctx.send("No valid nation ID provided.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.tree.command(name="stockpile", description="Get the resources of the nation")
@app_commands.describe(user_or_nation="Mention a user or provide a nation ID")
async def stockpile(interaction: discord.Interaction, user_or_nation: str):
    try:
        user_id = None
        nation_id = None

        # Check if the input is a mention
        if user_or_nation.startswith("<@") and user_or_nation.endswith(">"):
            # Extract the user ID from the mention
            user_id = int(user_or_nation.strip("<@!>"))
        else:
            nation_id = user_or_nation

        if user_id:
            is_registered = await db.is_user_registered(user_id)
            if is_registered:
                nation_id = await db.get_user_nation_id(user_id)
            else:
                await interaction.response.send_message("User is not registered. Please provide a nation ID instead.", ephemeral=True)
                return
        
        # Check if the user has the required roles
        guild_id = interaction.guild.id
        user_roles = [role.id for role in interaction.user.roles]
        ia = await db.get_guild_internal(guild_id)
        ea = await db.get_guild_finance(guild_id)

        if not ia or not ea or (int(ia) not in user_roles and int(ea) not in user_roles):
            return await interaction.response.send_message("You do not have the required roles to use this command.", ephemeral=True)
        
        # Retrieve API key from the database
        api_key = await db.get_api_key(interaction.guild.id)
        if not api_key:
            await interaction.response.send_message("API key is not registered.", ephemeral=True)
            return

        if nation_id:
            # Initialize the kit with the API key
            pnw_kit = pnwkit.QueryKit(api_key)
            
            # Define the query
            query = pnw_kit.query(
                "nations", 
                {"id": int(nation_id)}, 
                "nation_name money food coal oil uranium iron bauxite lead gasoline steel munitions aluminum"
            )
            
            # Execute the query
            result = query.get()

            if result and result.nations:
                nation = result.nations[0]
                embed = discord.Embed(
                    title=f"Resources of {nation['nation_name']}",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Money", value=f"{nation['money']:,}", inline=True)
                embed.add_field(name="Food", value=f"{nation['food']:,}", inline=True)
                embed.add_field(name="Coal", value=f"{nation['coal']:,}", inline=True)
                embed.add_field(name="Oil", value=f"{nation['oil']:,}", inline=True)
                embed.add_field(name="Uranium", value=f"{nation['uranium']:,}", inline=True)
                embed.add_field(name="Iron", value=f"{nation['iron']:,}", inline=True)
                embed.add_field(name="Bauxite", value=f"{nation['bauxite']:,}", inline=True)
                embed.add_field(name="Lead", value=f"{nation['lead']:,}", inline=True)
                embed.add_field(name="Gasoline", value=f"{nation['gasoline']:,}", inline=True)
                embed.add_field(name="Steel", value=f"{nation['steel']:,}", inline=True)
                embed.add_field(name="Munitions", value=f"{nation['munitions']:,}", inline=True)
                embed.add_field(name="Aluminum", value=f"{nation['aluminum']:,}", inline=True)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("No data found for the specified nation ID.", ephemeral=True)
        else:
            await interaction.response.send_message("No valid nation ID provided.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

@bot.command(name="mail", description="Send mail to a nation")
async def mail(ctx, *, args: str):
    """
    Send a message using the Politics and War API.
    Usage: !mail [nation_id;subject;message]
    """
    try:
        # Splitting the arguments
        args_list = args.split(';')

        # Validating the number of arguments
        if len(args_list) != 3:
            await ctx.send("Invalid number of arguments. Please use the format: !mail [nation_id;subject;message]")
            return

        recipient, subject, message = args_list

        # Check if the user has the leader role
        guild_id = ctx.guild.id
        user_roles = [role.id for role in ctx.author.roles]
        leader = await db.get_guild_leader(guild_id)

        if not leader or int(leader) not in user_roles:
            return await ctx.send("You do not have the required leader role to use this command.", ephemeral=True)

        # Get guild API key
        api_key = await db.get_api_key(ctx.guild.id)

        url = "https://politicsandwar.com/api/send-message/"
        data = {
            "key": api_key,
            "to": recipient,
            "subject": subject,
            "message": message,
        }

        # Sending the request
        response = requests.post(url, data=data)
        if response.status_code == 200:
            await ctx.send(f"Message sent successfully to `{recipient}`, subject: `{subject}`")
        else:
            await ctx.send("Failed to send message. Please check your API key and try again.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")    
        
@bot.tree.command(name="mail", description="Send mail to nations")
@app_commands.describe(recipients="Comma-separated nation IDs to send the message to", 
                       subject="The subject of the message", 
                       message="The message content",
                       api_key="Optional API key")
async def mail(interaction: discord.Interaction, recipients: str, subject: str, message: str, api_key: str = None):
    """
    Send a message using the Politics and War API.
    """
    try:
        # Check if the user has the leader role
        guild_id = interaction.guild.id
        user_roles = [role.id for role in interaction.user.roles]
        leader = await db.get_guild_leader(guild_id)  # You'll need to define db and this method
        
        if not leader or int(leader) not in user_roles:
            await interaction.response.send_message("You do not have the required leader role to use this command.", ephemeral=True)
            return

        # Get guild API key if not provided
        if not api_key:
            api_key = await db.get_api_key(interaction.guild.id)  # You'll need to define db and this method
        
        url = "https://politicsandwar.com/api/send-message/"

        # Split the recipients by comma and send the message to each
        recipient_list = recipients.split(',')
        success_count = 0
        failure_count = 0

        for recipient in recipient_list:
            data = {
                "key": api_key,
                "to": recipient.strip(),
                "subject": subject,
                "message": message,
            }
            # Sending the request
            response = requests.post(url, data=data)
            if response.status_code == 200:
                success_count += 1
            else:
                failure_count += 1

        await interaction.response.send_message(f"Message sent successfully to {success_count} nation(s). Failed to send to {failure_count} nation(s).")
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}")

@bot.tree.command(name="setup_applications", description="Setup the applicants applications for interview.")
@app_commands.describe(category="Provide the category for the applications", message="Provide message for the player when they open an application")
async def setup_applications(interaction: discord.Interaction, category: discord.CategoryChannel, message: str):
    try:
        # Check if the user is administrator
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

        # Check if the category exists
        if not category:
            return await interaction.response.send_message("Invalid category.", ephemeral=True)

        # Add category to the database
        guild_id = interaction.guild.id
        await db.add_ticket_category(guild_id, category.id)  # Ensure db.add_ticket_category is defined elsewhere in your code

        # Add the message to the database
        await db.add_ticket_message(guild_id, message)

        await interaction.response.send_message("Setup completed successfully.", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
@bot.command(name="apply", description="Apply to the alliance")
async def apply(ctx, nation_id: str):
    try:
        # Check if the setup for applications is done
        guild_id = ctx.guild.id
        message = await db.get_ticket_message(guild_id)
        category_id = await db.get_ticket_category(guild_id)
        
        if category_id is None:
            return await ctx.send("```Setup for applications is not completed. Use !setup_applications command to complete the setup.```")
        
        # Query for provided nation id
        query = kit.query("nations", {"id": int(nation_id)}, "nation_name", "score", "num_cities", "offensive_wars_count", "defensive_wars_count")
        result = query.get()
        
        if result and result.nations:
            nation = result.nations[0]
            nation_name = nation.nation_name
            score = nation.score
            num_cities = nation.num_cities
            offensive_wars_count = nation.offensive_wars_count
            defensive_wars_count = nation.defensive_wars_count
            wars = offensive_wars_count + defensive_wars_count

            # Check if the user already has an open ticket
            existing_ticket = None
            for channel in ctx.guild.text_channels:
                if channel.name.startswith(f"{nation_id}"):
                    existing_ticket = channel
                    break

            if existing_ticket:
                return await ctx.send(f"You already have an application open in {existing_ticket.mention}.")

            # Create a new ticket channel
            category = bot.get_channel(int(category_id))
            if not category:
                return await ctx.send("Category not found.")
            
            # Define overwrites for the ticket channel
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
            for role in category.overwrites:
                if isinstance(role, discord.Role):
                    overwrites[role] = category.overwrites[role]  # Modified section
                    
            # Create the channel
            ticket_channel = await category.create_text_channel(f"{nation_id}", overwrites=overwrites)
            
            # Send the message to the ticket channel
            embed = discord.Embed(
                title="Application",
                description=f"Message from Guild: {message}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Nation Name", value=f"[{nation_name}](<https://politicsandwar.com/nation/id={nation_id}>)", inline=False)
            embed.add_field(name="Score", value=score, inline=False)
            embed.add_field(name="Cities", value=num_cities, inline=False)
            embed.add_field(name="Active Wars", value=wars, inline=False)
            await ticket_channel.send(embed=embed)
            await ticket_channel.send(ctx.author.mention)
            
            # Send a confirmation message
            embed = discord.Embed(
                title="Application",
                description=f"Application for {nation_name} has been submitted successfully.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Application",
                description="Nation not found.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Application",
            description=f"An error occurred: {e}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        
@bot.tree.command(name="apply", description="Apply to the alliance")
@app_commands.describe(nation_id="Provide your nation id")
async def apply(interaction: discord.Interaction, nation_id: str):
    try:
        # Check if the setup for applications is done
        guild_id = interaction.guild.id
        message = await db.get_ticket_message(guild_id)
        category_id = await db.get_ticket_category(guild_id)
        
        if category_id is None:
            return await interaction.response.send_message("```Setup for applications is not completed. Use /setup_applications command to complete the setup.```", ephemeral=True)
        
        # Query for provided nation id
        query = kit.query("nations", {"id": int(nation_id)}, "nation_name", "score", "num_cities", "offensive_wars_count", "defensive_wars_count")
        result = query.get()
        
        if result and result.nations:
            nation = result.nations[0]
            nation_name = nation.nation_name
            score = nation.score
            num_cities = nation.num_cities
            offensive_wars_count = nation.offensive_wars_count
            defensive_wars_count = nation.defensive_wars_count
            wars = offensive_wars_count + defensive_wars_count

            # Check if the user already has an open ticket
            existing_ticket = None
            for channel in interaction.guild.text_channels:
                if channel.name.startswith(f"{nation_id}"):
                    existing_ticket = channel
                    break

            if existing_ticket:
                return await interaction.response.send_message(f"You already have an application open in {existing_ticket.mention}.", ephemeral=True)

            # Create a new ticket channel
            category = bot.get_channel(int(category_id))
            if not category:
                return await interaction.response.send_message("Category not found.", ephemeral=True)
            
            # Define overwrites for the ticket channel
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
            for role in category.overwrites:
                if isinstance(role, discord.Role):
                    overwrites[role] = category.overwrites[role]  # Modified section
                    
            
            # Create the channel
            ticket_channel = await category.create_text_channel(f"{nation_id}", overwrites=overwrites)
            
            # Send the message to the ticket channel
            embed = discord.Embed(
                title="Application",
                description=f"Message from Guild: {message}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Nation Name", value=f"[{nation_name}](<https://politicsandwar.com/nation/id={nation_id}>)", inline=False)
            embed.add_field(name="Score", value=score, inline=False)
            embed.add_field(name="Cities", value=num_cities, inline=False)
            embed.add_field(name="Active Wars", value=wars, inline=False)
            await ticket_channel.send(embed=embed)
            await ticket_channel.send(interaction.user.mention)
            
            # Send a confirmation message
            embed = discord.Embed(
                title="Application",
                description=f"Application for {nation_name} has been submitted successfully.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Application",
                description="Nation not found.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="Application",
            description=f"An error occurred: {e}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)        

@bot.command(name="militarisation_aa", description="Check the alliance militarisation")
async def militarisation_aa(ctx, alliance_id: int):
    try:
        query = kit.query(
            "alliances", 
            {"id": alliance_id}, 
            "name, nations { nation_name num_cities vmode soldiers tanks aircraft ships alliance_position_info { position_level }}"
        )
        # get synchronously
        result = query.get()
        alliance = result.alliances[0]

        total_cities = sum(
            nation.num_cities for nation in alliance.nations 
            if nation.vmode == 0 and nation.alliance_position_info is not None and nation.alliance_position_info.position_level is not None and nation.alliance_position_info.position_level >= 1
        )

        soldiers = sum(
            nation.soldiers for nation in alliance.nations 
            if nation.vmode == 0 and nation.alliance_position_info is not None and nation.alliance_position_info.position_level is not None and nation.alliance_position_info.position_level >= 1
        )
        total_soldiers = int(total_cities) * 15000
        soldier_mm = int(soldiers) / int(total_soldiers) * 100

        tanks = sum(
            nation.tanks for nation in alliance.nations 
            if nation.vmode == 0 and nation.alliance_position_info is not None and nation.alliance_position_info.position_level is not None and nation.alliance_position_info.position_level >= 1
        )
        total_tanks = int(total_cities) * 1250
        tanks_mm = int(tanks) / int(total_tanks) * 100

        aircraft = sum(
            nation.aircraft for nation in alliance.nations 
            if nation.vmode == 0 and nation.alliance_position_info is not None and nation.alliance_position_info.position_level is not None and nation.alliance_position_info.position_level >= 1
        )
        total_aircraft = int(total_cities) * 75
        aircraft_mm = int(aircraft) / int(total_aircraft) * 100

        ships = sum(
            nation.ships for nation in alliance.nations
            if nation.vmode == 0 and nation.alliance_position_info is not None and nation.alliance_position_info.position_level is not None and nation.alliance_position_info.position_level >= 1
        )
        total_ships = int(total_cities) * 15
        ships_mm = int(ships) / int(total_ships) * 100

        total_militarization = (soldier_mm + tanks_mm + aircraft_mm + ships_mm) / 4

        # Formulate response
        await ctx.send(f"**Militarisation Analysis for {alliance.name}:**\n"
            f"```Soldiers: {soldiers:,}/{total_soldiers:,} ({soldier_mm:.2f}%)\n"
            f"Tanks: {tanks:,}/{total_tanks:,}({tanks_mm:.2f}%)\n"
            f"Aircraft: {aircraft:,}/{total_aircraft:,} ({aircraft_mm:.2f}%)\n"
            f"Ships: {ships:,}/{total_ships:,} ({ships_mm:.2f}%)\n"
            f"Total Militarisation: {total_militarization:.2f}%```"
                      )
    except Exception as e:
        await ctx.send(f"An error occurred while processing the command: {str(e)}")

@bot.tree.command(name="militarisation_aa", description="Check the alliance militarisation")
@app_commands.describe(alliance_id="The ID of the alliance")
async def militarisation_aa(interaction: discord.Interaction, alliance_id: int):
    try:
        query = kit.query(
            "alliances", 
            {"id": alliance_id}, 
            "name nations { nation_name num_cities vmode soldiers tanks aircraft ships alliance_position_info { position_level }}"
        )
        # get synchronously
        result = query.get()
        alliance = result.alliances[0]

        total_cities = sum(
            nation.num_cities for nation in alliance.nations 
            if nation.vmode == 0 and nation.alliance_position_info is not None and nation.alliance_position_info.position_level is not None and nation.alliance_position_info.position_level >= 1
        )

        soldiers = sum(
            nation.soldiers for nation in alliance.nations 
            if nation.vmode == 0 and nation.alliance_position_info is not None and nation.alliance_position_info.position_level is not None and nation.alliance_position_info.position_level >= 1
        )
        total_soldiers = int(total_cities) * 15000
        soldier_mm = int(soldiers) / int(total_soldiers) * 100

        tanks = sum(
            nation.tanks for nation in alliance.nations 
            if nation.vmode == 0 and nation.alliance_position_info is not None and nation.alliance_position_info.position_level is not None and nation.alliance_position_info.position_level >= 1
        )
        total_tanks = int(total_cities) * 1250
        tanks_mm = int(tanks) / int(total_tanks) * 100

        aircraft = sum(
            nation.aircraft for nation in alliance.nations 
            if nation.vmode == 0 and nation.alliance_position_info is not None and nation.alliance_position_info.position_level is not None and nation.alliance_position_info.position_level >= 1
        )
        total_aircraft = int(total_cities) * 75
        aircraft_mm = int(aircraft) / int(total_aircraft) * 100

        ships = sum(
            nation.ships for nation in alliance.nations
            if nation.vmode == 0 and nation.alliance_position_info is not None and nation.alliance_position_info.position_level is not None and nation.alliance_position_info.position_level >= 1
        )
        total_ships = int(total_cities) * 15
        ships_mm = int(ships) / int(total_ships) * 100

        total_militarization = (soldier_mm + tanks_mm + aircraft_mm + ships_mm) / 4

        # Formulate response
        await interaction.response.send_message(f"**Militarisation Analysis for {alliance.name}:**\n"
            f"```Soldiers: {soldiers:,}/{total_soldiers:,} ({soldier_mm:.2f}%)\n"
            f"Tanks: {tanks:,}/{total_tanks:,}({tanks_mm:.2f}%)\n"
            f"Aircraft: {aircraft:,}/{total_aircraft:,} ({aircraft_mm:.2f}%)\n"
            f"Ships: {ships:,}/{total_ships:,} ({ships_mm:.2f}%)\n"
            f"Total Militarisation: {total_militarization:.2f}%```"
        )
    except Exception as e:
        await interaction.response.send_message(f"An error occurred while processing the command: {str(e)}")

@bot.tree.command(name="set_defensive_channel", description="Set the defensive wars channel for the guild.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def set_defensive_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    try:
        guild_id = interaction.guild_id
        def_channel = str(channel.id)
        
        alliance_id = await db.get_guild_alliance(guild_id)
        if alliance_id is None:
            await interaction.response.send_message("You need to register an alliance. Use /verify_aa or |verify_aa")
            return
        # Add the def_channel to the database
        await db.add_guild_def_channel(guild_id, def_channel)
        await db.close_connection()

        await interaction.response.send_message(f"Default defense channel has been set to {channel.mention}.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
@bot.tree.command(name="set_offensive_channel", description="Set the offensive wars channel for the guild.")
@discord.app_commands.checks.has_permissions(administrator=True)
async def set_offensive_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    try:
        guild_id = interaction.guild_id
        off_channel = str(channel.id)
        
        alliance_id = await db.get_guild_alliance(guild_id)
        if alliance_id is None:
            await interaction.response.send_message("You need to register an alliance. Use /verify_aa or |verify_aa.")
            return
        # Add the def_channel to the database
        await db.add_guild_off_channel(guild_id, off_channel)
        await db.close_connection()

        await interaction.response.send_message(f"Offensive Wars channel has been set to {channel.mention}.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"An error occured: {e}", ephemeral=True)

@bot.tree.command(name="treaty", description="Retrieve the treaties of a given alliance ID.")
@app_commands.describe(alliance_id="The ID of the alliance to retrieve treaties for")
async def treaty_command(interaction: discord.Interaction, alliance_id: int):
    query = kit.query("alliances", {"id": alliance_id}, "treaties{treaty_type, alliance1{name}, alliance2{name}, turns_left}")
    result = query.get()
    
    embed = discord.Embed(title="Treaties Information", color=discord.Color.blue())
    
    if result and result.alliances and result.alliances[0] and result.alliances[0].treaties:
        treaties = result.alliances[0].treaties
        for treaty in treaties:
            alliance1_name = treaty.alliance1.name
            treaty_type = treaty.treaty_type
            alliance2_name = treaty.alliance2.name
            turns_left = treaty.turns_left
            embed.add_field(name=f"{alliance1_name}┃{treaty_type} -> {alliance2_name}",
                            value=f"Turns Left: {turns_left}", inline=False)
    else:
        embed.description = "No treaties found for the given alliance ID."

    await interaction.response.send_message(embed=embed)

@bot.command(name="treaty", help="Retrieve the treaties of a given alliance ID.")
async def treaty_command(ctx, alliance_id: int):
    query = kit.query("alliances", {"id": alliance_id}, "treaties{treaty_type, alliance1{name}, alliance2{name}, turns_left}")
    result = query.get()
    
    embed = discord.Embed(title="Treaties Information", color=discord.Color.blue())
    
    if result and result.alliances and result.alliances[0] and result.alliances[0].treaties:
        treaties = result.alliances[0].treaties
        for treaty in treaties:
            alliance1_name = treaty.alliance1.name
            treaty_type = treaty.treaty_type
            alliance2_name = treaty.alliance2.name
            turns_left = treaty.turns_left
            embed.add_field(name=f"{alliance1_name}┃{treaty_type} -> {alliance2_name}",
                            value=f"Turns Left: {turns_left}", inline=False)
    else:
        embed.description = "No treaties found for the given alliance ID."

    await ctx.send(embed=embed)    

@bot.command(name='fast_beige', description='Find Fastest way to finish the war')
async def check_map(ctx, resistance: int):
    # Define the resistance and MAP values for each attack type
    attack_types = [
        {'name': 'Naval', 'resistance': 14, 'map': 4},
        {'name': 'Aircraft', 'resistance': 12, 'map': 4},
        {'name': 'Ground', 'resistance': 10, 'map': 3},
    ]

    # Initialize minimum MAP and best attack plan
    min_map = float('inf')
    best_plan = None

    # Explore all combinations of attacks
    for naval_attacks in range((resistance // attack_types[0]['resistance']) + 1):
        for aircraft_attacks in range((resistance // attack_types[1]['resistance']) + 1):
            for ground_attacks in range((resistance // attack_types[2]['resistance']) + 1):
                total_resistance = (
                    naval_attacks * attack_types[0]['resistance'] +
                    aircraft_attacks * attack_types[1]['resistance'] +
                    ground_attacks * attack_types[2]['resistance']
                )
                total_map = (
                    naval_attacks * attack_types[0]['map'] +
                    aircraft_attacks * attack_types[1]['map'] +
                    ground_attacks * attack_types[2]['map']
                )
                
                # Check if this combination meets or exceeds the resistance and uses fewer MAPs
                if total_resistance >= resistance and total_map < min_map:
                    min_map = total_map
                    best_plan = (naval_attacks, aircraft_attacks, ground_attacks, total_map)

    # Send the result as a response
    if best_plan:
        naval_attacks, aircraft_attacks, ground_attacks, total_map = best_plan
        await ctx.send(
            f"To reduce resistance from {resistance} to 0, use:\n"
            f"Naval attacks: {naval_attacks}\n"
            f"Aircraft attacks: {aircraft_attacks}\n"
            f"Ground attacks: {ground_attacks}\n"
            f"Total MAP used: {total_map}"
        )
    else:
        await ctx.send("No valid attack combination found.")   
 
@bot.tree.command(name='fastest_beige', description='Find the fastest way to finish the war')
@app_commands.describe(resistance='The amount of resistance to reduce')
async def check_map(interaction: discord.Interaction, resistance: int):
    # Define the resistance and MAP values for each attack type
    attack_types = [
        {'name': 'Naval', 'resistance': 14, 'map': 4},
        {'name': 'Aircraft', 'resistance': 12, 'map': 4},
        {'name': 'Ground', 'resistance': 10, 'map': 3},
    ]

    # Initialize minimum MAP and best attack plan
    min_map = float('inf')
    best_plan = None

    # Explore all combinations of attacks
    for naval_attacks in range((resistance // attack_types[0]['resistance']) + 1):
        for aircraft_attacks in range((resistance // attack_types[1]['resistance']) + 1):
            for ground_attacks in range((resistance // attack_types[2]['resistance']) + 1):
                total_resistance = (
                    naval_attacks * attack_types[0]['resistance'] +
                    aircraft_attacks * attack_types[1]['resistance'] +
                    ground_attacks * attack_types[2]['resistance']
                )
                total_map = (
                    naval_attacks * attack_types[0]['map'] +
                    aircraft_attacks * attack_types[1]['map'] +
                    ground_attacks * attack_types[2]['map']
                )
                
                # Check if this combination meets or exceeds the resistance and uses fewer MAPs
                if total_resistance >= resistance and total_map < min_map:
                    min_map = total_map
                    best_plan = (naval_attacks, aircraft_attacks, ground_attacks, total_map)

    # Send the result as a response
    if best_plan:
        naval_attacks, aircraft_attacks, ground_attacks, total_map = best_plan
        await interaction.response.send_message(
            f"To reduce resistance from {resistance} to 0, use:\n"
            f"Naval attacks: {naval_attacks}\n"
            f"Aircraft attacks: {aircraft_attacks}\n"
            f"Ground attacks: {ground_attacks}\n"
            f"Total MAP used: {total_map}"
        )
    else:
        await interaction.response.send_message("No valid attack combination found.")

keep_alive()    
bot.run(TOKEN)