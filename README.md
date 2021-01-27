# SchwiRSS
This is a RSS bot for discord intended to be easy to install. *This bot is NOT efficient when used in a lot of servers at once! See [MonitoRSS](https://monitorss.xyz/) if that's what you need.*

This bot is not hosted anywhere and that will likely not change (again - use MonitoRSS if that's what you need). It is however easy to setup.  
The bot is written entirely in Python and as such should be able to run on nearly every system. Instructions on how to install are below. For any system that isn't Windows/Linux, simply running `main.py` should be good once the files in `/settings` have been setup (see below).

Feel free to ask me if there's any questions (Discord: `blueYOSHI#1333` - Twitter: [@yoshisrc](https://twitter.com/yoshisrc) - or simply use the Discussion tab on Github).

**Note: The bot is still in active development so a lot of things might be annoying to do currently. This will get easier and better over time!**

# How to install/setup
[Tutorial is on the wiki](https://github.com/blueYOSHI9000/SchwiRSS/wiki/Install-SchwiRSS)

## (somewhat) Important info
If the bot is run on startup with the instructions here then there won't be a visible window anywhere, so the only way to close it (without having to find the exact task) is via discord commands:
- Use `schwi.kill` to shut it down
- Use `schwi.restart` to restart it

Note: Only owners can do this so make sure the correct owner ID was entered in config.json.
Instead of using the `schwi.` prefix (or whatever prefix is used) it's also possible to simply @ the bot.

Also, if the bot suddenly stopped responding, chances are it silently crashed (which hopefully never happens).