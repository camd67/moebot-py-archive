import configparser
from bot import moebot
import sys
from os import path
import datetime
import logging
import logging.config
import asyncio

def readConfig():
    output = {}
    config = configparser.ConfigParser()
    filepath = path.realpath("config/bot.ini")
    config.read(filepath)
    for key in config["settings"]:
        output[key] = config["settings"][key]
    return output


if __name__ == '__main__':
    config = readConfig()
    logPath = path.realpath(config["log_config_path"])
    logging.config.fileConfig(logPath)
    log = logging.getLogger("root")
    log.info("=======================================")
    log.info(" BEGIN LOG FILE FOR MOEBOT")
    moebot.setup(config) 
    moebot.run(config["bot_token"])
