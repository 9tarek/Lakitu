import discord
from discord import app_commands
from bot_instance import tree
from utils import resolve_track, make_embed, track_autocomplete, EMBED_COLOR
from data_manager_db import get_times
from tracks import TRACK_PRIMARY

ITEM_CHOICES = [
    app_commands.Choice(name="Shrooms", value="Shrooms"),
    app_commands.Choice(name="No Items", value="No Items")
]

@tree.command(name="display", description="Show saved times filtered by track and player/role.")
@app_commands.describe(
    items="Shrooms or No Items",
    track="(Optional) Track abbreviation (check /track_abbreviations)",
    player="(Optional) A user or role to filter by (mentionable)"
)
@app_commands.autocomplete(track=track_autocomplete)
@app_commands.choices(items=ITEM_CHOICES)
async def display_command(
    interaction: discord.Interaction,
    items: str,
    track: str = None,
    player: discord.Member | discord.Role = None
):
    """
    If track is provided: show times for that track and mode.  
    If only items: for each track with entries, show best time with rank 1/total.  
    If items + player: for each track the player/role has entries, show their best time with rank 1/total for that track.
    """
    guild = interaction.guild
    # Build list of member IDs based on player (Member or Role)
    player_ids: list[str] | None = None
    if player:
        if isinstance(player, discord.Role):
            player_ids = [str(m.id) for m in player.members]
        else:
            player_ids = [str(player.id)]

    def matches_player(uid: str) -> bool:
        return not player_ids or uid in player_ids

    lines: list[str] = []
    # Single-track mode
    if track:
        full = resolve_track(track)
        if not full:
            return await interaction.response.send_message(
                embed=discord.Embed(description="Invalid track.", color=discord.Color.red()),
                ephemeral=True
            )
        rows = await get_times(full, items)
        rows = [(u, t) for u, t in rows if interaction.guild.get_member(int(u))]
        rows = [rt for rt in rows if matches_player(rt[0])]
        if not rows:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    description="No matching times found.",
                    color=discord.Color.red()
                ), ephemeral=True
            )
        total = len(rows)
        if player_ids:
            # show only the player's best
            u, t = rows[0]
            if total > 1:
                lines.append(f"**{full}** — <@{u}>: `{t}` (1/{total})")
            else:
                lines.append(f"**{full}** — <@{u}>: `{t}`")
        else:
            for i, (u, t) in enumerate(rows):
                lines.append(f"{i+1}. <@{u}>: `{t}`")
        description = "\n".join(lines)
        title = f"{full} `{items}`"
        emb, file = make_embed(title, description, full)
        return await interaction.response.send_message(embed=emb, file=file) if file else await interaction.response.send_message(embed=emb)

    # Multi-track mode
    for full, _abbr in TRACK_PRIMARY.items():
        rows = await get_times(full, items)
        rows = [(u, t) for u, t in rows if interaction.guild.get_member(int(u))]
        rows = [rt for rt in rows if matches_player(rt[0])]
        if not rows:
            continue
        u, t = rows[0]
        total = len(rows)
        if total > 1:
            lines.append(f"**{full}** — <@{u}>: `{t}` (1/{total})")
        else:
            lines.append(f"**{full}** — <@{u}>: `{t}`")
    if not lines:
        return await interaction.response.send_message(
            embed=discord.Embed(
                description="No times found.",
                color=discord.Color.red()
            ), ephemeral=True
        )
    description = "\n".join(lines)
    title = f"Leaderboard `{items}`"
    emb = discord.Embed(title=title, description=description, color=EMBED_COLOR)
    await interaction.response.send_message(embed=emb)