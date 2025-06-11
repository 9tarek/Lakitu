import discord
from discord import app_commands
from bot_instance import tree
from utils import resolve_track, time_pattern, parse_time_ms, make_embed, track_autocomplete
from data_manager_db import get_times, save_time

ITEM_CHOICES = [
    app_commands.Choice(name="Shrooms", value="Shrooms"),
    app_commands.Choice(name="No Items", value="No Items")
]

@tree.command(name="save", description="Save your time for a track")
@app_commands.describe(
    track="Track abbreviation (check /track_abbreviations)",
    items="Shrooms or No Items",
    time="Time in M:SS.MMM format (e.g. 1:54.323)"
)
@app_commands.autocomplete(track=track_autocomplete)
@app_commands.choices(items=ITEM_CHOICES)
async def save_command(
    interaction: discord.Interaction,
    items: str,
    track: str,
    time: str
):
    full = resolve_track(track)
    if not full:
        return await interaction.response.send_message(
            embed=discord.Embed(description="Invalid track.", color=discord.Color.red()),
            ephemeral=True
        )
    if not time_pattern.match(time):
        return await interaction.response.send_message(
            embed=discord.Embed(description="Time must be in M:SS.MMM format.", color=discord.Color.red()),
            ephemeral=True
        )

    uid = str(interaction.user.id)
    # get previous times and find old for this user
    rows = await get_times(full, items)
    old_time = next((t for u, t in rows if u == uid), None)

    # save new time
    await save_time(full, items, uid, time)

    # build description with improvement if applicable
    if old_time and parse_time_ms(time) < parse_time_ms(old_time):
        diff_ms = parse_time_ms(old_time) - parse_time_ms(time)
        minutes = diff_ms // 60000
        seconds = (diff_ms % 60000) // 1000
        ms = diff_ms % 1000
        diff_str = f"{minutes}:{seconds:02d}.{ms:03d}"
        desc = f"<@{uid}> saved `{time}` (improved by `{diff_str}`)"
    else:
        desc = f"<@{uid}> saved `{time}`"

    title = f"{full} `{items}`"
    emb, file = make_embed(title, desc, full)
    if file:
        await interaction.response.send_message(embed=emb, file=file)
    else:
        await interaction.response.send_message(embed=emb)
