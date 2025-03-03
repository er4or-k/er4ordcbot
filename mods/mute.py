import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import timedelta, datetime
import re


def parse_duration(duration: str) -> int:
    match = re.match(r"(\d+)([mhd])", duration.lower())  # Match format like '1h', '30m', '2d'
    
    if not match:
        raise ValueError("Invalid time format. Use `10m`, `1h`, `2d`, etc.")
    
    value, unit = int(match.group(1)), match.group(2)

    if unit == "m":
        return value  # Minutes
    elif unit == "h":
        return value * 60  # Convert hours to minutes
    elif unit == "d":
        return value * 1440  # Convert days to minutes


class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_mutes.start()
        self.muted_users = {}  # Stores {user_id: (end_time, channel_id, guild_id)}

    def cog_unload(self):
        self.check_mutes.cancel()

    @tasks.loop(seconds=30)
    async def check_mutes(self):
        now = datetime.utcnow()
        to_remove = []
        for user_id, (end_time, channel_id, guild_id) in self.muted_users.items():
            if now >= end_time:
                guild = self.bot.get_guild(guild_id)  # Get the guild dynamically
                if guild:
                    user = guild.get_member(user_id)
                    if user:
                        await user.timeout(None, reason="Mute expired")
                        channel = guild.get_channel(channel_id)
                        if channel:
                            embed = discord.Embed(
                                title="🔊 Mute Expired",
                                description=f"✅ **{user.mention} has been unmuted.**",
                                color=discord.Color.green()
                            )
                            await channel.send(embed=embed)
                to_remove.append(user_id)
        for user_id in to_remove:
            del self.muted_users[user_id]

    @commands.command(name="mute")
    async def mute(self, ctx, user: discord.Member, duration: str, *, reason: str = "No reason provided"):

        if user == ctx.author:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{ctx.author.mention}, You cannot mute yourself!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        try:
            duration_td = parse_duration(str(duration))  # Ensure `duration` is passed as a string like "10m", "1h", "1d"
            if duration_td is None:
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"{ctx.author.mention}, Invalid duration format! Use `Xm`, `Xh`, or `Xd` (e.g., `10m`, `2h`, `1d`).",
                    color=discord.Color.red()
                )
                return await ctx.send(embed=embed)

            await user.timeout(timedelta(minutes=duration_td), reason=reason)
            self.muted_users[user.id] = (datetime.utcnow() + timedelta(minutes=duration_td), ctx.channel.id, ctx.guild.id)

            embed = discord.Embed(
                title="🔇 User Muted",
                description=f"✅ **{user.mention} has been muted for `{duration}` minutes.**",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{ctx.author.mention}, I don't have permission to mute {user.mention}!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{ctx.author.mention}, An error occurred while muting {user.mention}: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="unmute")
    async def unmute(self, ctx, user: discord.Member = None):
        if user is None:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{ctx.author.mention}, Please mention a user to unmute!",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        try:
            await user.timeout(None, reason="Unmuted")

            embed = discord.Embed(
                title="🔊 User Unmuted",
                description=f"✅ **{user.mention} has been unmuted.**",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{ctx.author.mention}, I don't have permission to unmute {user.mention}!",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{ctx.author.mention}, An error occurred while unmuting {user.mention}: `{e}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @app_commands.command(name="mute", description="Mute a user for a specific duration (in minutes).")
    async def mute_slash(self, interaction: discord.Interaction, user: discord.Member, duration: int, reason: str = "No reason provided"):
        if user == interaction.user:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{interaction.user.mention}, You cannot mute yourself!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)

        try:
            duration_td = parse_duration(str(duration))  # Ensure `duration` is passed as a string like "10m", "1h", "1d"
            if duration_td is None:
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"{interaction.user.mention}, Invalid duration format! Use `Xm`, `Xh`, or `Xd` (e.g., `10m`, `2h`, `1d`).",
                    color=discord.Color.red()
                )
                return await interaction.response.send_message(embed=embed)

            await user.timeout(timedelta(minutes=duration_td), reason=reason)
            self.muted_users[user.id] = (datetime.utcnow() + timedelta(minutes=duration_td), interaction.channel.id, interaction.guild.id)

            embed = discord.Embed(
                title="🔇 User Muted",
                description=f"✅ **{user.mention} has been muted for `{duration}` minutes.**",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{interaction.user.mention}, I don't have permission to mute {user.mention}!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{interaction.user.mention}, An error occurred while muting {user.mention}: `{e}`",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="unmute", description="Unmute a user.")
    async def unmute_slash(self, interaction: discord.Interaction, user: discord.Member):
        if user == interaction.user:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{interaction.user.mention}, You cannot unmute yourself!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        try:
            await user.timeout(None, reason="Unmuted")

            embed = discord.Embed(
                title="🔊 User Unmuted",
                description=f"✅ **{user.mention} has been unmuted.**",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{interaction.user.mention}, I don't have permission to unmute {user.mention}!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"{interaction.user.mention}, An error occurred while unmuting {user.mention}: `{e}`",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Mute(bot))
