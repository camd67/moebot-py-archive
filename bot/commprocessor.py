word = True
# Always end with a space if it is a word (so, comm message vs !message)
prefix = "moe "


def isCommand(message):
    return message.startswith(prefix)

def getCommandName(message):
    noPrefix = message.replace(prefix, "").strip()
    if len(noPrefix) > 0:
        return noPrefix.split(" ")[0]
    else:
        return "ERROR"

def getArguments(message):
     noPrefix = message.replace(prefix, "").strip()
     return noPrefix.split(" ")[1:]
