word = True
# Always end with a space if it is a word (so, comm message vs !message)
prefix = None

def isCommand(message):
    return message.startswith(prefix)

def getCommandName(message):
    noPrefix = message.replace(prefix, "", 1).strip().lower()
    if len(noPrefix) > 0:
        return noPrefix.split(" ")[0]
    else:
        # should probably use ac actual error here
        return "ERROR"

def getArguments(message):
    noPrefix = message.replace(prefix, "", 1).strip()
    return noPrefix.split(" ")[1:]
