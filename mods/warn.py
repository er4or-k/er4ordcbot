import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from pymongo import MongoClient
import asyncio
import datetime

MONGO_URI = "mongodb+srv://kiranpoo7ary:FPcsopE32NSR1zfP@cluster0.leb3q.mongodb.net/afk_db?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true"
client = MongoClient(MONGO_URI)
db = client["warn_db"]
warnings = db["warnings"]
settings = db["settings"]

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    def warn_data(self, guild, user, moderator, reason):
        return {
            "guild_id": guild.id,
            "user_id": user.id,
            "reason": reason,
            "moderator": moderator.id,
            "timestamp": datetime.datetime.now(),
            
        }
    #!!warn   
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def warn(self, ctx, member:discord.Member = None, *,reason="No Reason Provided"):
        if member is None:
            embed = discord.Embed(
                title="Warn Failed ❌",
                description=f"{ctx.author.mention},Please mention a user to warn!",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        if member == ctx.author:
            embed = discord.Embed(
                title="Warn Failed❌",
                description=f"{ctx.author.mention} You Can't Warn You're Self",
                colour=discord.Color.orange()
            )
            return await ctx.send(embed=embed)
        
        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                title="Permission Denied ❌",
                description=f"{ctx.author.mention},You can't warn {member.mention} because they have equal or higher permissions!",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)      
        
        warndata = self.warn_data(ctx.guild, member, ctx.author, reason)
        warnings.insert_one(warndata)

        embed = discord.Embed(
            title="User Warned⚠️",
            description=f"{member.mention} has been warned!. \n **Reason:**{reason}",
            colour= discord.Colour.orange()
        )
        embed.set_footer(text=f"Warned By {ctx.author}")
        await ctx.send(embed=embed)
    @warn.error
    async def warn_error(self, ctx, error):
        embed = discord.Embed(title="Warn Failed ❌", color=discord.Color.orange())
        if isinstance(error, commands.MissingPermissions):
            embed.description = f"{ctx.author.mention},You don't have permission to use this command!"
        elif isinstance(error, commands.BotMissingPermissions):
            embed.description = "I don't have permission to ban members!"
        elif isinstance(error, commands.BadArgument):
            embed.description = f"{ctx.author.mention},Invalid user! Please mention a valid member."
    #/warn
    @app_commands.command(name="warn", description="Warn A User")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn_slash(self, interaction: discord.Interaction, member:discord.Member, reason: str="No Reason Provided"):
        if member.top_role >= interaction.user.top_role:
            embed = discord.Embed(
                title="Permission Denied ❌",
                description=f"{interaction.user.mention},You can't warn {member.mention} because they have equal or higher permissions!",
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed)

        await member.ban(reason=reason)

        if member == interaction.user:
            embed = discord.Embed(
                title="Warn Failed ❌",
                description=f"{interaction.user.mention} You Can't Warn You're Self",
                colour= discord.Colour.orange()
            )
            await interaction.response.send_message(embed=embed)

        warndata = self.warn_data(interaction.guild, member, interaction.user, reason)
        warnings.insert_one(warndata)

        embed = discord.Embed(
             title="User Warned⚠️",
             description=f"{member.mention} has been warned!. \n **Reason:**{reason}",
             colour= discord.Colour.orange()
        )
        embed.set_footer(text=f"Warned By {interaction.user}")
        await interaction.response.send_message(embed=embed)
    
    @warn_slash.error
    async def warn_slash_error(self, interaction: discord.Interaction, error):
        embed = discord.Embed(title="Ban Failed ❌", color=discord.Color.orange())
        if isinstance(error, app_commands.MissingPermissions):
            embed.description = f"{interaction.user.mention},You don't have permission to use this command!"
        elif isinstance(error, app_commands.BotMissingPermissions):
            embed.description = "I don't have permission to ban members!"
        elif isinstance(error, app_commands.CommandInvokeError):
            embed.description = f"Invalid User! {interaction.user.mention},Please mention a valid member."
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Warn(bot))