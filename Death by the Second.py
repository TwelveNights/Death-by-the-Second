__author__ = 'JackelPPA'

import ast
import requests
import time
from math import ceil
from PIL import Image, ImageDraw, ImageFont
from visvis.vvmovie import images2swf


# Riot API Key
key = open("key").read()

# Constants
size = 1
dot_opacity = 100
map_size, scale = int(512 / size), 30 * size
r = 4
frame_delay = .2
mini_map = Image.open("minimap-mh.png").resize((map_size, map_size)).convert("RGBA")


def main_parse(epoch, matches, interval=60000):
    """
    :param epoch: Must be a multiple of 5 minutes
    :param matches: Number of matches used, beginning with the epoch match.
    :param interval: The sampling duration. 60000 is 60 seconds.
    :return: None
    """
    images = []
    games = []
    for m in range(matches):
        print("Adding bucket {}.".format(m+1))
        url = "https://na.api.pvp.net/api/lol/na/v4.1/game/ids?beginDate={0}&api_key={1}".format(epoch + m * 300, key)
        request = requests.get(url)
        games += ast.literal_eval(request.text)

    for g in games:
        images = death_parsing(images, g, interval)

    add_timestamp(images, interval)

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
            if 'events' in frames[i]:
                    for event in frames[i]["events"]:
                        if event["eventType"] == "CHAMPION_KILL":
                            y, x = event["position"]["y"], event["position"]["x"]
                            victim = event["victimId"]
                            timestamp = event["timestamp"]
                            images = draw_deaths(images, (x, y), victim, timestamp, interval)

    else:
        print("Match code is {}, and unable to parse.".format(match_response.status_code))

    return images


def draw_deaths(images, coord, victim, timestamp, interval):
    """
    :param images: The set of images to draw on.
    :param coord = Tuple containing x, y coordinates
    :param victim: The individual killed.
    :param timestamp: Timestamp.
    :param interval: The sampling duration.
    :return: Returns a set of images, with the image mapped.
    """

    # Checks for if the index of frames fits with the timestamp of the death
    images = set_images(images, timestamp, interval)
    x, y = coord

    # Offset correction
    x += 570
    y += 420

    for i, image in enumerate(images):
        if timestamp <= i * interval <= timestamp + 2 * interval:
            im = Image.new('RGBA', (map_size, map_size))
            draw = ImageDraw.Draw(im, "RGBA")
            if victim <= 5:
                color = (0, 0, 255, dot_opacity)
                print("Plotted at {}.".format(i))
            else:
                color = (255, 0, 0, dot_opacity)

            draw.ellipse((x / scale - r,
                          map_size - y / scale - r,
                          x / scale + r,
                          map_size - y / scale + r),
                         fill=color)

            del draw

            images[i] = Image.alpha_composite(image, im)

    return images


def add_timestamp(images, interval):
    font = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", 12)
    for i, image in enumerate(images):
        draw = ImageDraw.Draw(image, "RGBA")
        minutes = i * interval // 60000
        seconds = i * interval // 1000 % 60
        draw.text((0, map_size - 24),
                  "{0}{1}:{2}{3}".format(minutes // 10,
                                         minutes % 10,
                                         seconds // 10,
                                         seconds % 10),
                  font=font)
        del draw


def set_images(images, timestamp, interval):
    """
    :param images: The list of images being mapped.
    :param timestamp: Timestamp value.
    :param interval: The sampling duration.
    :return: The images parameter, either lengthened or unmodified
    """
    seconds_time = timestamp // interval
    if seconds_time >= len(images):
        extras = ceil(seconds_time) - len(images) + 1
        for x in range(extras):
            images.append(Image.new('RGBA', (map_size, map_size)))
        return images
    else:
        return images


def death_swf(images):
    """Returns a gif from images input."""
    print("Creating SWF with {} images.".format(len(images)))
    file_name = "death_swf.swf"
    images2swf.writeSwf(file_name, images, duration=frame_delay, repeat=False)
    print("SWF complete.")

# Uncomment to test
# main_parse(1428822000, 1)
