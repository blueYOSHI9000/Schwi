# SchwiRSS
This is a Discord bot I mainly made for myself. It currently has RSS and Rich Presence support. The bot is written entirely in Python and as such should be able to run on nearly every system. Instructions on how to install are below. For any system that isn't Windows/Linux, simply running `main.py` should be good once the files in `/settings` have been setup (see below).

Feel free to ask me if there's any questions (Discord: `blueYOSHI#1333` - Twitter: [@yoshisrc](https://twitter.com/yoshisrc) - or simply use the Discussion tab on Github).

**Note: This bot is currently kind of a pain to use. This might change in the future. Maybe. Hopefully.**

# How to install/setup
[Tutorial is on the wiki](https://github.com/blueYOSHI9000/SchwiRSS/wiki/Install-SchwiRSS)

## (somewhat) Important info
If the bot is run on startup with the instructions here then there won't be a visible window anywhere, so the only way to close it (without having to find the exact task) is via discord commands:
- Use `schwi.kill` to shut it down
- Use `schwi.restart` to restart it

Note: Only owners can do this so make sure the correct owner ID was entered in config.json.
Instead of using the `schwi.` prefix (or whatever prefix is used) it's also possible to simply @ the bot.

Also, if the bot suddenly stopped responding, chances are it silently crashed (which hopefully never happens).