# MoeBot
A (new) new version of MoeBot

Post all sorts of moe, memes, and also some actually useful moderation features!

## List of Commands
All commands are prefaced with `moe`
* `random` - returns a random image from r/awwnime/hot
* `count` - counts up that user's messages in that channel
* `danb tag` - searches and returns a random image given a tag (no autocomplete or corrections!)
* `sleep` - sleeps for about 5 seconds
* `brainpower` - spams twitch chat
* `goodshit` - classic meme time


## Developing MoeBot
Moebot relies upon the following libraries, all of which can be installed with pip
* [discord.py](https://github.com/Rapptz/discord.py)
* [praw](https://github.com/Rapptz/discord.py)
* configparser

You will need to create a folder named `log` containing the file `output.log` in order to get logging

You will also need to create the file `bot.ini` within the `config` folder in order to get Moebot to connect. This file contains the `bot token`, `reddit user agent`, and `log output path`

Please use branches to manage your code when contributing
