import configparser
import moebot

def readConfig():
    output = {}
    config = configparser.ConfigParser()
    config.read("./config/bot.ini")
    for key in config["Connection"]:
        output[key] = config["Connection"][key]
    return output

config = readConfig()
moebot.runClient(config["BotToken"])
