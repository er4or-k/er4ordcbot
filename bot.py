import discord
from discord import app_commands
import os
import subprocess 

subprocess.Popen(['python', 'app.py'])
TOKEN = "OTUyNDIyMjMzNTYzODczMzQy.GGaP3s.SoGN50Ic7KdYmEUzu8kY2iy0Ld8PCa-qIUxyaI" # Get token from environment variable

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        await self.tree.sync()
        await self.change_presence(activity=discord.Game("Bot is currently in development"))
        print(f"Logged in as {self.user}")

bot = MyBot()

@bot.tree.command(name="help", description="Shows bot status")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message("Bot is currently inactive.", ephemeral=True)

bot.run(TOKEN)
