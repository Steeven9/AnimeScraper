# AnimeScraper

![](https://img.shields.io/github/license/steeven9/AnimeScraper)
![](https://img.shields.io/docker/cloud/automated/steeven9/AnimeScraper)
![](https://img.shields.io/docker/cloud/build/steeven9/AnimeScraper)
![](https://img.shields.io/tokei/lines/github/steeven9/AnimeScraper)

Sends a webhook notification when a new anime episode releases.

## How to run it

First install the dependencies:

```bash
pip install deps/*.whl
pip install -r requirements.txt
```

Copy `config_sample.json` to `config.json`, adjust the options in there, and then run the script:

```bash
python main.py
```

## Docker

There is a Docker image available. To use it, simply run:

```bash
docker run -v ./config:/usr/src/app/config steeven9/animescraper
```
