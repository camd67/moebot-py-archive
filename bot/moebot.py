import asyncio
import discord
import praw
from bot import commprocessor
from bot import dbmanager
import random
import logging
import urllib
import io
import json
from os import path, listdir
from os.path import isfile, join
from PIL import Image
import traceback

client = discord.Client()
botAdmin = None
mods = []
commands = {}
permittedChannels = []
imagesToProcess = []
reddit = None
allEmojis = []
logger = logging.getLogger("moebot")
memeText = []
smugFaces = []
smugFolder = None
uploadFolder = None
memeTextLineCount = 0
serverRoleMember = None
deletedChannel = 0

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
    if commprocessor.isCommand(message.content) and message.author.id != client.user.id:
        com = commprocessor.getCommandName(message.content)
        args = commprocessor.getArguments(message.content)
        logger.info("Recieved command: \"{}\" from user {}/{} in channel {}/{} with params {}"
                    .format(com, message.author.name, message.author.id, message.channel.name, message.channel.id, args))
        if com in commands:
            #if com == "permit" or com == "ban" or
            #dbmanager.isCommandPermitted(message.channel.id, com):
            await asyncio.wait([client.send_typing(message.channel),
                                commands[com](message, args)
                               ])
            #else:
             #   await client.send_message(message.channel, "\"{}\" isn't
             #   permitted in this channel".format(com))
        else:
            await client.send_message(message.channel, "I don't recognize that command, \"{}\"...".format(com))
@client.event
async def on_message_delete(message):
    await client.send_message(deletedChannel, "User {}/{} had their message ch:{}/id:{} deleted with content: `{}`"
        .format(message.author.name, message.author.id, message.channel.name, message.id, message.content))

#
#   Begin commands
#
@command("rules")
async def commRules(message, args):
    if len(args) >= 1 and args[0] == "read" and message.author.top_role.name == "@everyone":
        await asyncio.wait([
            client.send_message(message.channel, "Welcome to the server <@{}>!".format(message.author.id)),
            client.add_roles(message.author, serverRoleMember),
            client.delete_message(message)
            ])
    else:
        await client.send_message(message.channel, "<@{}>, Make sure to read all the rules!".format(message.author.id))


@command("ban")
async def commBanCommand(message, args):
    # shouldn't ever be able to ban or permit the ban and permit commands
    if args[0] != "ban" and args[0] != "permit":
        dbmanager.banCommand(message.channel.id, message.author.id, args[0])
        await client.send_message(message.channel, "Command \"{}\" has been banned from this channel!".format(args[0]))

@command("permit")
async def commPermitCommand(message, args):
    # shouldn't ever be able to ban or permit the ban and permit commands
    if args[0] != "ban" and args[0] != "permit":
        dbmanager.permitCommand(message.channel.id, message.author.id, args[0])
        await client.send_message(message.channel, "Command \"{}\" has been permitted in this channel!".format(args[0]))

@command("smug")
async def commSmug(message, args):
    chosenSmug = random.randrange(len(smugFaces))
    await sendImage(message, smugFolder + smugFaces[chosenSmug], "smug.png")

@command("game")
async def commGame(message, args):
    if message.author.id == botAdmin.id:
        gameTitle = " ".join(args)
        game = discord.Game(name=gameTitle, url="", type=0)
        await asyncio.wait([client.change_status(game=game),
            client.send_message(message.channel, "What kind of game is '{}'...?".format(gameTitle))])

@command("pasta")
async def commPasta(message, args):
    await client.send_message(message.channel, memeText[random.randrange(memeTextLineCount)])

# both of these should figure out a way to store results, then grab a random
# one from there
@command("danb")
async def commRandomDan(message, args):
    numSubmissions = 50
    danbooruUrl = "https://danbooru.donmai.us"
    posts = None
    fullUrl = "{}/posts.json?limit={}&tags=rating:s+{}".format(danbooruUrl, numSubmissions, args[0])
    logger.debug("Downloading data from {}".format(fullUrl))
    try:
        posts = urllib.request.urlopen(fullUrl).read()
    except Exception as e:
        logging.exception("Failed to download all danbooru posts")
        await sendErrorMessage(message, e, "I couldn't download danbooru posts...")
        return
    # danbooru api returns an empty array on tag error...
    if len(posts) < 5:
        logger.debug("No results from: {}".format(fullUrl))
        await client.send_message(message.channel, "Doesn't look like danbooru likes that tag...")
        return
    index = random.randrange(numSubmissions)
    decodedJson = json.loads(posts.decode(encoding="UTF-8"))
    selected = decodedJson[index]
    logger.debug("Downloading image from: {}{}".format(danbooruUrl, selected["file_url"]))
    image = None
    try:
        image = urllib.request.urlopen(danbooruUrl + selected["file_url"])
        await sendImage(message, io.BytesIO(image.read()), "danbooru.png")
    except Exception as e:
        logging.exception("Failed to download danbooru image")
        await sendErrorMessage(message, e, "I couldn't download from danbooru")
        return

@command("irl")
async def commRandomMoe(message, args):
    await randomRedditImage(message, args, "anime_irl")


@command("meme")
async def commRandomMoe(message, args):
    await randomRedditImage(message, args, "animemes")


@command("random")
async def commRandomMoe(message, args):
    await randomRedditImage(message, args, "awwnime")

# Helper function to grab a random image from the top 100 images of a given subreddit
async def randomRedditImage(message, args, subreddit):
    numSubmissions = 100
    submissions = reddit.subreddit(subreddit).hot(limit=numSubmissions)
    index = random.randrange(numSubmissions)
    currIndex = 0
    for submission in submissions:
        if currIndex == index:
            if ".gif" in submission.url or submission.spoiler:
                index += 1
                continue
            try:
                response = urllib.request.urlopen(submission.url)
                if response.info().get_content_maintype() == "image":
                    logger.debug("Downloading data from post: {}/{}".format(submission.title, submission.url))
                    await sendImage(message, io.BytesIO(response.read()), filename=subreddit + ".png", content=submission.title)
                    return
                else:
                    index += 1
                    continue
            except Exception as e:
                logging.exception("Failed to download reddit submission")
                await sendErrorMessage(message, e, "I couldn't download the image...")
                return
            break
        currIndex += 1
    await client.send_message(message.channel, "Sorry, I couldn't get any images. Salt's working on fixing it! Until then, try again.")

@command("count")
async def commCount(message, args):
    counter = 0
    tmp = await client.send_message(message.channel, "Calculating messages...")
    for log in client.logs_from(message.channel, limit=100):
        if log.author == message.author:
            counter += 1
    await client.edit_message(tmp, "You have {} messages.".format(counter))

@command("sleep")
async def commSleep(message, args):
    await asyncio.sleep(5)
    await client.send_message(message.channel, "Ah, that was a nice nap")

@command("goodshit")
async def commGoodshit(message, args):
    await client.send_message(message.channel, ":ok_hand::eyes::ok_hand::eyes::ok_hand::eyes::ok_hand::eyes::ok_hand::eyes: good shit go౦ԁ sHit:ok_hand: thats :heavy_check_mark: some good:ok_hand::ok_hand:shit right:ok_hand::ok_hand:there:ok_hand::ok_hand::ok_hand: right:heavy_check_mark:there :heavy_check_mark::heavy_check_mark:if i do ƽaү so my self :100: i say so :100: thats what im talking about right there right there (chorus: ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ) mMMMMᎷМ:100: :ok_hand::ok_hand: :ok_hand:НO0ОଠOOOOOОଠଠOoooᵒᵒᵒᵒᵒᵒᵒᵒᵒ:ok_hand: :ok_hand::ok_hand: :ok_hand: :100: :ok_hand: :eyes: :eyes: :eyes: :ok_hand::ok_hand:Good shit")

@command("brainpower")
async def commBrainpower(message, args):
    bp = ["お－おおおおおおおおおお　ああえーあーあーいーあーうーおおーおおおおおおおおおおおおお　ああえーおーあーあーうーうーあー　ええーええーええーえええ　ああああえーあーえーいーえーあーじょーおおおーおおーおおーおお　ええええおーあーあああーああああ",
          "O-oooooooooo AAAAE-A-A-I-A-U-JO-oooooooooooo AAE-O-A-A-U-U-A-E-eee-ee-eee AAAAE-A-E-I-E-A-JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA", "O-oooooooooo AAAAE-A-A-I-A-U-JO-oooooooooooo AAE-O-A-A-U-U-A-E-eee-ee-eee AAAAE-A-E-I-E-A-JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA",
          "오-오오오오오오오오오오 아아아아이-아-아-아이-아-우 저-어어어어어어어어어어어어 아아이-오-아-아-우-우-아- 이-이이이-이이-이이이 아아아아이-아-이-아이-이-아-저-어어어-어어-어어-어어 이이이이오-아-아아아-아아아아"]
    if len(args) >= 1:
        try:
            await client.send_message(message.channel, bp[int(args[0]) % len(bp)])
        except ValueError:
            # Send random on error
            await client.send_message(message.channel, bp[random.randrange(4)])
    else:
        await client.send_message(message.channel, bp[random.randrange(4)])


@command("help")
async def commHelp(message, args):
    await client.send_message(message.channel, "Commands are `" + commprocessor.prefix + "` followed by one of the following: {}".format(list(commands.keys())))
#
#   End commands
#

async def sendImage(message, file, filename, content=""):
    toReact = await client.send_file(message.channel, file, filename=filename, content=content)
    await asyncio.wait([client.add_reaction(toReact, "👍"),
        client.add_reaction(toReact, "👎"),
        client.add_reaction(toReact, "🚫")
        ])

async def sendErrorMessage(message, e, customText):
    await asyncio.wait([client.send_message(message.channel, "Something went wrong... <@{0}> something went wrong! :sob: It looks like {1}"
                              .format(botAdmin.id, customText)),
        client.send_message(botAdmin, "Looks like there was an error in {0} with the message ({1}). Here's the stack trace: ```{2}``` {3}/{4} typed: {5}"
                            .format(message.channel.name, customText, traceback.format_exc(), message.author.name, message.author.id, message.content))])

async def logout():
    logger.debug("Logging out")
    logger.debug("=======================================")
    await client.logout()

def setupDatabase():
    dbmanager.updateCommands(commands)

@client.event
async def on_ready():
    logger.info("Logged in as: {0} - {1}".format(client.user.name, client.user.id))
    logger.debug("Downloading user/server information...")
    await setupDiscordInformation()
    logger.info("Moebot is ready to recieve commands")

async def setupDiscordInformation():
    global botAdmin, allEmojis, deletedChannel, serverRoleMember
    botAdmin = await client.get_user_info(configData["admin_id"])
    deletedChannel = discord.utils.get(client.get_all_channels(), id=configData["deleted_channel"])
    logger.info(deletedChannel.id)
    for server in client.servers:
        for role in server.roles:
            if role.name == "Member":
                serverRoleMember = role
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
    global smugFaces, smugFolder, uploadFolder, reddit
    reddit = praw.Reddit(user_agent=config["user_agent"], client_id=config["reddit_id"], client_secret=config["reddit_secret"])
    smugFolder = config["smug_folder"]
    uploadFolder = config["upload_folder"]
    smugFaces = [f for f in listdir(smugFolder) if isfile(join(smugFolder, f)) and not f.endswith(".ini") and not f.endswith(".db")]
    #dbmanager.init(config["db_path"], config["allow_db_creation"])
    #setupDatabase()
    commprocessor.prefix = config["prefix"] + " "
    logger.debug("Moebot local setup end...")

def run(token):
    client.run(token)
