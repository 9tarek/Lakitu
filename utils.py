import re
from discord import File, Embed
from config import TRACKIMGS_DIR
from tracks import TRACK_PRIMARY, TRACK_REVERSE
import discord
from discord import app_commands

# Time format validator: M:SS.MMM
time_pattern = re.compile(r"^\d+:[0-5]\d\.\d{3}$")

EMBED_COLOR = 0x5d9c67

def parse_time_ms(time_str: str) -> int:
    minutes, rest = time_str.split(":")
    seconds, ms = rest.split(".")
    return int(minutes) * 60000 + int(seconds) * 1000 + int(ms)

def resolve_track(abbr_input: str) -> str | None:
    for abbr, full in TRACK_REVERSE.items():
        if abbr_input.lower() == abbr.lower():
            return full
    return None

def make_embed(title: str, description: str, track: str):
    """Return a (Embed, File|None) tuple with thumbnail if image exists."""
    embed = Embed(title=title, description=description, color=EMBED_COLOR)
    abbr = TRACK_PRIMARY.get(track)
    if abbr:
        img_path = TRACKIMGS_DIR / f"{abbr.lower()}.png"
        if img_path.exists():
            file = File(str(img_path), filename=f"{abbr.lower()}.png")
            embed.set_thumbnail(url=f"attachment://{abbr.lower()}.png")
            return embed, file
    return embed, None

async def track_autocomplete(interaction, current: str):
    from discord import app_commands
    return [
        app_commands.Choice(name=abbr, value=abbr)
        for abbr in TRACK_REVERSE
        if current.lower() in abbr.lower()
    ][:25]