from discord.ext import commands
from datetime import datetime
import json

log_config = json.load(open('settings/config.json', 'r'))['log']

def log_level_to_num (level):
    """converts a log level string to a number

    strings are used instead of numbers directly so it's easier to read and also easier to add more levels in between old ones

    Args:
        level (string): the level in string form
    Returns:
        level in number form
    """
    if level == 'debug':
        return 1
    elif level == 'spamInfo':
        return 2
    elif level == 'info':
        return 3
    elif level == 'warn':
        return 4
    # should NOT be used in practice - this is only used insie the config
    # instead of checking whether silent is on or not it just simply increases the level so high that nothing ever gets logged
    elif level == 'silent':
        return 10
    # failsafe
    else:
        return 2


async def log (text, level, *, client=False, discord_log=True, cli_log=True):
    """logs a text to a file, the CLI and on discord.

    Note: file logging cannot be disabled since that would destroy the whole purpose of it.

    Args:
        text (string): the text to log
        level (string): the log level (view above for all possibilities)
        client: the discord.py client
        discord_log (boolean): whether it should be logged on discord (default is True)
        cli_log (boolean): whether it should be logged in cli (default is True)
    """
    level = log_level_to_num(level)

    log_level = log_level_to_num(log_config['level'])
    discord_log_output = log_config['discordLogOutput']
    discord_log_channel = log_config['discordLogChannel']
    discord_log_level = log_level_to_num(log_config['discordLogLevelOverwrite'])
    discord_log_time = log_config['logTimeOnDiscord']
    max_lines = log_config['logFileMaxLines']

    # get time and day of month
    time = str(datetime.today().day) + '-' + str(datetime.now().time())[:8]

    # print to console
    if level >= log_level and cli_log == True:
        print(f'[{time}] {text}')

    # remove newlines as neither discord nor the file need them
    text = text.replace("\n", "")

    # file logging
    with open("settings/log.txt", "r") as f:
        lines = f.readlines()

        # add newline to last line because apparently its needed
        lines.append(f'[{time}] {text}\n')

        # calculate how many lines have to be removed so there's not too many (based on max_lines)
        length = len(lines)
        length = length - max_lines
        if (length > 0):
            lines = lines[length:-1]
    with open("settings/log.txt", "w") as f:
        i = 1
        for line in lines:
            f.write(line)

    # discord logging
    # make sure that it should be logged on discord and that discord logging is enabled and that client is valid (somewhat)
    if discord_log == True and discord_log_output == True and client != False:
        # make sure that the level is 'info' or higher (since discord logs shouldn't be spammed)
        if level >= 3:
            # make sure the channel ID is valid (somewhat at least - checks whether it's all numbers)
            if discord_log_channel.isdigit():
                # check whether discordLogLevelOverwrite is used (it's equal to 2 if it isn't)
                # if it's used, compare level to that - if it isn't compare it to the normal log level
                if (discord_log_level > 2 and level >= discord_log_level) or (discord_log_level == 2 and level >= log_level):
                    channel = client.get_channel(int(discord_log_channel))
                    if discord_log_time == True:
                        await channel.send(f'`[{time}]` {text}')
                    else:
                        await channel.send(text)
