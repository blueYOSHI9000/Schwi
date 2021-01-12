import discord
import json

async def change_activity(*, atype=False, name=False, url=False, status=False, client):
    """Changes the bots activity

    Note: atype stands for activity type since 'type' seems to be used by python itself
    """
    with open('settings/config.json', 'r+') as f:
        config = json.load(f)

        # uppercase if it's a string
        if atype != False:
            atype = atype.upper()

        # make sure type is valid - otherwise get default type from config
        if atype == False or (atype not in ('PLAYING', 'WATCHING', 'LISTENING', 'STREAMING')) or atype == '':
            atype = config['bot']['activityType']
        # if type is valid then replace the config with the new type
        else:
            config['bot']['activityType'] = atype

        # same as before but with name
        if name == False:
            name = config['bot']['activityName']
        else:
            config['bot']['activityName'] = name

        # same as before but with url
        if url == False or url == '':
            url = config['bot']['activityURL']
        else:
            config['bot']['activityURL'] = url

        # lowercase if it's a string
        if status != False:
            status = status.lower()

        # same as before but with status
        if status == False or (status not in ('online', 'idle', 'dnd', 'invisible')) or status == '':
            status = config['bot']['status']
        else:
            config['bot']['status'] = status

        # reset file position to the beginning - stackoverflow copy, dont ask
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()

    if status == 'online':
        status = discord.Status.online
    elif status == 'idle':
        status = discord.Status.idle
    elif status == 'dnd':
        status = discord.Status.dnd
    elif status == 'invisible':
        status = discord.Status.invisible

    if atype == 'PLAYING':
        await client.change_presence(status=status, activity=discord.Game(name=name))
    elif atype == 'WATCHING':
        await client.change_presence(status=status, activity=discord.Streaming(name=name, url=url))
    elif atype == 'LISTENING':
        await client.change_presence(status=status, activity=discord.Activity(type=discord.ActivityType.listening, name=name))
    elif atype == 'STREAMING':
        await client.change_presence(status=status, activity=discord.Activity(type=discord.ActivityType.watching, name=name))