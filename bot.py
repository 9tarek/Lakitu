from bot_instance import client, tree
from config import TOKEN
from data_manager_db import init_db
import discord


import commands.save_command
import commands.display_command
import commands.delete_command
import commands.delete_all_command
import commands.track_abbreviations_command
import commands.tops_command

@client.event
async def on_ready():
    # Sync slash commands
    await init_db()
    await tree.sync()

    server_count = len(client.guilds)
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name=f"{server_count} servers"
    )
    await client.change_presence(activity=activity)
    
    print("Slash commands synced. Bot is ready!")

@client.event
async def on_guild_join(guild):
    # Update presence when joining a new guild
    server_count = len(client.guilds)
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name=f"{server_count} servers"
    )
    await client.change_presence(activity=activity)

@client.event
async def on_guild_remove(guild):
    # Update presence when removed from a guild
    server_count = len(client.guilds)
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name=f"{server_count} servers"
    )
    await client.change_presence(activity=activity)



if __name__ == "__main__":
    client.run(TOKEN)
