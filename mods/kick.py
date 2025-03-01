import discord
from discord.ext import commands
from discord import app_commands

class Kick(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Prefix Command: !!kick
    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason="No reason provided"):
        if member is None:
            embed = discord.Embed(
                title="Kick Failed ❌",
                description=f"{ctx.author.mention},Please mention a user to kick!",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                title="Permission Denied ❌",
                description=f"{ctx.author.mention},You can't kick {member.mention} because they have equal or higher permissions!",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        await member.kick(reason=reason)
        embed = discord.Embed(
            title="Member Kicked ✅",
            description=f"{member.mention} has been kicked!",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Kicked by", value=ctx.author.mention, inline=False)
        await ctx.send(embed=embed)

    @kick.error
    async def kick_error(self, ctx, error):
        embed = discord.Embed(title="Kick Failed ❌", color=discord.Color.orange())
        if isinstance(error, commands.MissingPermissions):
            embed.description = f"{ctx.author.mention},You don't have permission to use this command!"
        elif isinstance(error, commands.BotMissingPermissions):
            embed.description = "I don't have permission to kick members!"
        elif isinstance(error, commands.BadArgument):
            embed.description = f"{ctx.author.mention},Invalid user! Please mention a valid member."
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = f"{ctx.author.mention},Please mention a user to kick!"
        await ctx.send(embed=embed)

    # Slash Command: /kick
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_user(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            embed = discord.Embed(
                title="Permission Denied ❌",
                description=f"{interaction.user.mention},You can't kick {member.mention} because they have equal or higher permissions!",
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed)

        await member.kick(reason=reason)

        embed = discord.Embed(
            title="✅ Member Kicked",
            description=f"{member.mention} has been kicked!",
            color=discord.Color.red()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Kicked by", value=interaction.user.mention, inline=False)

        await interaction.response.send_message(embed=embed)

    @kick_user.error
    async def kick_slash_error(self, interaction: discord.Interaction, error):
        embed = discord.Embed(title="Kick Failed ❌", color=discord.Color.orange())
        if isinstance(error, app_commands.MissingPermissions):
            embed.description = f"{interaction.user.mention},You don't have permission to use this command!"
        elif isinstance(error, app_commands.BotMissingPermissions):
            embed.description = "I don't have permission to kick members!"
        elif isinstance(error, app_commands.CommandInvokeError):
            embed.description = f"Invaild User!!, {interaction.user.mention},Please mention a valid member."
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Kick(bot))
