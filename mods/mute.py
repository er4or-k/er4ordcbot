import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import timedelta, datetime
import re
from database.models import mute_collection
from pymongo import MongoClient

def parse_duration(duration: str) -> int:
    match = re.match(r"(\d+)([mhd])", duration.lower())
    if not match:
        raise ValueError("Invalid time format. Use `10m`, `1h`, `2d`.")  
    value, unit = int(match.group(1)), match.group(2)
    
    if unit == "m":
        return value
    elif unit == "h":
        return value * 60
    elif unit == "d":
        return value * 1440

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_mutes.start()

    def cog_unload(self):
        self.check_mutes.cancel()

    @tasks.loop(seconds=30)
    async def check_mutes(self):
        now = datetime.utcnow()
        mutes = list(mute_collection.find({}))

        for mute in mutes:
            end_time = mute["end_time"]
            if now >= end_time:
                guild = self.bot.get_guild(mute["guild_id"])
                if guild:
                    member = guild.get_member(mute["user_id"])
                    if member:
                        await member.timeout(None, reason="Mute Expired")
                        channel = guild.get_channel(mute["channel_id"])
                        if channel:
                            embed = discord.Embed(
                                title="🔊 Mute Expired",
                                description=f"✅ {member.mention} has been unmuted.",
                                color=discord.Color.green()
                            )
                            await channel.send(embed=embed)
                mute_collection.delete_one({"user_id": mute["user_id"]})

    async def mute_user(self, ctx, user, duration, reason):
        try:
            duration_td = parse_duration(duration)
            end_time = datetime.utcnow() + timedelta(minutes=duration_td)
            await user.timeout(timedelta(minutes=duration_td), reason=reason)
            
            mute_collection.insert_one({
                "user_id": user.id,
                "guild_id": ctx.guild.id,
                "channel_id": ctx.channel.id,
                "end_time": end_time,
            })

            embed = discord.Embed(
                title="🔇 User Muted",
                description=f"✅ **{user.mention} has been muted for `{duration}`.**",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)

            if isinstance(ctx, discord.Interaction):
                await ctx.response.send_message(embed=embed)
            else:
                await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(
                title="Mute Failed ❌",
                description=f"I don't have permission to mute {user.mention}!",
                color=discord.Color.red()
            ))

    @commands.command(name="mute")
    async def mute(self, ctx, user: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
        if user is None or duration is None:
            return await ctx.send(embed=discord.Embed(
                title="Mute Failed ❌",
                description="Please mention the user and duration! Example: `!!mute @user 10m reason`",
                color=discord.Color.red()
            ))

        if user == ctx.author:
            return await ctx.send(embed=discord.Embed(
                title="Mute Failed ❌",
                description="You cannot mute yourself!",
                color=discord.Color.red()
            ))

        await self.mute_user(ctx, user, duration, reason)

    @app_commands.command(name="mute", description="Mute a member")
    @app_commands.describe(user="The member to mute", duration="Duration of mute (e.g. 10m, 1h)", reason="Reason for mute")
    async def mute_slash(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "No reason provided"):
        if user == interaction.user:
            return await interaction.response.send_message(embed=discord.Embed(
                title="Mute Failed ❌",
                description="You cannot mute yourself!",
                color=discord.Color.red()
            ), ephemeral=True)

        await self.mute_user(interaction, user, duration, reason)

    @commands.command(name="unmute")
    async def unmute(self, ctx, user: discord.Member = None):
        if user is None:
            return await ctx.send(embed=discord.Embed(
                title="Mute Failed ❌",
                description="Please mention a user to unmute!",
                color=discord.Color.red()
            ))

        await user.timeout(None, reason="Unmuted")
        mute_collection.delete_one({"user_id": user.id})

        await ctx.send(embed=discord.Embed(
            title="🔊 User Unmuted",
            description=f"{user.mention} has been unmuted.",
            color=discord.Color.green()
        ))
    @app_commands.command(name="unmute", description="Unmute a member")
    @app_commands.describe(user="The member to unmute")
    async def unmute_slash(self, interaction: discord.Interaction, user: discord.Member):
        await user.timeout(None, reason="Unmuted")
        mute_collection.delete_one({"user_id": user.id})

        embed = discord.Embed(
            title="🔊 User Unmuted",
            description=f"{user.mention} has been unmuted.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Mute(bot))

