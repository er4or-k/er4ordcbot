import discord
from discord.ext import commands
from discord import app_commands
from pymongo import MongoClient
import datetime

# MongoDB setup
client = MongoClient('mongodb+srv://kiranpoo7ary:FPcsopE32NSR1zfP@cluster0.leb3q.mongodb.net/afk_db?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true')  # Replace with your MongoDB connection string
db = client['afk_db']
afk_collection = db['afk_data']

class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Prefix Command: !!afk (Everyone can use it)
    @commands.command()
    async def afk(self, ctx, *, reason="No reason provided"):
        user = ctx.author

        # Check if the user is already AFK
        existing_afk = afk_collection.find_one({"user_id": str(user.id), "afk_status": True})
        if existing_afk:
            embed = discord.Embed(
                title="You are already AFK",
                description=f"{user.mention}, you are already marked as AFK!",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        # Update the nickname to [AFK]
        new_nickname = f"[AFK] {user.display_name}"
        await user.edit(nick=new_nickname)

        # Store AFK status in MongoDB
        timestamp = datetime.datetime.utcnow()
        afk_collection.update_one(
            {"user_id": str(user.id)},
            {"$set": {
                "afk_status": True,
                "afk_reason": reason,
                "timestamp": timestamp
            }},
            upsert=True
        )

        embed = discord.Embed(
            title="You are now AFK",
            description=f"{user.mention}, you are now marked as AFK!\nReason: {reason}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    # Slash Command: /afk (Everyone can use it)
    @app_commands.command(name="afk", description="Mark yourself as AFK")
    async def afk_slash(self, interaction: discord.Interaction, reason: str = "No reason provided"):
        user = interaction.user

        # Check if the user is already AFK
        existing_afk = afk_collection.find_one({"user_id": str(user.id), "afk_status": True})
        if existing_afk:
            embed = discord.Embed(
                title="You are already AFK",
                description=f"{user.mention}, you are already marked as AFK!",
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed)

        # Update the nickname to [AFK]
        new_nickname = f"[AFK] {user.display_name}"
        await user.edit(nick=new_nickname)

        # Store AFK status in MongoDB
        timestamp = datetime.datetime.utcnow()
        afk_collection.update_one(
            {"user_id": str(user.id)},
            {"$set": {
                "afk_status": True,
                "afk_reason": reason,
                "timestamp": timestamp
            }},
            upsert=True
        )

        embed = discord.Embed(
            title="You are now AFK",
            description=f"{user.mention}, you are now marked as AFK!\nReason: {reason}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    # Handle mentions: Show if user is AFK and how long ago
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check if someone mentions an AFK user
        for mentioned_user in message.mentions:
            afk_data = afk_collection.find_one({"user_id": str(mentioned_user.id), "afk_status": True})
            if afk_data:
                afk_time = afk_data["timestamp"]
                reason = afk_data["afk_reason"]
                time_ago = self.time_since(afk_time)

                # Send the AFK status of the mentioned user
                embed = discord.Embed(
                    title=f"{mentioned_user.display_name} is AFK",
                    description=f"Reason: {reason if reason != 'No reason provided' else 'No reason provided'}\n{mentioned_user.mention} has been AFK for {time_ago}.",
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)

        # If the user is AFK and sends a message, remove AFK status
        afk_data = afk_collection.find_one({"user_id": str(message.author.id), "afk_status": True})
        if afk_data:
            # Set AFK status to False and remove [AFK] prefix from nickname
            afk_collection.update_one(
                {"user_id": str(message.author.id)},
                {"$set": {"afk_status": False}}  # Set AFK status to False
            )

            # Remove the [AFK] prefix from the nickname
            user = message.author
            if user.nick and user.nick.startswith("[AFK] "):
                new_nickname = user.nick.replace("[AFK] ", "")
                await user.edit(nick=new_nickname)

            # Send embed for removing AFK status
            embed = discord.Embed(
                title="AFK status removed",
                description=f"{message.author.mention}, your AFK status has been removed. You are now active.",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed)

    # Calculate time difference
    def time_since(self, timestamp):
        now = datetime.datetime.utcnow()
        diff = now - timestamp
        seconds = diff.total_seconds()

        if seconds < 60:
            return f"{int(seconds)} second{'s' if int(seconds) > 1 else ''}"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{int(minutes)} minute{'s' if int(minutes) > 1 else ''}"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{int(hours)} hour{'s' if int(hours) > 1 else ''}"
        else:
            days = seconds // 86400
            return f"{int(days)} day{'s' if int(days) > 1 else ''}"

async def setup(bot):
    await bot.add_cog(AFK(bot))
