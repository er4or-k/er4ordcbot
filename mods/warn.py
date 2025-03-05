import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from pymongo import MongoClient
import asyncio
import datetime
from mods.utils import send_warn_log  # ✅ Keep this
from database.models import warnings, warn_config  # ✅ Import Both Models

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    #warn data
    def warn_data(self, guild, user, moderator, reason):
        return {
            "guild_id": guild.id,
            "user_id": user.id,
            "reason": reason,
            "moderator": moderator.id,
            "timestamp": datetime.datetime.now(),
        }
    #guild settings
    async def guild_settings(self, guild_id):
        existing = await warn_config.find_one({"guild_id":guild_id})
        if not existing :
            await warn_config.insert_one({
                "guild_id": guild_id,
                "log_channel": None,
                "warn_limit": 3,
                "mute_time": 600,
                "auto_mute": True
            })
            await self.guild_settings(guild_id)


    #!!warn   
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason="No Reason Provided"):

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
        
        await self.guild_settings(ctx.guild.id)
        guild_settings = await warn_config.find_one({"guild_id": ctx.guild.id})
        if not guild_settings:
            guild_settings = {"log_channel": None}

        if not guild_settings["log_channel"]:  # Step 3: Warn Log Channel Suggestion
            embed = discord.Embed(
                title="⚙️ Warn System Logs Setup",
                description="It seems **Warn Log Channel** is not set up.\nWould you like to create one automatically?",
                color=discord.Color.blue()
            )
            view = self.LogChannelView(ctx.guild)
            await ctx.send(embed=embed, view=view)
            return
   
        
        warndata = self.warn_data(ctx.guild, member, ctx.author, reason)
        await warnings.insert_one(warndata)

        await send_warn_log(self.bot, ctx.guild, member, ctx.author, reason, guild_settings)  # Add Here 🔥✅

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
        await ctx.send(embed=embed)

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



        if member == interaction.user:
           await interaction.response.defer(thinking=True)
           embed = discord.Embed(
               title="Warn Failed ❌",
               description=f"{interaction.user.mention} You Can't Warn Yourself",
               colour=discord.Colour.orange()
           )
           await interaction.followup.send(embed=embed, ephemeral=True)
           return
        await self.guild_settings(interaction.guild.id)
        guild_settings = await warn_config.find_one({"guild_id": interaction.guild.id})
        if not guild_settings:
            guild_settings = {"log_channel": None}


        if not guild_settings["log_channel"]:  # Step 3 Here ✅
            embed = discord.Embed(
                title="⚙️ Warn System Logs Setup",
                description="It seems **Warn Log Channel** is not set up.\nWould you like to create one automatically?",
                color=discord.Color.blue()
            )

            view = self.LogChannelView(interaction.guild)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            return

        warndata = self.warn_data(interaction.guild, member, interaction.user, reason)
        await warnings.insert_one(warndata)

        await send_warn_log(self.bot, interaction.guild, member, interaction.user, reason, guild_settings)

        embed = discord.Embed(
             title="User Warned⚠️",
             description=f"{member.mention} has been warned!. \n **Reason:**{reason}",
             colour= discord.Colour.orange()
        )
        embed.set_footer(text=f"Warned By {interaction.user}")
        await interaction.response.send_message(embed=embed)
    
    @warn_slash.error
    async def warn_slash_error(self, interaction: discord.Interaction, error):
        embed = discord.Embed(title="Warn Failed ❌", color=discord.Color.orange())
        if isinstance(error, app_commands.MissingPermissions):
            embed.description = f"{interaction.user.mention},You don't have permission to use this command!"
        elif isinstance(error, app_commands.CommandInvokeError):
            embed.description = f"Invalid User! {interaction.user.mention},Please mention a valid member."
        await interaction.response.send_message(embed=embed)
    class LogChannelView(View):
        def __init__(self, guild):
            super().__init__(timeout=60)
            self.guild = guild
        
        @discord.ui.button(label="✅ Create Channel", style=discord.ButtonStyle.green)
        async def create_channel(self, interaction: discord.Interaction, button: Button):
            if not interaction.user.guild_permissions.administrator:
               return await interaction.response.send_message("You don't have permission!")
            channel = await self.guild.create_text_channel("warn_logs")
            await warn_config.update_one({"guild_id":self.guild.id}, {"$set": {"log_channel": channel.id}})
            embed = discord.Embed(
                title= "Warns Log Channel Created ✅",
                description= f"Channel= {channel.mention}",
                colour= discord.Colour.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()
            
        @discord.ui.button(label="❌ Cancel ", style=discord.ButtonStyle.green)
        async def cancel(self, interaction: discord.Interaction, button: Button):
            embed= discord.Embed(
                title="Warn Logs Setup Cancelled❌",
                colour= discord.Colour.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            self.stop()



async def setup(bot):
    await bot.add_cog(Warn(bot))