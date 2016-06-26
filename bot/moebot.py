import asyncio
import discord
import praw
from bot import comm_processor
import random

client = discord.Client()
admins = ["84394456941359104", "172495826264915968"]

# Client events
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if comm_processor.isCommand(message.content) and message.author.id != client.user.id:
        com = comm_processor.getCommandName(message.content)
        if com == "count":
            counter = 0
            tmp = await client.send_message(message.channel, 'Calculating messages...')
            async for log in client.logs_from(message.channel, limit=100):
                if log.author == message.author:
                    counter += 1
            await client.edit_message(tmp, 'You have {} messages.'.format(counter))
        elif com == "sleep":
            await asyncio.sleep(5)
            await client.send_message(message.channel, 'Done sleeping')
        elif com == "permit":
            # add in argument of who to permit
            if message.author.id in admins:
                await client.send_message(message.channel, 'You\'re already in the list of admins!')
            else:
                admins.append(message.author.id)
                await client.send_message(message.channel, 'Added ' + message.author.name + ' to the list of admins ('+message.author.id+')')
            print(admins)
        elif com == "logout" and message.author.id in admins:
            await client.send_message(message.channel, 'Goodbye everyone!')
            print("Logging out...")
            await client.logout()
        elif com == "goodshit":
            await client.send_message(message.channel, ":ok_hand::eyes::ok_hand::eyes::ok_hand::eyes::ok_hand::eyes::ok_hand::eyes: good shit go౦ԁ sHit:ok_hand: thats :heavy_check_mark: some good:ok_hand::ok_hand:shit right:ok_hand::ok_hand:there:ok_hand::ok_hand::ok_hand: right:heavy_check_mark:there :heavy_check_mark::heavy_check_mark:if i do ƽaү so my self :100: i say so :100: thats what im talking about right there right there (chorus: ʳᶦᵍʰᵗ ᵗʰᵉʳᵉ) mMMMMᎷМ:100: :ok_hand::ok_hand: :ok_hand:НO0ОଠOOOOOОଠଠOoooᵒᵒᵒᵒᵒᵒᵒᵒᵒ:ok_hand: :ok_hand::ok_hand: :ok_hand: :100: :ok_hand: :eyes: :eyes: :eyes: :ok_hand::ok_hand:Good shit")
        elif com == "brainpower":
            bp = ["お－おおおおおおおおおお　ああえーあーあーいーあーうーおおーおおおおおおおおおおおおお　ああえーおーあーあーうーうーあー　ええーええーええーえええ　ああああえーあーえーいーえーあーじょーおおおーおおーおおーおお　ええええおーあーあああーああああ",
    			"O-oooooooooo AAAAE-A-A-I-A-U-JO-oooooooooooo AAE-O-A-A-U-U-A-E-eee-ee-eee AAAAE-A-E-I-E-A-JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA", "O-oooooooooo AAAAE-A-A-I-A-U-JO-oooooooooooo AAE-O-A-A-U-U-A-E-eee-ee-eee AAAAE-A-E-I-E-A-JO-ooo-oo-oo-oo EEEEO-A-AAA-AAAA",
    			"오-오오오오오오오오오오 아아아아이-아-아-아이-아-우 저-어어어어어어어어어어어어 아아이-오-아-아-우-우-아- 이-이이이-이이-이이이 아아아아이-아-이-아이-이-아-저-어어어-어어-어어-어어 이이이이오-아-아아아-아아아아"]
            await client.send_message(message.channel, bp[random.randrange(4)])

def setup():
    print('------')
    print("Moebot setup...")
    print('------')

def run(token):
    client.run(token)
