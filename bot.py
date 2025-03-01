import discord
from discord.ext import commands
from discord import app_commands
import os
import subprocess  # Import subprocess to run app.py

TOKEN = os.getenv("BOT_TOKEN")  # Get token from environment variable

# Start the web server (app.py) in a separate process
subprocess.Popen(["python", "app.py"])
#hlo
# Define bot with prefix and slash command support
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(activity=discord.Game("Bot is currently in development"))
    print(f"Logged in as {bot.user}")

# Slash Command: /help
@bot.tree.command(name="help", description="Shows bot status")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message("Bot is currently inactive.")

# Prefix Command: !!about
@bot.command(name="about")
async def about(ctx):
    await ctx.send("This Bot Is Created By @er4or.k.")

bot.run(TOKEN)
