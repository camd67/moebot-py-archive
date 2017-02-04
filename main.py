import configparser
from bot import moebot
import sys
from os import path
import datetime
import logging
import logging.config
#import asyncio

def readConfig():
    output = {}
    config = configparser.ConfigParser()
    filepath = path.realpath("config/bot.ini")
    config.read(filepath)
    for key in config["settings"]:
        output[key] = config["settings"][key]
    return output


if __name__ == '__main__':
    logPath = path.realpath("config/log.ini")
    logging.config.fileConfig(logPath)
    log = logging.getLogger("root")
    config = readConfig()
    log.debug("=======================================")
    log.debug(" BEGIN LOG FILE FOR MOEBOT")
    moebot.setup(config)
    moebot.run(config["bot_token"])
