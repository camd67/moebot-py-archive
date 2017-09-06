import asyncio
import discord
import praw
from bot import commprocessor
from bot import dbmanager
from bot import random_location
import random
import logging
import urllib
import io
import json
from os import path, listdir
from os.path import isfile, join
import traceback

client = discord.Client()
configData = None
botAdmin = None
mods = []
commands = {}
permittedChannels = []
imagesToProcess = []
reddit = None
all_emojis = []
logger = logging.getLogger("moebot")
memeText = []
smugFaces = []
smugFolder = None
uploadFolder = None
memeTextLineCount = 0
serverRoleMember = None
deletedChannel = 0
deletedIgnoreServers = []
deletedIgnoreChannels = []
approvedChannels = []
pubg_locations = []
pubg_emote_win = None
pubg_emote_loss = None
pubg_emote_5 = None
pubg_emote_10 = None


# Decorator for commands
def command(command_name):
    def decorate(func):
        commands[command_name] = func
        logger.debug("Added command '{}'".format(command_name))
        return func

    return decorate


# Client events
@client.event
async def on_message(message):
    if commprocessor.is_command(message.content) and message.author.id != client.user.id:
        # if the message isn't in a PM and isn't in an approved channel, delete and notify user
        if message.server is None and message.channel.id not in approvedChannels:
            await asyncio.wait([
                client.send_message(message.author,
                                    "Hey there {}, just a heads up that MoeBot commands should be placed into an approved channel. Your command `{}` in channel `{}` was deleted. Please ask Salt or another admin about approved channels in your server. Typically these are channels such as `moebot`, `bot`, or `commands` but vary between servers."
                                    .format(message.author.name, message.content, message.channel.name)),
                client.delete_message(message)
            ])
        else:
            com = commprocessor.get_command_name(message.content)
            args = commprocessor.get_arguments(message.content)
            logger.info("Recieved command: \"{}\" from user {}/{} in channel {}/{} with params {}"
                        .format(com, message.author.name, message.author.id, message.channel.name, message.channel.id,
                                args))
            if com in commands:
                # if com == "permit" or com == "ban" or
                # dbmanager.isCommandPermitted(message.channel.id, com):
                await asyncio.wait([client.send_typing(message.channel),
                                    commands[com](message, args)
                                    ])
                # else:
                #    await client.send_message(message.channel, "\"{}\" isn't
                #    permitted in this channel".format(com))
            else:
                await client.send_message(message.channel,
                                          "I don't recognize that command, \"{}\"...".format(com))


@client.event
async def on_message_delete(message):
    if (message.author.id != client.user.id and
            message.server.id not in deletedIgnoreServers and
            message.channel.id not in deletedIgnoreChannels):
        await client.send_message(deletedChannel, "User {}/{} had their message ch:{}/id:{} deleted with content: `{}`"
                                  .format(message.author.name, message.author.id, message.channel.name, message.id,
                                          message.content))


#
#   Begin commands
#
@command("ignore")
async def comm_ignore(message, args):
    if message.author.id != botAdmin.id:
        await client.send_message(message.channel, "Ignore is an admin only command")
        return
    if len(args) > 2:
        await client.send_message(message.channel,
                                  "Incorrect usage, please supply <ignore type> followed by <ignore ID>")
        return
    if args[0] == "server":
        if args[1] in deletedIgnoreServers:
            await client.send_message(message.channel, "I'm already ignoring that server!")
            return
        deletedIgnoreServers.append(args[1])
        await client.send_message(message.channel, "{} Added to the list of servers to ignore".format(args[1]))
    elif args[0] == "channel":
        if args[1] in deletedIgnoreChannels:
            await client.send_message(message.channel, "I'm already ignoring that Channel!")
            return
        deletedIgnoreChannels.append(args[1])
        await client.send_message(message.channel, "{} Added to the list of channels to ignore".format(args[1]))
    else:
        await client.send_message(message.channel, "Unknown argument {}".format(args[0]))


@command("unignore")
async def comm_unignore(message, args):
    if message.author.id != botAdmin.id:
        await client.send_message(message.channel, "Unignore is an admin only command")
        return
    if len(args) > 2:
        await client.send_message(message.channel,
                                  "Incorrect usage, please supply <ignore type> followed by <ignore ID>")
        return
    try:
        if args[0] == "server":
            deletedIgnoreServers.remove(args[1])
            await client.send_message(message.channel, "{} Removed from the list of servers to ignore".format(args[1]))
        elif args[0] == "channel":
            deletedIgnoreChannels.remove(args[1])
            await client.send_message(message.channel, "{} Removed from the list of channels to ignore".format(args[1]))
        else:
            await client.send_message(message.channel, "Unknown argument {}".format(args[0]))
    except ValueError:
        await client.send_message(message.channel, "I'm not ignoring {}}...".format(args[1]))


@command("rules")
async def comm_rules(message, args):
    if len(args) >= 1 and args[0] == "read" and message.author.top_role.name == "@everyone":
        await asyncio.wait([
            client.send_message(message.channel, "Welcome to the server <@{}>!".format(message.author.id)),
            client.add_roles(message.author, serverRoleMember),
            client.delete_message(message)
        ])
    else:
        await client.send_message(message.channel, "<@{}>, Make sure to read all the rules!".format(message.author.id))


@command("ban")
async def comm_ban_command(message, args):
    if message.author.id != botAdmin.id:
        await client.send_message(message.channel, "Ban is an admin only command")
        return
    # shouldn't ever be able to ban or permit the ban and permit commands
    if args[0] != "ban" and args[0] != "permit":
        dbmanager.banCommand(message.channel.id, message.author.id, args[0])
        await client.send_message(message.channel, "Command \"{}\" has been banned from this channel!".format(args[0]))


@command("permit")
async def comm_permit_command(message, args):
    if message.author.id != botAdmin.id:
        await client.send_message(message.channel, "Permit is an admin only command")
        return
    # shouldn't ever be able to ban or permit the ban and permit commands
    if args[0] != "ban" and args[0] != "permit":
        dbmanager.permitCommand(message.channel.id, message.author.id, args[0])
        await client.send_message(message.channel, "Command \"{}\" has been permitted in this channel!".format(args[0]))


@command("smug")
async def comm_smug(message, args):
    chosen_smug = random.randrange(len(smugFaces))
    await send_image(message, smugFolder + smugFaces[chosen_smug], "smug.png")


@command("game")
async def comm_game(message, args):
    if message.author.id != botAdmin.id:
        await client.send_message(message.channel, "Game is an admin only command")
    else:
        game_title = " ".join(args)
        game = discord.Game(name=game_title, url="", type=0)
        await asyncio.wait([client.change_status(game=game),
                            client.send_message(message.channel, "What kind of game is '{}'...?".format(game_title))])


@command("pasta")
async def comm_pasta(message, args):
    await client.send_message(message.channel, memeText[random.randrange(memeTextLineCount)])


# both of these should figure out a way to store results, then grab a random
# one from there
@command("d")
@command("danb")
async def comm_random_dan(message, args):
    num_submissions = 50
    danbooru_url = "https://danbooru.donmai.us"
    full_url = "{}/posts.json?limit={}&tags=rating:s+{}".format(danbooru_url, num_submissions, args[0])
    logger.debug("Downloading data from {}".format(full_url))
    try:
        posts = urllib.request.urlopen(full_url).read()
    except Exception as e:
        logging.exception("Failed to download all danbooru posts")
        await send_error_message(message, e, "I couldn't download danbooru posts...")
        return
    # danbooru api returns an empty array on tag error...
    if len(posts) < 5:
        logger.debug("No results from: {}".format(full_url))
        await client.send_message(message.channel, "Doesn't look like danbooru likes that tag...")
        return
    index = random.randrange(num_submissions)
    decoded_json = json.loads(posts.decode(encoding="UTF-8"))
    selected = decoded_json[index]
    logger.debug("Downloading image from: {}{}".format(danbooru_url, selected["file_url"]))
    try:
        image = urllib.request.urlopen(danbooru_url + selected["file_url"])
        await send_image(message, io.BytesIO(image.read()), "danbooru.png")
    except Exception as e:
        logging.exception("Failed to download danbooru image")
        await send_error_message(message, e, "I couldn't download from danbooru")
        return


@command("irl")
async def comm_random_irl(message, args):
    await random_reddit_image(message, args, "anime_irl")


@command("meme")
async def comm_random_meme(message, args):
    await random_reddit_image(message, args, "animemes")


@command("r")
@command("random")
async def comm_random_moe(message, args):
    await random_reddit_image(message, args, "awwnime")


# Helper function to grab a random image from the top 100 images of a given subreddit
async def random_reddit_image(message, args, subreddit):
    num_submissions = 100
    submissions = reddit.subreddit(subreddit).hot(limit=num_submissions)
    index = random.randrange(num_submissions)
    curr_index = 0
    for submission in submissions:
        if curr_index == index:
            if ".gif" in submission.url or submission.spoiler:
                index += 1
                continue
            try:
                response = urllib.request.urlopen(submission.url)
                if response.info().get_content_maintype() == "image":
                    logger.debug("Downloading data from post: {}/{}".format(submission.title, submission.url))
                    await send_image(message, io.BytesIO(response.read()), filename=subreddit + ".png",
                                     content=submission.title)
                    return
                else:
                    index += 1
                    continue
            except Exception as e:
                logging.exception("Failed to download reddit submission")
                await send_error_message(message, e, "I couldn't download the image...")
                return
        curr_index += 1
    await client.send_message(message.channel,
                              "Sorry, I couldn't get any images. Salt's working on fixing it! Until then, try again.")


@command("sleep")
async def comm_sleep(message, args):
    await asyncio.sleep(5)
    await client.send_message(message.channel, "Ah, that was a nice nap")


@command("goodshit")
async def comm_goodshit(message, args):
    await client.send_message(message.channel,
                              ":ok_hand::eyes::ok_hand::eyes::ok_hand::eyes::ok_hand::eyes::ok_hand::eyes: good shit go౦ԁ sHit:ok_hand: thats :heavy_check_mark: some good:ok_hand::ok_hand:shit right:ok_hand::ok_hand:there:ok_hand::ok_hand::ok_hand: right:heavy_check_mark:there :heavy_check_mark::heavy_check_mark:if i do ƽaү so my self :100: i say so :100: thats what im talking about right there right there (chorus: ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ) mMMMMᎷМ:100: :ok_hand::ok_hand: :ok_hand:НO0ОଠOOOOOОଠଠOoooᵒᵒᵒᵒᵒᵒᵒᵒᵒ:ok_hand: :ok_hand::ok_hand: :ok_hand: :100: :ok_hand: :eyes: :eyes: :eyes: :ok_hand::ok_hand:Good shit")


@command("brainpower")
async def comm_brainpower(message, args):
    bp = [
        "お－おおおおおおおおおお　ああえーあーあーいーあーうーおおーおおおおおおおおおおおおお　ああえーおーあーあーうーうーあー　ええーええーええーえええ　ああああえーあーえーいーえーあーじょーおおおーおおーおおーおお　ええええおーあーあああーああああ",
        "O-oooooooooo AAAAE-A-A-I-A-U-JO-oooooooooooo AAE-O-A-A-U-U-A-E-eee-ee-eee AAAAE-A-E-I-E-A-JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA",
        "O-oooooooooo AAAAE-A-A-I-A-U-JO-oooooooooooo AAE-O-A-A-U-U-A-E-eee-ee-eee AAAAE-A-E-I-E-A-JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA",
        "오-오오오오오오오오오오 아아아아이-아-아-아이-아-우 저-어어어어어어어어어어어어 아아이-오-아-아-우-우-아- 이-이이이-이이-이이이 아아아아이-아-이-아이-이-아-저-어어어-어어-어어-어어 이이이이오-아-아아아-아아아아"]
    if len(args) >= 1:
        try:
            await client.send_message(message.channel, bp[int(args[0]) % len(bp)])
        except ValueError:
            # Send random on error
            await client.send_message(message.channel, bp[random.randrange(4)])
    else:
        await client.send_message(message.channel, bp[random.randrange(4)])


@command("pubg")
async def comm_pubg(message, args):
    if len(args) > 0 and args[0] == "map":
        await client.send_file(message.channel, configData["pubg_data_path"] + "Map.png", filename="map.png")
    else:
        val = random.random()
        for loc in pubg_locations:
            if loc.rate >= val:
                desc = "<@{}>: You must go to #{}: {}! Make sure to react with the match outcome.".format(
                    message.author.id, loc.index, loc.name)
                path = configData["pubg_data_path"] + loc.img_path
                logger.debug("PUBG - {} Chosen: {}".format(val, str(loc)))
                sent = await client.send_file(message.channel, path, filename=loc.name + ".png", content=desc)
                await asyncio.wait([
                    client.add_reaction(sent, pubg_emote_win),
                    client.add_reaction(sent, pubg_emote_loss),
                    client.add_reaction(sent, pubg_emote_5),
                    client.add_reaction(sent, pubg_emote_10),
                ])
                return
        logger.warn("Got to the end of pubg command with no location selected...")


@command("help")
async def comm_help(message, args):
    reply = "Commands are `" + commprocessor.prefix + "` followed by one of the following: {}".format(
        list(commands.keys()))
    if args[0] == "pubg":
        reply = "Command `pubg`: Generate a random location to land at for the game PlayerUnknown's BattleGrounds. Your goal is to travel to that location at some point during the game. Use `pubg map` to display a map of every location"
    elif args[0] == "danb" or args[0] == "d":
        reply = "Command `danb` or `d`: Download a random image from danbooru.donmai.us, you must supply a tag to search for."
    await client.send_message(message.channel, reply)


#
#   End commands
#

async def send_image(message, file, filename, content=""):
    to_react = await client.send_file(message.channel, file, filename=filename, content=content)
    await asyncio.wait([
        client.add_reaction(to_react, "👍"),
        client.add_reaction(to_react, "👎"),
        client.add_reaction(to_react, "🚫")
    ])


async def send_error_message(message, e, custom_text):
    await asyncio.wait([client.send_message(message.channel,
                                            "Something went wrong... <@{0}> something went wrong! :sob: It looks like {1}"
                                            .format(botAdmin.id, custom_text)),
                        client.send_message(botAdmin,
                                            "Looks like there was an error in {0} with the message ({1}). Here's the stack trace: ```{2}``` {3}/{4} typed: {5}"
                                            .format(message.channel.name, custom_text, traceback.format_exc(),
                                                    message.author.name, message.author.id, message.content))])


async def logout():
    logger.debug("Logging out")
    logger.debug("=======================================")
    await client.logout()


def setup_database():
    dbmanager.updateCommands(commands)


@client.event
async def on_ready():
    logger.info("Logged in as: {0} - {1}".format(client.user.name, client.user.id))
    logger.debug("Downloading user/server information...")
    await setup_discord_information()
    logger.info("Moebot is ready to recieve commands")


async def setup_discord_information():
    global botAdmin, all_emojis, deletedChannel, serverRoleMember, pubg_emote_win, pubg_emote_loss, pubg_emote_10, pubg_emote_5
    botAdmin = await client.get_user_info(configData["admin_id"])
    deletedChannel = discord.utils.get(client.get_all_channels(), id=configData["deleted_channel"])
    logger.info(deletedChannel.id)
    for server in client.servers:
        for role in server.roles:
            if role.name == "Member":
                serverRoleMember = role
    all_emojis = list(client.get_all_emojis())
    # TODO: move this to a class, and also iterate once not 4 times...
    pubg_emote_win = next((x for x in all_emojis if x.name == "pubg_win"), None)
    pubg_emote_loss = next((x for x in all_emojis if x.name == "pubg_loss"), None)
    pubg_emote_5 = next((x for x in all_emojis if x.name == "pubg_top5"), None)
    pubg_emote_10 = next((x for x in all_emojis if x.name == "pubg_top10"), None)
    logger.debug("Done downloading setup information")


def setup(config):
    logger.debug("Moebot local setup begin...")
    global configData
    configData = config
    f = open(path.realpath(config["meme_file"]), "r", encoding="UTF-8")
    global memeTextLineCount
    global memeText
    for line in f:
        memeTextLineCount += 1
        memeText.append(line)
    f.close()
    global smugFaces, smugFolder, uploadFolder, reddit, pubg_locations, approvedChannels
    reddit = praw.Reddit(user_agent=config["user_agent"], client_id=config["reddit_id"],
                         client_secret=config["reddit_secret"])
    smugFolder = config["smug_folder"]
    uploadFolder = config["upload_folder"]
    smugFaces = [f for f in listdir(smugFolder) if
                 isfile(join(smugFolder, f)) and not f.endswith(".ini") and not f.endswith(".db")]
    pubg_file = open(config["pubg_data_path"] + "standard.txt", "r", encoding="UTF-8")
    for line in pubg_file:
        split_line = line.split(":")
        pubg_locations.append(
            random_location.RandomLocation(split_line[0].strip(), split_line[1], split_line[2], split_line[3].strip()))
    pubg_locations = sorted(pubg_locations, key=lambda x: x.rate)
    approvedChannels = config["allow_channels"].split(",")
    # dbmanager.init(config["db_path"], config["allow_db_creation"])
    # setupDatabase()
    commprocessor.prefix = config["prefix"] + " "
    logger.debug("Moebot local setup end...")


def run(token):
    client.run(token)
