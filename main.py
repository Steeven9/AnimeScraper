import json
from datetime import datetime
from os import getenv
from traceback import print_exc
from typing import Tuple

import feedparser as fp
from discord import Activity, ActivityType, errors, utils
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
from pynimeapi import PyNime
from requests import get

# -- Options --
# Set this to True to register slash commands on boot
sync_commands = True
# Events fetch interval (in minutes)
scrape_interval = 60
# Discord bot token
discord_token = getenv("BOT_TOKEN")
# Debug channel to send errors to (private)
debug_channel_id = getenv("DEBUG_CHANNEL_ID")
# Heartbeat URL for uptime tracking
heartbeat_url = getenv("HEARTBEAT_URL")
# Channel to send notifications to
channel_id = getenv("CHANNEL_ID")
# Role to ping for events
role_id = getenv("ROLE_ID")
# API to fetch anime data from
gogoanime_api_url = getenv("API_URL")

# -- Read config --
file_path = "config/config.json"
f = open(file_path, "r")
config = json.load(f)
f.close()

api = PyNime(base_url=gogoanime_api_url)

# -- Initialize stuff --
if channel_id == None:
    raise ValueError("Channel ID not found!")
if discord_token == None:
    raise ValueError("Discord bot token not found!")
client = commands.Bot(".evt")
slash = SlashCommand(client, sync_commands)
channel = None
role_to_ping = None
debug_channel = None

# -- Event handling --


@client.event
async def on_ready() -> None:
    global channel, role_to_ping, debug_channel

    await client.change_presence(activity=Activity(type=ActivityType.watching,
                                                   name="events for you 🏳️‍🌈"))

    print("Starting AnimeScraper...")
    log(f"Logged in as {client.user}")
    print("Watching following anime:",
          {anime["name"]
           for anime in config["anime"]})
    print("Watching following manga:",
          {manga["name"]
           for manga in config["manga"]})

    channel = client.get_channel(int(channel_id))
    role_to_ping = utils.get(channel.guild.roles, id=role_id)
    debug_channel = client.get_channel(int(debug_channel_id))
    # Start cron
    if not check_events_loop.is_running():
        check_events_loop.start()


# Main loop that gets the events
@tasks.loop(minutes=scrape_interval)
async def check_events_loop() -> list:
    # Send heartbeat
    if (heartbeat_url is not None):
        get(heartbeat_url)

    new_content = []
    for anime in config["anime"]:
        current_episode, url = fetch_episodes(anime["name"])
        if current_episode > anime["latest_episode"]:
            anime["latest_episode"] = current_episode
            new_content.append(
                f"{' '.join(anime['followers'])} 🎬 {anime['name']} ep {current_episode} - [Watch]({url}) - [MAL]({anime['MAL_url']})"
            )

    for manga in config["manga"]:
        current_volume, current_chapter, url = fetch_chapters(manga)
        if current_chapter > manga["latest_chapter"]:
            manga["latest_chapter"] = current_chapter
            new_content.append(
                f"{' '.join(manga['followers'])} 📚 {manga['name']} vol {current_volume} ch {current_chapter} - [Read]({url}) - [MAL]({manga['MAL_url']})"
            )

    if len(new_content) > 0:
        links = "\n".join(new_content)
        notif_str = f"New stuff found! 🥳 \n{links}"
        print(notif_str)

        ping = f"{role_to_ping.mention} " if role_to_ping else ""
        try:
            await channel.send(ping + notif_str)
        except errors.HTTPException:
            print_exc()
            log("Events skipped due to length")
            await debug_channel.send(
                "Too many characters to send in one message, skipping events")

        # Save new episodes to config
        f = open(file_path, "w")
        json.dump(config, fp=f, indent=2)
        f.close()


# -- Slash commands --


@slash.slash(name="ping", description="Show server latency")
async def ping(ctx: SlashContext) -> None:
    log(f"Command `ping` called from server {ctx.guild_id} by {ctx.author}")
    await ctx.send(f"Pong! ({round(client.latency*1000, 2)}ms)")


@slash.slash(name="list", description="List watched shows and mangas")
async def list(ctx: SlashContext) -> None:
    log(f"Command `list` called from server {ctx.guild_id} by {ctx.author}")
    msg = f"Watching following anime: {', '.join(anime['name'] for anime in config['anime'])}\n"
    msg += f"and following manga: {', '.join(manga['name'] for manga in config['manga'])}"
    await ctx.send(msg)


@slash.slash(name="next", description="Show next event")
async def next(ctx: SlashContext) -> None:
    log(f"Command `next` called from server {ctx.guild_id} by {ctx.author}")
    await ctx.send("Not implemented yet")


# -- Helper functions --


def fetch_episodes(anime_title: str) -> Tuple[int, str]:
    """Returns the number of episodes and the latest
    episode link for a given anime title"""
    search_result = api.search_anime(anime_title=anime_title)
    episodes_urls = api.get_episode_urls(
        anime_category_url=search_result[0].category_url)
    # extract latest episode from URL
    num_episodes = int(episodes_urls[-1].split("-")[-1])

    return (num_episodes, episodes_urls[-1])


def fetch_chapters(manga) -> Tuple[int, float, str]:
    """Returns the number of chapters and the latest
    chapter link for a given manga title"""
    data = fp.parse(manga["url"])
    try:
        url = data["entries"][0]["link"]
        volume = url.split("/")[5][1:]
        chapter = url.split("/")[6][1:]
    except IndexError:
        raise ValueError(f"Invalid URL for {manga['name']}")
    return (int(volume), float(chapter), url)


def fetch_events():
    return [0, []]


# Helper to log messages in stdout
def log(msg: str) -> None:
    print(f"{str(datetime.now())[:-7]} {msg}")


client.run(discord_token)
