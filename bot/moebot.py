import asyncio
import discord
import praw
from bot import comm_processor
import random
import logging
import urllib
import io

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
            await commands[com](message, args);
        else:
            logger.debug("could not find command: "+com)
#
#   Begin commands
#

# both of these should figure out a way to store results, then grab a random one from there
async def commRandomDan(message, args):
    numSubmissions = 20
    posts = urllib.request.urlopen("https://danbooru.donmai.us/posts.json?tags=rating:s+"+args[0]).read()
    # trim off the brackets
    posts = posts[:-1]
    posts = posts[1:]
    index = random.randrange(numSubmissions)
    print(posts)
    selected = posts.split(',')[index]
    danbooruUrl = "https://danbooru.donmai.us"
    logger.debug("Downliading image from: " + danbooruUrl +selected.file_url)
    image = urllib.request.urlopen(danbooruUrl + selected.file_url)
    await client.send_file(message.channel, io.BytesIO(image.read()), filename="danbooru.png")

async def commRandomMoe(message, args):
    numSubmissions = 100
    submissions = reddit.get_subreddit('awwnime').get_hot(limit=numSubmissions)
    index = random.randrange(numSubmissions)
    currIndex = 0
    for submission in submissions:
        if currIndex == index:
            logger.debug("Downloading image from " + submission.url)
            response = urllib.request.urlopen(submission.url)
            await client.send_file(message.channel, io.BytesIO(response.read()), filename="moe.png", content=submission.title)
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
        await logout();
#
#   End commands
#

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
    #commands["db"] = commRandomDan
    #commands["danbooru"] = commRandomDan
    logger.debug("Added the following commands:")
    for c in commands:
        logger.debug(c)
    logger.debug("Moebot setup end...")

def run(token, userAgent):
    global reddit
    reddit = praw.Reddit(user_agent=userAgent)
    client.run(token)
