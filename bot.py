import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ----- SETTINGS -----
AI_CHANNEL = None        # Replace with channel ID later
BOT_PREFIX = None        # If you want custom trigger words


# ===== BOT READY =====

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(e)


# ====== TRIGGER WHEN BOT IS TAGGED ======

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # If someone tags the bot (@Bot)
    if bot.user in message.mentions:
        await message.channel.send(f"Hello {message.author.mention}, how can I help you?")
        return

    # If AI channel is set → respond automatically
    if AI_CHANNEL and message.channel.id == AI_CHANNEL:
        await message.channel.send(f"AI will answer here soon… (Feature pending)")
        return

    await bot.process_commands(message)


# ========= SLASH COMMANDS ==========

# /ping
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! `{round(bot.latency * 1000)}ms`")


# /avatar @user
@bot.tree.command(name="avatar", description="Show someone's avatar")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"{user.name}'s Avatar")
    embed.set_image(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)


# /userinfo @user
@bot.tree.command(name="userinfo", description="Shows info about a user")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"User Info - {user.name}")
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Roles", value=", ".join([r.name for r in user.roles]))
    embed.set_thumbnail(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)


# ===== ADMIN COMMANDS =====

# /clear amount
@bot.tree.command(name="clear", description="Clear messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"Cleared {amount} messages.", ephemeral=True)


# /kick user reason
@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {member.name}")


# /ban user reason
@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"Banned {member.name}")


# ===== SET AI CHANNEL =====

@bot.tree.command(name="setai", description="Set the channel where bot responds without tag")
@app_commands.checks.has_permissions(administrator=True)
async def set_ai_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    global AI_CHANNEL
    AI_CHANNEL = channel.id
    await interaction.response.send_message(f"AI channel set to {channel.mention}")


# ===== RUN BOT =====
bot.run(os.getenv("TOKEN"))
