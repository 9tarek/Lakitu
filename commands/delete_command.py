import discord
from discord import app_commands
from bot_instance import tree
from utils import resolve_track, make_embed, track_autocomplete
from data_manager_db import get_times, delete_time

ITEM_CHOICES = [
    app_commands.Choice(name="Shrooms", value="Shrooms"),
    app_commands.Choice(name="No Items", value="No Items")
]

@tree.command(name="delete", description="Delete your time for a track.")
@app_commands.describe(
    track="Track abbreviation (check /track_abbreviations)",
    items="Shrooms or No Items"
)
@app_commands.autocomplete(track=track_autocomplete)
@app_commands.choices(items=ITEM_CHOICES)
async def delete_command(
    interaction: discord.Interaction,
    items: str,
    track: str
    
):
    full = resolve_track(track)
    if not full:
        return await interaction.response.send_message(
            embed=discord.Embed(description="Invalid track.", color=discord.Color.red()),
            ephemeral=True
        )

    uid = str(interaction.user.id)
    # Check if user has a previous time for this track/items
    rows = await get_times(full, items)
    if not any(u == uid for u, _ in rows):
        return await interaction.response.send_message(
            embed=discord.Embed(
                description=f"No {items}-time for {full} found.",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

    # Delete the specific time entry
    await delete_time(full, items, uid)

    desc = f"<@{uid}> deleted their {items}-time for {full}."
    title = "Time Deleted"
    emb, file = make_embed(title, desc, full)
    await interaction.response.send_message(embed=emb, file=file, ephemeral=True)