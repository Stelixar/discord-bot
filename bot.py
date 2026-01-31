import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print("Slash sync failed:", e)

# ========== SLASH COMMANDS ==========

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Pong! `{round(bot.latency * 1000)}ms`"
    )

@bot.tree.command(name="avatar", description="Show a user's avatar")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"{user.name}'s Avatar")
    embed.set_image(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="Shows user info")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"User Info - {user.name}")
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Top Role", value=user.top_role)
    embed.set_thumbnail(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clear", description="Clear messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(
        f"Cleared {amount} messages.", ephemeral=True
    )

bot.run(os.getenv("TOKEN"))
