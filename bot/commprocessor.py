word = True
# Always end with a space if it is a word (so, comm message vs !message)
prefix = None


def is_command(message):
    return message.startswith(prefix)


def get_command_name(message):
    no_prefix = message.replace(prefix, "", 1).strip().lower()
    if len(no_prefix) > 0:
        return no_prefix.split(" ")[0]
    else:
        # should probably use ac actual error here
        return "ERROR"


def get_arguments(message):
    no_prefix = message.replace(prefix, "", 1).strip()
    return no_prefix.split(" ")[1:]
