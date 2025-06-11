import discord
from discord import app_commands
from bot_instance import tree
from tracks import TRACK_PRIMARY
from utils import EMBED_COLOR

@tree.command(
    name="track_abbreviations",
    description="List all tracks and their abbreviations."
)
async def track_abbreviations_command(
    interaction: discord.Interaction
):
    """
    Responds with an embed listing every track and its abbreviation.
    """
    # Build description: Full Name – Abbreviation
    lines = [f"**{full}** — `{abbr}`" for full, abbr in TRACK_PRIMARY.items()]
    description = "\n".join(lines)

    embed = discord.Embed(
        title="Track Abbreviations",
        description=description,
        color=EMBED_COLOR
    )

    await interaction.response.send_message(embed=embed)
