import os
import discord
from discord.ext import commands
import random
import datetime
import asyncio
import time

# Bot initialization with required intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Needed to manage members and mute them
bot = commands.Bot(command_prefix="!", intents=intents)

# Data storage
challenges = {}
meetups = {}
user_participation = {}
user_attendance = {}
last_login = {}
user_scores = {}

# Simple calculator command
@bot.command()
async def calculator(ctx):
    """🧮 A simple calculator with a timeout for user inputs."""
    await ctx.send("💡 **Simple Calculator**\nSelect operation:\n1️⃣ Add\n2️⃣ Subtract\n3️⃣ Multiply\n4️⃣ Divide")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        # Ask for operation choice
        choice_msg = await bot.wait_for('message', check=check, timeout=30.0)
        choice = choice_msg.content

        # Ask for numbers
        await ctx.send("🔢 Enter first number:")
        num1_msg = await bot.wait_for('message', check=check, timeout=30.0)
        num1 = float(num1_msg.content)

        await ctx.send("🔢 Enter second number:")
        num2_msg = await bot.wait_for('message', check=check, timeout=30.0)
        num2 = float(num2_msg.content)

        if choice == '1':
            await ctx.send(f"{num1} ➕ {num2} = {num1 + num2}")
        elif choice == '2':
            await ctx.send(f"{num1} ➖ {num2} = {num1 - num2}")
        elif choice == '3':
            await ctx.send(f"{num1} ✖️ {num2} = {num1 * num2}")
        elif choice == '4':
            if num2 != 0:
                await ctx.send(f"{num1} ➗ {num2} = {num1 / num2}")
            else:
                await ctx.send("🚨 Error: Division by zero!")
        else:
            await ctx.send("❌ Invalid operation. Please select a valid operation.")

    except asyncio.TimeoutError:
        await ctx.send("⏳ You took too long to respond. Please try again.")

# Time function with mute feature
@bot.command()
async def timeon(ctx, user: discord.Member = None):
    """⏰ Display current time and mute a tagged user for the timeout period."""
    if user is None:
        await ctx.send("⚠️ You need to mention a user to mute.")
        return

    # Create a mute role if it doesn't already exist
    guild = ctx.guild
    mute_role = discord.utils.get(guild.roles, name="Muted")
    
    if mute_role is None:
        mute_role = await guild.create_role(name="Muted", reason="Mute role for timeouts")
        # Set permissions so that the role can't send messages in any channel
        for channel in guild.text_channels:
            await channel.set_permissions(mute_role, send_messages=False)

    # Mute the user
    await user.add_roles(mute_role)
    await ctx.send(f"{user.name} 🤐, you are muted for 30 seconds while I get the current time...")

    try:
        current_time = time.strftime("%H:%M:%S %p")  # Format as Hour:Minute:Second AM/PM
        await asyncio.sleep(30)  # Timeout period of 30 seconds for the user to wait
        await ctx.send(f"⏰ The current time is: {current_time}")
    except asyncio.TimeoutError:
        await ctx.send("⏳ You took too long to get the time. Please try again.")

    # Unmute the user after the timeout expires
    await user.remove_roles(mute_role)
    await ctx.send(f"{user.name} 🙊, you are no longer muted.")

# Timeout function
@bot.command()
async def timeout(ctx, seconds: int):
    """⏳ Set a timeout for the bot to wait before responding."""
    await ctx.send(f"⏰ Waiting for {seconds} seconds before responding...")
    await asyncio.sleep(seconds)
    await ctx.send(f"{seconds} seconds have passed! ⏱️")

# Challenge creation
@bot.command()
async def create_challenge(ctx, challenge_name: str, description: str, duration: int):
    """🏆 Create a new group challenge."""
    challenge_id = random.randint(1000, 9999)
    challenge_data = {
        "creator": ctx.author.id,
        "name": challenge_name,
        "description": description,
        "duration": duration,
        "participants": [ctx.author.id],  # The creator is the first participant
        "start_time": datetime.datetime.now(),
        "completed": False,
        "reviews": [],
        "milestones": []
    }
    challenges[challenge_id] = challenge_data
    user_participation.setdefault(ctx.author.id, []).append(challenge_id)
    await ctx.send(f"🎉 Challenge '{challenge_name}' created successfully! Challenge ID: {challenge_id}")

# Join an existing challenge
@bot.command()
async def join_challenge(ctx, challenge_id: int):
    """🤝 Join a group challenge by its ID."""
    challenge = challenges.get(challenge_id)
    if not challenge:
        await ctx.send(f"❌ No challenge found with ID {challenge_id}.")
        return

    if ctx.author.id in challenge["participants"]:
        await ctx.send("🚫 You are already a participant in this challenge.")
        return

    challenge["participants"].append(ctx.author.id)
    user_participation.setdefault(ctx.author.id, []).append(challenge_id)
    await ctx.send(f"{ctx.author.name} ✅ has joined the challenge '{challenge['name']}'.")

# List all active challenges
@bot.command()
async def list_challenges(ctx):
    """📜 List all active challenges."""
    if not challenges:
        await ctx.send("⚠️ No active challenges at the moment.")
        return

    message = "🔹 **Active Challenges** 🔹\n"
    for challenge_id, challenge in challenges.items():
        creator = bot.get_user(challenge['creator'])
        creator_name = creator.name if creator else "Unknown User"
        message += (f"**ID**: {challenge_id} - {challenge['name']} (Created by {creator_name})\n"
                    f"**Description**: {challenge['description']}\n"
                    f"**Duration**: {challenge['duration']} hours\n\n")
    await ctx.send(message)

# Create a new meetup
@bot.command()
async def create_meetup(ctx, topic: str, date_time: str):
    """📅 Create a new meetup."""
    try:
        meetup_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M")
    except ValueError:
        await ctx.send("❌ Invalid date-time format. Use YYYY-MM-DD HH:MM.")
        return

    meetup_id = random.randint(1000, 9999)
    meetup_data = {
        "organizer": ctx.author.id,
        "topic": topic,
        "time": meetup_time,
        "attendees": [ctx.author.id]
    }
    meetups[meetup_id] = meetup_data
    user_attendance.setdefault(ctx.author.id, []).append(meetup_id)
    await ctx.send(f"🎉 Meetup on '{topic}' created successfully! Scheduled for {meetup_time}.")

# Join an existing meetup
@bot.command()
async def join_meetup(ctx, meetup_id: int):
    """🤝 Join a virtual meetup by its ID."""
    meetup = meetups.get(meetup_id)
    if not meetup:
        await ctx.send(f"❌ No meetup found with ID {meetup_id}.")
        return

    if ctx.author.id in meetup["attendees"]:
        await ctx.send("🚫 You are already attending this meetup.")
        return

    meetup["attendees"].append(ctx.author.id)
    user_attendance.setdefault(ctx.author.id, []).append(meetup_id)
    await ctx.send(f"{ctx.author.name} ✅ has joined the meetup '{meetup['topic']}' scheduled for {meetup['time']}.")

# List upcoming meetups
@bot.command()
async def list_meetups(ctx):
    """📅 List upcoming meetups."""
    if not meetups:
        await ctx.send("⚠️ No upcoming meetups at the moment.")
        return

    message = "🔹 **Upcoming Meetups** 🔹\n"
    for meetup_id, meetup in meetups.items():
        organizer = bot.get_user(meetup['organizer'])
        organizer_name = organizer.name if organizer else "Unknown User"
        message += (f"**ID**: {meetup_id} - {meetup['topic']} (Organized by {organizer_name})\n"
                    f"**Scheduled for**: {meetup['time']}\n\n")
    await ctx.send(message)

# Claim daily reward
@bot.command()
async def daily_reward(ctx):
    """🎁 Claim your daily reward."""
    user_id = ctx.author.id
    now = datetime.datetime.now()

    if user_id in last_login and (now - last_login[user_id]).days == 0:
        await ctx.send("🚫 You have already claimed your daily reward today!")
        return

    last_login[user_id] = now
    reward = random.choice([100, 250, 500])  # Random reward amount
    user_scores[user_id] = user_scores.get(user_id, 0) + reward  # Update the global score
    await ctx.send(f"🎉 Congratulations! You've claimed your daily reward of {reward} points. 🎁")

# Show the global leaderboard
@bot.command()
async def leaderboard(ctx):
    """🏆 Show the global leaderboard."""
    leaderboard = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    message = "**🏅 Global Leaderboard 🏅**\n"
    for i, (user_id, score) in enumerate(leaderboard[:5], start=1):
        user_name = bot.get_user(user_id).name
        message += f"{i}. {user_name} - {score} points\n"

    await ctx.send(message)

# Show a user's stats
@bot.command()
async def stats(ctx):
    """📊 View a user's stats for challenges and meetups."""
    user_id = ctx.author.id
    challenge_count = len(user_participation.get(user_id, []))
    meetup_count = len(user_attendance.get(user_id, []))

    await ctx.send(f"{ctx.author.name}'s Stats 📊:\n"
                   f"🔹 Challenges Joined: {challenge_count}\n"
                   f"🔹 Meetups Attended: {meetup_count}")

# Error handling for command errors
@bot.event
async def on_command_error(ctx, error):
    """Handle errors gracefully."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"⚠️ Missing argument: {error.param}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Invalid command. Type !commands for a list of available commands.")
    else:
        await ctx.send("❌ An error occurred. Please try again later.")

# Reminder command
@bot.command()
async def remindme(ctx, time: int, *, reminder: str):
    """⏰ Set a reminder for yourself."""
    await ctx.send(f"Got it! I'll remind you in {time} minutes about: {reminder}")
    
    # Convert minutes to seconds for the sleep
    await asyncio.sleep(time * 60)  # Time in seconds
    await ctx.send(f"⏰ Reminder: {reminder}")

# List commands command
@bot.command()
async def commands(ctx):
    """📜 List all available commands."""
    command_list = """
    **Bot Commands:**
    - `!calculator`: 🧮 Use a simple calculator.
    - `!timeon <user>`: ⏰ Mute a user for 30 seconds while checking the time.
    - `!timeout <seconds>`: ⏳ Set a timeout for the bot to wait before responding.
    - `!create_challenge <name> <description> <duration>`: 🏆 Create a new challenge.
    - `!join_challenge <challenge_id>`: 🤝 Join an existing challenge.
    - `!list_challenges`: 📜 List all active challenges.
    - `!create_meetup <topic> <date_time>`: 📅 Create a new meetup.
    - `!join_meetup <meetup_id>`: 🤝 Join an existing meetup.
    - `!list_meetups`: 📅 List upcoming meetups.
    - `!daily_reward`: 🎁 Claim your daily reward.
    - `!leaderboard`: 🏆 View the global leaderboard.
    - `!stats`: 📊 View your personal stats for challenges and meetups.
    - `!remindme <time> <message>`: ⏰ Set a reminder with a specific time and message.
    """
    await ctx.send(command_list)

# Bot startup event
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Run the bot
bot.run('Token')  # Replace with your actual bot token.
