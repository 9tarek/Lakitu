import discord
from discord import app_commands
from bot_instance import tree
from utils import resolve_track, track_autocomplete, make_embed
from data_manager_db import get_times

ITEM_CHOICES = [
    app_commands.Choice(name="Shrooms", value="Shrooms"),
    app_commands.Choice(name="No Items", value="No Items")
]

@tree.command(name="tops", description="Show the top 5 times for a track across all servers. (These are not WW Tops -> Top 5 Bot Entries)")
@app_commands.describe(
    track="Track abbreviation (check /track_abbreviations)",
    items="Shrooms or No Items"
)
@app_commands.autocomplete(track=track_autocomplete)
@app_commands.choices(items=ITEM_CHOICES)
async def tops_command(
    interaction: discord.Interaction,
    items: str,
    track: str
    
):
    """
    Lists the top 5 best times globally for the specified track and mode.
    """
    full = resolve_track(track)
    if not full:
        return await interaction.response.send_message(
            embed=discord.Embed(description="Invalid track.", color=discord.Color.red()),
            ephemeral=True
        )

    # Fetch all times for track and mode
    rows = await get_times(full, items)
    total_entries = len(rows)
    if not rows:
        return await interaction.response.send_message(
            embed=discord.Embed(
                description=f"No times found for {full} in {items} mode.",
                color=discord.Color.red()
            ),
            ephemeral=True
        )

    # Take top 5
    top5 = rows[:5]
    lines = []
    for i, (uid, t) in enumerate(top5, start=1):
        # try cache first, then API
        user = interaction.client.get_user(uid)
        if user is None:
            try:
                user = await interaction.client.fetch_user(uid)
            except (discord.NotFound, discord.HTTPException):
                user = None

        display = str(user) if user else f"<@{uid}>"
        lines.append(f"{i}. {display}: `{t}`")

    description = "\n".join(lines)
    title = f"Top 5     `{items}` \n{full}"
    emb, file = make_embed(title, description, full)
    emb.set_footer(text=f"Total entries: {total_entries}")
    # send normally
    if file:
        await interaction.response.send_message(embed=emb, file=file)
    else:
        await interaction.response.send_message(embed=emb)