import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.all()

# Store auto-chat channel
AI_CHANNEL = None


# ======================
# CUSTOM BOT CLASS
# ======================
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.synced = False  # Prevent double sync

    async def setup_hook(self):
        if not self.synced:
            await self.tree.sync()  # Sync slash commands globally
            self.synced = True
            print("Slash commands synced.")

    async def on_ready(self):
        print(f"Bot is online as {self.user}")


bot = MyBot()


# ======================
# TAG RESPONSE + AUTOCHAT
# ======================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    global AI_CHANNEL

    # Respond when bot is tagged
    if bot.user in message.mentions:
        await message.channel.send(f"Hello {message.author.mention}, what do you need?")
        return

    # Auto-response in AI channel (AI will be added later)
    if AI_CHANNEL and message.channel.id == AI_CHANNEL:
        await message.channel.send("AI system is coming soon…")
        return

    await bot.process_commands(message)


# ======================
# SLASH COMMANDS
# ======================

# /ping
@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Pong! `{round(bot.latency * 1000)}ms`"
    )


# /avatar
@bot.tree.command(name="avatar", description="Show a user's avatar")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"{user.name}'s Avatar")
    embed.set_image(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)


# /userinfo
@bot.tree.command(name="userinfo", description="Shows info about a user")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"User Info - {user.name}")
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Top Role", value=user.top_role)
    embed.set_thumbnail(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)


# /clear
@bot.tree.command(name="clear", description="Clear messages")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(
        f"Cleared {amount} messages.", ephemeral=True
    )


# /kick
@bot.tree.command(name="kick", description="Kick a member")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {member.name}")


# /ban
@bot.tree.command(name="ban", description="Ban a member")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f"Banned {member.name}")


# /lock
@bot.tree.command(name="lock", description="Lock this channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("🔒 Channel locked")


# /unlock
@bot.tree.command(name="unlock", description="Unlock this channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
    await interaction.response.send_message("🔓 Channel unlocked")


# /slowmode
@bot.tree.command(name="slowmode", description="Set slowmode in this channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"⏳ Slowmode set to {seconds} seconds")


# /announce
@bot.tree.command(name="announce", description="Send an announcement")
@app_commands.checks.has_permissions(administrator=True)
async def announce(interaction: discord.Interaction, message: str):
    embed = discord.Embed(title="📢 Announcement", description=message, color=0x00ffea)
    embed.set_footer(text=f"By {interaction.user}")
    await interaction.response.send_message(embed=embed)


# /setchannel
@bot.tree.command(name="setchannel", description="Set channel for auto-chat")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    global AI_CHANNEL
    AI_CHANNEL = channel.id
    await interaction.response.send_message(f"Auto-chat enabled in {channel.mention}")


# ======================
# RUN BOT
# ======================
bot.run(os.getenv("TOKEN"))
