from discord.ext import commands
from datetime import datetime
import json

log_config = json.load(open('settings/config.json', 'r'))['log']

def log_level_to_num (level):
    """converts a log level string to a number

    strings are used instead of numbers directly so it's easier to read and also easier to add more levels in between old ones
    """
    if level == 'debug':
        return 1
    elif level == 'spamInfo':
        return 2
    elif level == 'info':
        return 3
    elif level == 'warn':
        return 4
    elif level == 'silent':
        return 10
    # failsafe
    else:
        return 2


async def log (text, level, *, client=False, cliOnly=False):
    """logs a text to a file (TODO), the CLI and on discord

    discord logs only if enabled by the user
    """
    level = log_level_to_num(level)

    log_level = log_level_to_num(log_config['level'])
    discord_log_output = log_config['discordLogOutput']
    discord_log_channel = log_config['discordLogChannel']
    discord_log_level = log_level_to_num(log_config['discordLogLevelOverwrite'])
    max_lines = log_config['logFileMaxLines']

    # get time
    time = str(datetime.now().time())[:8]

    # print to console
    if level >= log_level:
        print(f'[{time}] {text}')

    # remove newlines as neither discord nor the file need them
    text = text.replace("\n", "")

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
    # make sure that it's not CLI only and that discord logging is enabled and that client is valid (somewhat)
    if cliOnly != True and discord_log_output == True and client != False:
        # make sure that the level is 'info' or higher (since discord logs shouldn't be spammed)
        if level >= 3:
            # make sure the channel ID is valid (somewhat at least - checks whether it's all numbers)
            if discord_log_channel.isdigit():
                # check whether discordLogLevelOverwrite is used (it's equal to 2 if it isn't)
                # if it's used, compare level to that - if it isn't compare it to the normal log level
                if (discord_log_level > 2 and level >= discord_log_level) or (discord_log_level == 2 and level >= log_level):
                    channel = client.get_channel(int(discord_log_channel))
                    await channel.send(text)



"""log: function (client, level, text, cliOnly, passthrough) {
        level = module.exports.logLevelToNum(level);
        var configLevel = module.exports.logLevelToNum(config.log.level);
        var discordLogLevelOverwrite = module.exports.logLevelToNum(config.log.discordLogLevelOverwrite);

        if (level < configLevel) {
            return;
        }

        if (passthrough != undefined) {
            console.log(passthrough);
            return;
        }

        var time = new Date();
        time = time + '';
        time = time.slice(16,24);

        text = '[' + time + '] ' + text;

        console.log(text);

        if (typeof client === 'object' && client != null) { //check if client is actually a client
            if (cliOnly != true) { //check that it's not CLI only
                if (level >= 3) { //check if log level is info or higher
                    if (config.log.discordLogOutput === true) { //check in config.json if discord logs are allowed
                        if (discordLogLevelOverwrite === null || discordLogLevelOverwrite <= level) { //check if discordLogLevelOverwrite is used and compare the level against it
                            module.exports.sendMessage(client, config.log.discordLogChannel, text);
                        }
                    }
                }
            }
        }
    },"""