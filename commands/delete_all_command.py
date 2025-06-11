import discord
from discord import app_commands
from bot_instance import tree
from data_manager_db import delete_all_user_times


@tree.command(name="delete_all_tracks", description="Delete all your times across all tracks (Shrooms & No Items).")
async def delete_all_tracks_command(
    interaction: discord.Interaction
):
    uid = str(interaction.user.id)
    # Remove all entries for this user
    await delete_all_user_times(uid)

    desc = f"<@{uid}> deleted all their times across all tracks."
    title = "All Times Deleted"
    embed = discord.Embed(title=title, description=desc, color=discord.Color.red())
    await interaction.response.send_message(embed=embed, ephemeral=True)
