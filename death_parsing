__author__ = 'Eddie'

import requests
from PIL import Image, ImageDraw, ImageFont
from math import ceil, floor
from visvis.vvmovie import images2swf
import ast

# Riot API Key
key = "SECRET_KEY"

size = 2
map_size, scale, r = int(512 / size), 30 * size, 8
mini_map = Image.open("minimap-mh.png").resize((map_size, map_size)).convert("RGBA")


def main_parse(epoch, interval=5000):
    """
    :param epoch: must be a multiple of 5 minutes
    :param interval: the sampling duration. 5000 is 5 seconds.
    :return: None
    """
    images = []
    url = "https://na.api.pvp.net/api/lol/na/v4.1/game/ids?beginDate={0}&api_key={1}".format(epoch, key)
    response = requests.get(url)
    games = ast.literal_eval(response.text)
    for x in games:
        images = death_parsing(images, x, interval)

    death_swf([Image.alpha_composite(mini_map, image) for image in images])


def death_parsing(images, match, interval):
    """
    :param match: Match ID.
    :param interval: The sampling duration.
    :return: List of images.
    """
    match_url = "https://na.api.pvp.net/api/lol/na/v2.2/match/{0}?includeTimeline=true&api_key={1}".format(
        match, key)
    match_response = requests.get(match_url)
    if match_response.status_code == 200:
        print("Parsing match.")
        frames = match_response.json()["timeline"]["frames"]

        for i in range(len(frames)):
            if frames[i]["timestamp"] != 0:
                for event in frames[i]["events"]:
                    if event["eventType"] == "CHAMPION_KILL":
                        y, x = event["position"]["y"], event["position"]["x"]
                        victim = event["victimId"]
                        time = event["timestamp"]
                        images = draw_deaths(images, x, y, victim, time, interval)
    else:
        pass

    return images


def set_images(images, time, interval):
    """
    :param time: Timestamp value.
    :param images:
    :param interval:
    :return:
    """
    if time / interval >= len(images):
        extras = ceil(time / interval) - len(images) + 1
        for x in range(extras):
            images.append(Image.new('RGBA', (map_size, map_size)))
        return images
    else:
        return images


def draw_deaths(images, x, y, victim, time, interval):
    font = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", 12)
    images = set_images(images, time, interval)
    x_off, y_off = 570, 420
    for f in range(len(images)):
        if time <= f * interval <= time + 2 * interval:
            im = Image.new('RGBA', (map_size, map_size))
            draw = ImageDraw.Draw(im, "RGBA")
            if victim <= 5:
                color = (0, 0, 255, 155)
            else:
                color = (255, 0, 0, 155)

            x += x_off
            y += y_off

            draw.ellipse((x / scale - r,
                          map_size - y / scale - r,
                          x / scale + r,
                          map_size - y / scale + r),
                         fill=color)

            minutes = floor(f * interval / 60000)
            seconds = (f * interval / 1000) % 60
            draw.text((0, map_size - 24),
                      "{0}{1}:{2}{3}".format(floor(minutes / 10),
                                             round(minutes % 10),
                                             floor(seconds / 10),
                                             round(seconds % 10)),
                      font=font)
            del draw

            print("Plotted at {}".format(f))

            images[f] = Image.alpha_composite(images[f], im)

        else:
            im = Image.new('RGBA', (map_size, map_size))
            draw = ImageDraw.Draw(im, "RGBA")
            minutes = floor(f * interval / 60000)
            seconds = (f * interval / 1000) % 60
            draw.text((0, map_size - 24),
                      "{0}{1}:{2}{3}".format(floor(minutes / 10),
                                             round(minutes % 10),
                                             floor(seconds / 10),
                                             round(seconds % 10)),
                      font=font)
            del draw

            images[f] = Image.alpha_composite(images[f], im)

    return images


def death_swf(images):
    """Returns a gif from images input."""
    print("Creating SWF with {} images.".format(len(images)))
    file_name = "death_swf.swf"
    images2swf.writeSwf(file_name, images, duration=0.2)
    print("SWF complete.")

main_parse(1428782400, 5000)
