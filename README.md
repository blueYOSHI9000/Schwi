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

## Don't rely on this too much
I once missed an appointment because I looked at the `schwi.listreminders` time, converted it from UTC to my local timezone with `schwi.converttime` and it ended up being wrong. Now, you might be thinking that I fixed this since then but boy do I have bad news for you!
In addition to that, RSS feeds are *NOT* reliable. Though this partly to blame for the RSS site I added because that one broke too. Needless to say, I think you figured out that this too did not get fixed.

## So when will these be fixed
Once I rewrite the entire project. It should be noted that my plans for the rewrite get bigger and more ambitious with each passing day. It should also be noted that I'm currently rewriting another project as well so it'll take some time until I get to this one again and even when I'll get around to this, rewriting it will take quite some time since my plans are probably bigger than NASA's plans at that point.