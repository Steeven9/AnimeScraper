import json
from time import sleep
from typing import Tuple

import requests
from pynimeapi import PyNime

# Read config
file_path = "config/config.json"
f = open(file_path, "r")
options = json.load(f)
f.close()

api = PyNime(base_url=options["apiUrl"])


def fetch_episodes(anime_title: str) -> Tuple[int, str]:
    '''Returns the number of episodes and the latest
      episode link for a given anime title'''
    search_result = api.search_anime(anime_title=anime_title)
    episodes_urls = api.get_episode_urls(
        anime_category_url=search_result[0].category_url)
    # extract latest episode from URL
    num_episodes = int(episodes_urls[-1].split("-")[-1])

    return (num_episodes, episodes_urls[-1])


if __name__ == "__main__":
    print("Starting AnimeScraper watching following anime:", options["anime"])

    while True:
        new_episodes = []
        for anime in options["anime"]:
            episodes, url = fetch_episodes(anime["name"])
            if episodes > anime["episodes"]:
                anime["episodes"] = episodes
                new_episodes.append(f"{anime['name']} ep {episodes} - {url}")

        if len(new_episodes) > 0:
            notif_str = f"New episodes found!\n{', '.join(new_episodes)}"
            print(notif_str)

            data = {
                "content": notif_str,
            }
            requests.post(url=options["webhookUrl"], data=data)

            f = open(file_path, "w")
            json.dump(options, fp=f, indent=2)
            f.close()

        # sleep for the given minutes
        sleep(60 * options["interval"])
