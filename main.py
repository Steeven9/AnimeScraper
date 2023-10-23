import json
from time import sleep
from typing import Tuple

import feedparser as fp
import requests
from pynimeapi import PyNime

# Read config
file_path = "config/config.json"
f = open(file_path, "r")
config = json.load(f)
f.close()

api = PyNime(base_url=config["gogoanime_api_url"])


def fetch_episodes(anime_title: str) -> Tuple[int, str]:
    """Returns the number of episodes and the latest
    episode link for a given anime title"""
    search_result = api.search_anime(anime_title=anime_title)
    episodes_urls = api.get_episode_urls(
        anime_category_url=search_result[0].category_url
    )
    # extract latest episode from URL
    num_episodes = int(episodes_urls[-1].split("-")[-1])

    return (num_episodes, episodes_urls[-1])


def fetch_chapters(manga) -> Tuple[int, int, str]:
    """Returns the number of chapters and the latest
    chapter link for a given manga title"""
    data = fp.parse(manga["url"])
    url = data["entries"][0]["link"]
    volume = url.split("/")[5][1:]
    chapter = url.split("/")[6][1:]
    return (int(volume), int(chapter), url)


if __name__ == "__main__":
    print("Starting AnimeScraper...")
    print("Watching following anime:", config["anime"])
    print("Watching following manga:", config["manga"])

    while True:
        new_content = []
        for anime in config["anime"]:
            current_episode, url = fetch_episodes(anime["name"])
            if current_episode > anime["latest_episode"]:
                anime["latest_episode"] = current_episode
                new_content.append(f"{anime['name']} ep {current_episode} - {url}")

        for manga in config["manga"]:
            current_volume, current_chapter, url = fetch_chapters(manga)
            if current_chapter > manga["latest_chapter"]:
                manga["latest_chapter"] = current_chapter
                new_content.append(
                    f"{manga['name']} vol {current_volume} ch {current_chapter} - {url}"
                )

        if len(new_content) > 0:
            links = "\n".join(new_content)
            notif_str = f"New episodes found! :partying_face: \n{links}"
            print(notif_str)

            data = {
                "content": notif_str,
            }
            requests.post(url=config["webhook_url"], data=data)

            f = open(file_path, "w")
            json.dump(config, fp=f, indent=2)
            f.close()

        # sleep for the given minutes
        sleep(60 * config["scrape_interval"])
