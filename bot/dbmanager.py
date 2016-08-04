import sqlite3
import logging
from discord import utils
from bot import moebot # Maybe this should be passed as an arg instead
from bot import queries

def createTables():
    schemaFile = open('bot/schema.sql', 'r')
    schema = schemaFile.read()
    schemaFile.close()
    db.executescript(schema)
    conn.commit()

log = logging.getLogger("database")
sqliteDbFile = "data/moedata.db"
conn = sqlite3.connect(sqliteDbFile)
db = conn.cursor()
db.execute("SELECT name FROM sqlite_master WHERE type='table'")
if db.fetchone() is None:
    createTables()

def addChannelData(channel):
    row = { 'channelId': channel }
    db.execute(queries.add_channel_query, row)
    log.info('Inserted new channel {} into table channels.'.format(moebot.client.get_channel(channel).name))
    conn.commit()

def addUserData(user, channel): # Could pass server instead of channel
    # check for existing user, if not add
    row = { 'userId': user }
    db.execute(queries.add_user_query, row)
    log.debug('Inserted new user {} ({})',
              utils.find(lambda m: m.id == user, channel.server.members, user))
    conn.commit()

def permitCommand(channel, user, command):
    if isCommandPermitted(channel, command):
        log.info('Overwriting command permit for channel {} command {} '
                 'with new user {}.'.format(channel, command, user))
    row = {
        'channelId': channel,
        'userId': user,
        'commandId': command.lower()
    }
    db.execute(queries.insert_permitted_query, row)
    log.info("{} inserted into {} into permitted commands for channel {}."
             .format(user, command, moebot.client.get_channel(channel).name))
    conn.commit()

def getCommandId(commandName):
    cols = { 'commandName': commandName }
    db.execute(queries.get_command_id_query, cols)
    return db.fetchone()

def isCommandPermitted(channel, command):
    cols = {
        'channelId': channel,
        'commandId': command
    }
    db.execute(queries.check_permitted_query, cols)
    rows = db.fetchone()
    return rows is not None
