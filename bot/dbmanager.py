import sqlite3
import logging


log = logging.getLogger("database")
sqliteDbFile = "moedata.db"
conn = sqlite3.connect(sqliteDbFile)
db = conn.cursor()

def permitCommand(channel, user, command):
    db.execute("SELECT id FROM command WHERE name = ?", command)
    rows = db.fetchall()
    if not rows or len(rows) > 1:
        log.error("More than one command found when searching for {}".format(command))
    db.execute("INSERT INTO permittedCommand VALUES(NULL, ?, ?, ?)", channel.id, rows[0].id, user.id)
    log.info("Inserted into permitted commands the command {} to {}".format(command, channel.name))
    log.info(db.fetchone())

def isCommandPermitted(channel, command):
    db.execute("SELECT channelId FROM permittedCommand JOIN command ON command.id = permittedCommand.commandId WHERE channelId = ? AND commandId = ?", channel.id, command)
    rows = db.fetchall()
    return not rows
