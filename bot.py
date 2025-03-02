import discord
from discord.ext import commands
from discord import app_commands
import os
from config import BOT_TOKEN

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="!!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")

    # Load Cogs
    try:
        await bot.load_extension("mods.kick")
        await bot.load_extension("mods.ban")
        await bot.load_extension("mods.afk")
        print("✅cog loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load cog: {e}")

    # Syncing Slash Commands
    try:
        await bot.tree.sync()
        print(f"✅ Synced {len(await bot.tree.sync())} slash commands.")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")

    # Set bot status
    await bot.change_presence(activity=discord.Game("Bot is currently in development"))

# Slash Command: /help
@bot.tree.command(name="help", description="Shows bot status")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📌 Bot Status",
        description="Bot is currently inactive!!",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

# Prefix Command: !!about
@bot.command(name="about")
async def about(ctx):
    embed = discord.Embed(
        title="ℹ️ About",
        description="This Bot Is Created By @er4or.k.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

bot.run(BOT_TOKEN)
