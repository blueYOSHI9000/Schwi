import json

from modules.log import log
import modules.convert_time as t

def get_feed_by_guild(guild):
    """Get all feeds in a certain guild

    Args:
        guild (number): the guild ID (int() is used on it so string is fine too)
    Returns:
        sends a list of all "channels" objects that matched from the database, in addition it adds a 'url' string to all of them
    """
    guild = int(guild)
    results = []
    feeds = json.load(open('settings/database.json', 'r'))['feeds']

    for f in feeds:
        for c in f['channels']:
            if int(c['guildID']) == guild:
                c['url'] = f['url']
                results.append(c)

    return results

def get_feed_by_channel(channel):
    """Get all feeds that post in a certain channel

    Args:
        channel (number): the channel ID (int() is used on it so string is fine too)
    Returns:
        sends a list of all "channels" objects that matched from the database, in addition it adds a 'url' string to all of them
    """
    channel = int(channel)
    results = []
    feeds = json.load(open('settings/database.json', 'r'))['feeds']

    for f in feeds:
        for c in f['channels']:
            if int(c['channelID']) == channel:
                c['url'] = f['url']
                results.append(c)

    return results

def get_feed_by_name(name):
    """Gets a feed by name (note: only exact matches)

    Args:
        name (string): the name to search
    Returns:
        sends a list of all "channels" objects that matched from the database, in addition it adds a 'url' string to all of thems
    """
    name = name
    results = []
    feeds = json.load(open('settings/database.json', 'r'))['feeds']

    for f in feeds:
        for c in f['channels']:
            if int(c['feedName']) == name:
                c['url'] = f['url']
                results.append(c)

    return results

def get_feed_by_url(url, guild=False):
    """Get all feeds in a certain guild

    Args:
        url (string): the url to search for
        guild (number): (optional) the guild ID (int() is used on it so string is fine too)
    Returns:
        sends all database entries if no guild specified; otherwise sends a list of all "channels" objects that matched from the database, in addition it adds a 'url' string to all of them
    """
    guild = int(guild)
    results = []
    feeds = json.load(open('settings/database.json', 'r'))['feeds']

    for f in feeds:
        if f['url'] == url:
            if guild != False:
                results.append(f)
            else:
                for c in f['channels']:
                    if int(c['guildID']) == guild:
                        c['url'] = f['url']
                        results.append(c)

    return results

def add_feed(channel, url, name):
    """Adds a new RSS feed

    Args:
        channel (channel object): the channel object, likely gotten with client.get_channel()
        url (string): url as string (technically doesn't even have to be valid)
        name (string): the name used
    Returns:
        'added' if added, 'exists' if the exact url was already added to the same channel
    """
    with open('settings/database.json', 'r+') as f:
        database = json.load(f)
        feeds = database['feeds']

        for i in range(len(feeds)):
            if feeds[i]['url'] == url:
                for c in feeds[i]['channels']:
                    if int(c['channelID']) == channel.id:
                        return 'exists'

                feeds[i]['channels'].append({'feedName': name, 'channelID': str(channel.id), 'guildID': str(channel.guild.id)})
                break
        else:
            item = {}
            item['name'] = name
            item['url'] = url
            item['unavailable'] = False
            item['lastChecked'] = t.struct_to_ms(t.get_current_time())
            item['chanels'] = [{'feedName': name, 'channelID': str(channel.id), 'guildID': str(channel.guild.id)}]

            feeds.append(item)

        # reset file position to the beginning - stackoverflow copy, dont ask
        f.seek(0)
        json.dump(database, f, indent=4)
        f.truncate()

        return 'added'