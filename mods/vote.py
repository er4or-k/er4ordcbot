import discord
from discord.ext import commands
from discord import app_commands

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Prefix command !!vote
    @commands.command(name='vote')
    async def vote_prefix(self, ctx):
        """Sends a voting link for the bot using prefix"""
        vote_link = "https://top.gg/bot/952422233563873342?s=06c879c0f3e24"
        embed = discord.Embed(
            title="Vote for Er4orBot!",
            description=f"Thank you for supporting Er4orBot! If you enjoy using the bot, please consider voting for it on Top.gg! \n\n[Vote here]({vote_link})",
            color=discord.Color.green()
        )
        embed.set_footer(text="Voting helps keep the bot active and visible.")
        await ctx.send(embed=embed)

    # Slash command /vote
    @app_commands.command(name='vote', description='Vote for Er4orBot on Top.gg')
    async def vote_slash(self, interaction: discord.Interaction):
        """Sends a voting link for the bot using slash command"""
        vote_link = "https://top.gg/bot/952422233563873342?s=06c879c0f3e24"
        embed = discord.Embed(
            title="Vote for Er4orBot!",
            description=f"Thank you for supporting Er4orBot! If you enjoy using the bot, please consider voting for it on Top.gg! \n\n[Vote here]({vote_link})",
            color=discord.Color.green()
        )
        embed.set_footer(text="Voting helps keep the bot active and visible.")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Vote(bot))
