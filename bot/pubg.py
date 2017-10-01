import asyncio
import random
import logging
import discord
from os import listdir

from os.path import isfile, join


class Pubg(object):
    logger = logging.getLogger("moebot")  # type: logging
    modes = []

    def __init__(self, client, data_path):
        self.client = client  # type: discord.Client
        self.data_path = data_path  # type: str
        Pubg.modes = [".", "AR", "H", "M", "E", "X", "EZ", "CD", "D", "C", "A", "S", "4C"]

        self.pubg_locations = []
        loc_file = open(self.data_path + "locations.txt", "r", encoding="UTF-8")
        for line in loc_file:
            split_line = line.split("_")
            self.pubg_locations.append((int(split_line[0]), split_line[1].strip()))
        self.pubg_locations = sorted(self.pubg_locations, key=lambda x: x[0])
        loc_file.close()

        # This should be re-written a little bit at a later date
        self.random_values = {}
        value_file = open(self.data_path + "values.txt", "r", encoding="UTF-8")
        current_type = ""  # type: str
        for line in value_file:
            split_line = line.split("_")
            if split_line[0][0] == "~":
                current_type = split_line[1].strip()
                self.random_values[current_type] = []
            else:
                self.random_values[current_type].append((int(split_line[0]), float(split_line[1].strip())))
        path = self.data_path + "imgs"
        temp_images = [f for f in listdir(path) if
                       isfile(join(path, f)) and not f.endswith(".ini")]
        self.images = []
        for filename in temp_images:
            split_filename = filename.split("_")
            self.images.append((int(split_filename[0]), filename))
        self.images = sorted(self.images, key=lambda x: x[0])

        all_emojis = list(client.get_all_emojis())
        self.pubg_emote_win = next((x for x in all_emojis if x.name == "pubg_win"), None)
        self.pubg_emote_loss = next((x for x in all_emojis if x.name == "pubg_loss"), None)
        self.pubg_emote_5 = next((x for x in all_emojis if x.name == "pubg_top5"), None)
        self.pubg_emote_10 = next((x for x in all_emojis if x.name == "pubg_top10"), None)

    async def process_message(self, message, args):
        """Entry point for processing pubg messages"""
        args[0] = str.upper(args[0])
        if len(args) > 0:
            if args[0] == "MAP":
                await self.client.send_file(message.channel, self.data_path + "Map.png", filename="map.png")
            elif args[0] == "RULES" or args[0] == "HELP":
                await self.print_help(message)
            elif args[0] == "MODES":
                await self.print_modes(message, False)
            elif args[0] in Pubg.modes:
                await self.choose_location(message, args)
            else:
                await self.client.send_message(message.channel, "Sorry, I don't understand how to process that choice. Try out `!moe pubg help` for some help on using the pubg command!")
        else:
            await self.client.send_message(message.channel, "Sorry, I don't understand how to process that choice. Try out `!moe pubg help` for some help on using the pubg command!")

    async def choose_location(self, message, args):
        random_value = random.random()
        if args[0] not in self.random_values:
            self.print_modes(message.channel, True)
            return
        chosen_values = self.random_values[args[0]]
        for value in chosen_values:
            if value[1] >= random_value:
                selected_location = self.pubg_locations[value[0] - 1]
                image_path = self.images[value[0] - 1][1]
                desc = "<@{}>: You must go to #{}: {}! Make sure to react with the match outcome.".format(
                    message.author.id, selected_location[0], selected_location[1])
                path = self.data_path + "imgs/" + image_path
                Pubg.logger.debug("PUBG - {} Chosen: {}".format(random_value, str(value)))
                sent = await self.client.send_file(message.channel, path, filename=selected_location[1] + ".png", content=desc)
                await asyncio.wait([
                    self.client.add_reaction(sent, self.pubg_emote_win),
                    self.client.add_reaction(sent, self.pubg_emote_loss),
                    self.client.add_reaction(sent, self.pubg_emote_5),
                    self.client.add_reaction(sent, self.pubg_emote_10),
                ])
                return
        Pubg.logger.warning("Got to the end of pubg command with no location selected...")

    async def print_help(self, message):
        """print help message to the channel"""
        await self.client.send_message(message.channel,
                                       """**1.** All alive players must be at the location on the ground at the same time to count as completing the challenge. This means all players must be outside of any vehicle.
 **2.** You can complete the challenge at any stage of the game. You don't have to land there, go there first, etc.
 **3.** When you are within ~50m(1/2 a minimap square) of any structure pictured on the location image you are officialy at the location.
 **4.** For Capes you must reach within ~10m of the edge to count.
 **5.** For Mountains you must reach the top to count.
 **6.** For Fields you must reach the near center of the field to count.
 **7.** In Four Corners each member's requirement is singularly their own. They can move from the location once they reach it and do not need to wait for their teammates to reach theirs.""")

    async def print_modes(self, message, error):
        """Print out all the modes to the channel"""
        if error:
            await self.client.send_message(message.channel, "Sorry, I don't know that mode. try one of these:")
        await self.client.send_message(message.channel,
                                       """"`!moe pubg ?`" - Random Mode: Play a randomly selected mode (excluding 4C)
 "`!moe pubg .`" - Easy Random Mode: Play a random mode selected from M, E, EZ, CD, and C.
 "`!moe pubg AR`" - All Random: Every location is available with an equal chance to roll.
 "`!moe pubg H`" - Hard: Every location is available with the odds stacked in the favor of dangerous and useless areas.
 "`!moe pubg M`" - Medium: Every location is available with the odds stacked in the favor of moderately risky, but profitable areas.
 "`!moe pubg E`" - Easy: Every location is available with the odds stacked in the favor of safe, somewhat profitable areas.
 "`!moe pubg X`" - Chaos: Every location is available with the odds being stacked in an unusual manner.
 "`!moe pubg EZ`" - EZPZ: Only useful locations are available to roll with the odds stacked in the favor of profitable, non-risky areas.
 "`!moe pubg CD`" - Chicken Dinner: Only roll safe to somewhat risky, but profitable areas.
 "`!moe pubg D`" - Dangerous: Only roll "hot spots" that regularly have lots of action.
 "`!moe pubg C`" - City: Only roll major cities.
 "`!moe pubg A`" - Adventure: Only roll places like Fields, Capes, Mountains, and other more or less useless locations.
 "`!moe pubg S`" - Suicide: Only roll extremely high risk or totally unrewarding locations.
 "`!moe pubg 4C`" - Four Corners(SQUADS ONLY): Each player goes to a seperate area of the map and then meets up with their team.""")