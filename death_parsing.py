__author__ = 'JackelPPA'

import ast
import requests
from math import ceil, floor
from PIL import Image, ImageDraw, ImageFont
from visvis.vvmovie import images2swf


# Riot API Key
key = "SECRET_KEY"

# Constants
size = 2
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
        url = "https://na.api.pvp.net/api/lol/na/v4.1/game/ids?beginDate={0}&api_key={1}".format(epoch + m * 300, key)
        request = requests.get(url)
        games += ast.literal_eval(request.text)

    for g in games:
        images = death_parsing(images, g, interval)

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


def draw_deaths(images, x, y, victim, time, interval):
    """
    :param images: The set of images to draw on.
    :param x: x-Coordinate of death.
    :param y: y-Coordinate of death.
    :param victim: The individual killed.
    :param time: Timestamp.
    :param interval: The sampling duration.
    :return: Returns a set of images, with the image mapped.
    """
    font = ImageFont.truetype("C:/Windows/Fonts/ariblk.ttf", 12)
    images = set_images(images, time, interval)
    x_off, y_off = 570, 420
    x += x_off
    y += y_off

    for i, image in enumerate(images):
        if time <= i * interval <= time + 2 * interval:
            im = Image.new('RGBA', (map_size, map_size))
            draw = ImageDraw.Draw(im, "RGBA")
            if victim <= 5:
                color = (0, 0, 255, dot_opacity)
            else:
                color = (255, 0, 0, dot_opacity)

            draw.ellipse((x / scale - r,
                          map_size - y / scale - r,
                          x / scale + r,
                          map_size - y / scale + r),
                         fill=color)

            minutes = floor(i * interval / 60000)
            seconds = (i * interval / 1000) % 60
            draw.text((0, map_size - 24),
                      "{0}{1}:{2}{3}".format(floor(minutes / 10),
                                             round(minutes % 10),
                                             floor(seconds / 10),
                                             round(seconds % 10)),
                      font=font)
            del draw

            print("Plotted at {}.".format(i))

            images[i] = Image.alpha_composite(image, im)

        else:
            im = Image.new('RGBA', (map_size, map_size))
            draw = ImageDraw.Draw(im, "RGBA")
            minutes = floor(i * interval / 60000)
            seconds = (i * interval / 1000) % 60
            draw.text((0, map_size - 24),
                      "{0}{1}:{2}{3}".format(floor(minutes / 10),
                                             round(minutes % 10),
                                             floor(seconds / 10),
                                             round(seconds % 10)),
                      font=font)
            del draw

            images[i] = Image.alpha_composite(image, im)

    return images


def set_images(images, time, interval):
    """
    Prepares frames if there aren't enough to represent the current time.
    :param images: The list of images being mapped.
    :param time: Timestamp value.
    :param interval: The sampling duration.
    :return: The images parameter, either lengthened or unmodified
    """
    if time / interval >= len(images):
        extras = ceil(time / interval) - len(images) + 1
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
# main_parse(1428825600, 1)
