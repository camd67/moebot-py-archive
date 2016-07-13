import asyncio
import discord
import praw
from bot import comm_processor
import random
import logging
import urllib
import io
import json

client = discord.Client()
admins = ["84394456941359104", "172495826264915968"]
mods = []
commands = {}
permittedChannels = [];
reddit = None;
logger = logging.getLogger("moebot")

# Client events
@client.event
async def on_ready():
    logger.debug('Logged in as:')
    logger.debug(client.user.name)
    logger.debug(client.user.id)

@client.event
async def on_message(message):
    if comm_processor.isCommand(message.content) and message.author.id != client.user.id:
        com = comm_processor.getCommandName(message.content)
        logger.debug("Recieved command: " + com)
        args = comm_processor.getArguments(message.content)
        if com in commands:
            await client.send_typing(message.channel)
            await commands[com](message, args);
        else:
            logger.debug("could not find command: "+com)
#
#   Begin commands
#

# both of these should figure out a way to store results, then grab a random one from there
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
        await sendErrorMessage(message, e)
        return
    # danbooru api returns an empty array on tag error...
    if len(posts) < 5:
        logger.debug("No results from: {}".format(fullUrl))
        await client.send_message(message.channel, "I don't recognize that tag...")
        return
    index = random.randrange(numSubmissions)
    decodedJson = json.loads(posts.decode(encoding="UTF-8"))
    selected = decodedJson[index]
    logger.debug("Downloading image from: {}{}".format(danbooruUrl, selected["file_url"]))
    image = None
    try:
        image = urllib.request.urlopen(danbooruUrl + selected["file_url"])
        await client.send_file(message.channel, io.BytesIO(image.read()), filename="danbooru.png")
    except Exception as e:
        logging.exception("Failed to download danbooru image")
        await sendErrorMessage(message, e)
        return

async def commRandomMoe(message, args):
    numSubmissions = 100
    submissions = reddit.get_subreddit('awwnime').get_hot(limit=numSubmissions)
    index = random.randrange(numSubmissions)
    currIndex = 0
    for submission in submissions:
        if currIndex == index:
            if ".gif" in submission.url or "i.redd.it" in submission.url:
                index += 1
                continue
            logger.debug("Downloading image from " + submission.url)
            try:
                response = urllib.request.urlopen(submission.url)
                await client.send_file(message.channel, io.BytesIO(response.read()), filename="moe.png", content=submission.title)
            except Exception as e:
                logging.exception("Failed to download reddit submission")
                await sendErrorMessage(message, e)
                return
            break
        currIndex+= 1

async def commCount(message, args):
    counter = 0
    tmp = await client.send_message(message.channel, 'Calculating messages...')
    async for log in client.logs_from(message.channel, limit=100):
        if log.author == message.author:
            counter += 1
    await client.edit_message(tmp, 'You have {} messages.'.format(counter))

async def commSleep(message, args):
    await asyncio.sleep(5)
    await client.send_message(message.channel, 'Ah, that was a nice nap')

async def commPermit(message, args):
    # add in argument of who to permit
    if message.author.id in admins:
        await client.send_message(message.channel, 'You\'re already in the list of admins!')
    else:
        admins.append(message.author.id)
        await client.send_message(message.channel, 'Added ' + message.author.name + ' to the list of admins ('+message.author.id+')')

async def commGoodshit(message, args):
    await client.send_message(message.channel, ":ok_hand::eyes::ok_hand::eyes::ok_hand::eyes::ok_hand::eyes::ok_hand::eyes: good shit go౦ԁ sHit:ok_hand: thats :heavy_check_mark: some good:ok_hand::ok_hand:shit right:ok_hand::ok_hand:there:ok_hand::ok_hand::ok_hand: right:heavy_check_mark:there :heavy_check_mark::heavy_check_mark:if i do ƽaү so my self :100: i say so :100: thats what im talking about right there right there (chorus: ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ) mMMMMᎷМ:100: :ok_hand::ok_hand: :ok_hand:НO0ОଠOOOOOОଠଠOoooᵒᵒᵒᵒᵒᵒᵒᵒᵒ:ok_hand: :ok_hand::ok_hand: :ok_hand: :100: :ok_hand: :eyes: :eyes: :eyes: :ok_hand::ok_hand:Good shit")

async def commBrainpower(message, args):
    bp = ["お－おおおおおおおおおお　ああえーあーあーいーあーうーおおーおおおおおおおおおおおおお　ああえーおーあーあーうーうーあー　ええーええーええーえええ　ああああえーあーえーいーえーあーじょーおおおーおおーおおーおお　ええええおーあーあああーああああ",
        "O-oooooooooo AAAAE-A-A-I-A-U-JO-oooooooooooo AAE-O-A-A-U-U-A-E-eee-ee-eee AAAAE-A-E-I-E-A-JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA", "O-oooooooooo AAAAE-A-A-I-A-U-JO-oooooooooooo AAE-O-A-A-U-U-A-E-eee-ee-eee AAAAE-A-E-I-E-A-JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA",
        "오-오오오오오오오오오오 아아아아이-아-아-아이-아-우 저-어어어어어어어어어어어어 아아이-오-아-아-우-우-아- 이-이이이-이이-이이이 아아아아이-아-이-아이-이-아-저-어어어-어어-어어-어어 이이이이오-아-아아아-아아아아"]
    await client.send_message(message.channel, bp[random.randrange(4)])

async def commLogout(message, args):
    if message.author.id in admins:
        await client.send_message(message.channel, 'Goodbye everyone!')
        logger.debug("Logging out...")
        await logout()
#
#   End commands
#

async def sendErrorMessage(message, e):
    await client.send_message(message.channel, "Something went wrong... <@%s> something went wrong! :sob:" % admins[0])
    # would be good to send the exception over to Salt in a private message

async def logout():
    await client.logout()
    logger.debug("Logged out")
    logger.debug("=======================================")

def setup():
    logger.debug("Moebot setup begin...")
    commands["logout"] = commLogout
    commands["brainpower"] = commBrainpower
    commands["goodshit"] = commGoodshit
    commands["sleep"] = commSleep
    commands["count"] = commCount
    commands["random"] = commRandomMoe
    commands["db"] = commRandomDan
    commands["danbooru"] = commRandomDan
    logger.debug("Added the following commands:")
    for c in commands:
        logger.debug(c)
    logger.debug("Moebot setup end...")

def run(token, userAgent):
    global reddit
    reddit = praw.Reddit(user_agent=userAgent)
    client.run(token)
