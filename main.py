import configparser
from bot import moebot
from os import path
import logging.config


def read_config():
    output = {}
    config_parser = configparser.ConfigParser()
    filepath = path.realpath("config/bot.ini")
    config_parser.read(filepath)
    for key in config_parser["settings"]:
        output[key] = config_parser["settings"][key]
    return output


if __name__ == '__main__':
    config = read_config()
    logPath = path.realpath(config["log_config_path"])
    logging.config.fileConfig(logPath)
    log = logging.getLogger("root")
    log.info("=======================================")
    log.info(" BEGIN LOG FILE FOR MOEBOT")
    moebot.setup(config) 
    moebot.run(config["bot_token"])
