import json

from modules.log import log

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
    channel = int(channel)
    results = []
    feeds = json.load(open('settings/database.json', 'r'))['feeds']

    for f in feeds:
        for c in f['channels']:
            if int(c['feedName']) == channel:
                c['url'] = f['url']
                results.append(c)

    return results
