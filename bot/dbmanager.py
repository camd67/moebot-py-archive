import sqlite3
import logging
from discord import utils
from bot import moebot # Maybe this should be passed as an arg instead
from bot import queries

db = None
conn = None
log = None

def init(dbPath, allowCreateDb):
    global db, conn, log
    log = logging.getLogger("database")
    conn = sqlite3.connect(dbPath)
    db = conn.cursor()
    db.execute("SELECT name FROM sqlite_master WHERE type='table'")
    if db.fetchone() is None:
        if allowCreateDb.lower() == 'true':
            log.warning("Database is empty or does not exist! Creating tables.")
            createTables()
        else:
            log.info(allowCreateDb.lower())
            raise FileNotFoundError("Database {} is empty or does not exist!".format(dbPath))

def createTables():
    schemaFile = open("bot/schema.sql", "r+")
    schema = schemaFile.read()
    schemaFile.close()
    db.executescript(schema)
    conn.commit()

def updateCommands(comms):
    try:
        db.execute('BEGIN')
        for c in comms:
            db.execute(queries.insert_command, {'name': c})
        conn.commit()
    except sqlite3.DatabaseError: # Couple of other errors to catch, but this is the only one we care about
        conn.rollback()

def banCommand(channel, user, command):
    if not isCommandPermitted(channel, command):
        log.debug("Overwriting (with ban) command permit for channel {} command {} "
                 "with new user {}.".format(channel, command, user))
    row = {
        'channelId': channel,
        'commandName': command
    }
    db.execute(queries.delete_permitted, row)
    log.debug("{} banned command {} for channel {}."
             .format(user, command, moebot.client.get_channel(channel).name))
    conn.commit()

def permitCommand(channelId, userId, command):
    if isCommandPermitted(channelId, command):
        log.debug("Overwriting (with permit) command for channel {} command {} "
                 "with new user {}.".format(channelId, command, userId))
    row = {
        'channelId': channelId,
        'userId': userId,
        'commandName': command
    }
    db.execute(queries.insert_permitted, row)
    log.debug("{} permitted command {} for channel {}."
             .format(userId, command, moebot.client.get_channel(channelId).name))
    conn.commit()

def getCommandId(commandName):
    cols = {'commandName': commandName}
    db.execute(queries.get_command_id_query, cols)
    return db.fetchone()

def isCommandPermitted(channelId, command):
    cols = {
        'channelId': channelId,
        'commandName': command
    }
    db.execute(queries.check_permitted_query, cols)
    rows = db.fetchone()
    return rows is not None
