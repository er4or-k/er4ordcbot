import discord
from discord.ext import commands
from discord import app_commands

class Ban(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Prefix Command: !!ban
    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason="No reason provided"):
        if member is None:
            embed = discord.Embed(
                title="Ban Failed ❌",
                description=f"{ctx.author.mention},Please mention a user to ban!",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                title="Permission Denied ❌",
                description=f"{ctx.author.mention},You can't ban {member.mention} because they have equal or higher permissions!",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        await member.ban(reason=reason)
        embed = discord.Embed(
            title="Member Banned ✅",
            description=f"{member.mention} has been banned!",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Banned by", value=ctx.author.mention, inline=False)
        await ctx.send(embed=embed)

    @ban.error
    async def ban_error(self, ctx, error):
        embed = discord.Embed(title="Ban Failed ❌", color=discord.Color.orange())
        if isinstance(error, commands.MissingPermissions):
            embed.description = f"{ctx.author.mention},You don't have permission to use this command!"
        elif isinstance(error, commands.BotMissingPermissions):
            embed.description = "I don't have permission to ban members!"
        elif isinstance(error, commands.BadArgument):
            embed.description = f"{ctx.author.mention},Invalid user! Please mention a valid member."
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = f"{ctx.author.mention},Please mention a user to ban!"
        await ctx.send(embed=embed)

    # Slash Command: /ban
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_user(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            embed = discord.Embed(
                title="Permission Denied ❌",
                description=f"{interaction.user.mention},You can't ban {member.mention} because they have equal or higher permissions!",
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed)

        await member.ban(reason=reason)

        embed = discord.Embed(
            title="✅ Member Banned",
            description=f"{member.mention} has been banned!",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Banned by", value=interaction.user.mention, inline=False)

        await interaction.response.send_message(embed=embed)

    @ban_user.error
    async def ban_slash_error(self, interaction: discord.Interaction, error):
        embed = discord.Embed(title="Ban Failed ❌", color=discord.Color.orange())
        if isinstance(error, app_commands.MissingPermissions):
            embed.description = f"{interaction.user.mention},You don't have permission to use this command!"
        elif isinstance(error, app_commands.BotMissingPermissions):
            embed.description = "I don't have permission to ban members!"
        elif isinstance(error, app_commands.CommandInvokeError):
            embed.description = f"Invalid User! {interaction.user.mention},Please mention a valid member."
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Ban(bot))
