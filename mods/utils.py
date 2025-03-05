import discord

from database.models import warnings, warn_config  # ✅ Import Both Models

async def send_warn_log(bot, guild, member, moderator, reason, guild_settings):
    collection = guild.db["warn_settings"]
    settings = await collection.find_one({"guild_id": guild.id})

    if not settings or "log_channel" not in settings:
        return  # If no log channel is set, do nothing

    log_channel_id = settings["log_channel"]
    log_channel = discord.utils.get(bot.get_all_channels(), id=guild_settings["log_channel"])


    if log_channel is None:
        return  # If channel is deleted, do nothing

    embed = discord.Embed(
        title="⚠️ Warning Issued",
        color=discord.Color.orange()
    )
    embed.add_field(name="Member", value=f"{member.mention} (`{member.id}`)", inline=False)
    embed.add_field(name="Moderator", value=f"{moderator.mention} (`{moderator.id}`)", inline=False)
    embed.add_field(name="Reason", value=reason, inline=False)

    await log_channel.send(embed=embed)
