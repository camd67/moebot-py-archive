import configparser
from bot import moebot
import sys
import datetime

def readConfig():
    output = {}
    config = configparser.ConfigParser()
    config.read("./config/bot.ini")
    for key in config["settings"]:
        output[key] = config["settings"][key]
    return output

config = readConfig()

if __name__ == '__main__':
    #sys.stdout = open(config["output"], "a+")
    print("=======================================")
    print(" BEGIN LOG FILE FOR MOEBOT ON : {:%Y-%m-%d %H:%M:%S}'".format(datetime.datetime.now()))
    moebot.setup()
    moebot.run(config["bottoken"])
