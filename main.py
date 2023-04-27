import json
from time import sleep

import requests
from pynimeapi import PyNime

api = PyNime(base_url="https://gogoanime.llc")
file_path = "config/config.json"


def fetch_episodes(anime_title: str) -> int:
    '''Returns the number of episodes for a given anime title'''
    search_result = api.search_anime(anime_title=anime_title)
    episodes_urls = api.get_episode_urls(
        anime_category_url=search_result[0].category_url)
    num_episodes = len(episodes_urls)

    return num_episodes


if __name__ == "__main__":
    #TODO add error handling
    f = open(file_path, "r")
    options = json.load(f)
    f.close()
    print("Starting AnimeScraper watching following anime:", options["anime"])

    while True:
        new_episodes = []
        for anime in options["anime"]:
            episodes = fetch_episodes(anime["name"])
            if episodes > anime["episodes"]:
                anime["episodes"] = episodes
                new_episodes.append(anime["name"])

        if len(new_episodes) > 0:
            notif_str = f"{len(new_episodes)} new episodes found for {', '.join(new_episodes)}"
            print(notif_str)

            data = {
                "username": "AnimeScraper",
                "content": notif_str,
            }
            requests.post(url=options["webhookUrl"], data=data)

            f = open(file_path, "w")
            json.dump(options, fp=f, indent=2)
            f.close()

        # sleep for the given minutes
        sleep(60 * options["interval"])
