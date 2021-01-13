import discord

import feedparser
import json
import time

import modules.convert_time as t
from modules.log import log

def scan_feed(url):
    """Simply scans a feed and returns it. Does NOT check whether
    """
    return feedparser.parse(url)

def get_new_items_from_feed(*, feed=False, url=False, last_checked):
    """Scans a feed for new items and returns a list of them.

    Args:
        feed: an already scanned feed
        url (string): url to scan in case a feed isn't given directly
        last_checked (time.struct_time object): last time it got checked for new items
    Returns:
        list of all new items
    """
    # if
    if feed == False:
        feed = scan_feed(url)

    # check if the feed exists - otherwise return False to indicate that the page likely doesn't exist (anymore)
    try:
        feed.entries[0]
    except (NameError, AttributeError, IndexError):
        return False

    final = []
    # dont stop scanning after the items are older since some new items might've been lower in the list (like for Manga, some special in-between chapters might've been released later on and as such are lower in the list where they technically belong despite being new)
    for i in feed.entries:
        if i.published_parsed > t.ms_to_struct(last_checked):
            final.append(i)

    # TODO: add the last 10 titles or something to the database as a double check

    return final

def get_embed_from_item(*, item, db_item, feed):
    """Creates an embed from an rss feed.

    Args:
        item: the rss feed item that should be used
        db_item: the corresponding feed in the database (used in case name & url can't be parsed)
        feed: the full rss feed, not just the item (used for thumbnail)
    Returns:
        discord.Embed object
    """
    embed = {}
    date_format = json.load(open('settings/config.json', 'r'))['rss']['dateFormat']

    if hasattr(item, 'title'):
        embed['title'] = item.title
    else:
        embed['title'] = db_item['name']

    if hasattr(item, 'summary'):
        # cut if summary is above 350 characters
        embed['description'] = item.summary[:350]
    else:
        embed['description'] = '[no description found]'

    if hasattr(item, 'link'):
        embed['url'] = item.link
    else:
        embed['url'] = db_item['url']

    embed = discord.Embed(**embed)

    if hasattr(item, 'published_parsed'):
        embed.set_footer(text=time.strftime(date_format, item.published_parsed))
    else:
        embed.set_footer(text='[could not parse time published]')

    image_found = False

    try:
        for i in item.media_content:
            if i['medium'] == 'image':
                embed.set_image(url = i['url'])
                image_found = True
    except (NameError, AttributeError, IndexError):
        pass

    # if no image was found, set the thumbnail as image instead
    try:
        if image_found == True:
            embed.set_thumbnail(url = feed.feed.image.href)
        else:
            embed.set_image(url = feed.feed.image.href)
    except (NameError, AttributeError, IndexError):
        pass

    return embed


async def scan_all_feeds(*, client):
    await log('Start scanning all feeds.', 'info', client=client)

    with open('settings/database.json', 'r+') as f:
        database = json.load(f)
        feeds = database['feeds']
        config = json.load(open('settings/config.json', 'r'))

        combine_posts = config['rss']['combinePosts']
        oldest_posts_first = config['rss']['oldestFirst']
        interval = config['rss']['interval'] * 60

        if interval < 600:
            interval = 600

        # convert both to seconds
        scan_delay = config['rss']['scanDelay'] / 1000
        post_delay = config['rss']['postDelay'] / 1000

        if scan_delay < 0:
            scan_delay = 0

        if post_delay < 0:
            post_delay = 0

        # go through all feeds that have to be scanned
        # use range() because the original feeds variable has to be edited
        for i in range(len(feeds)):
            time.sleep(scan_delay)

            current_time = t.get_current_time()

            # multiply interval by 1000 to convert from seconds to ms
            # subtract 5s from interval to make sure that a scheduled scan doesn't hit it
            last_checked_with_interval = feeds[i]['lastChecked'] + (interval * 1000 - 5000)
            last_checked_with_interval = t.ms_to_struct(last_checked_with_interval)

            if last_checked_with_interval > current_time:
                await log(f' Skip scanning {feeds[i]["name"]} ({int(interval / 60)}min interval).', 'spamInfo', client=client)
                continue

            await log(f'Start scanning {feeds[i]["name"]}.', 'spamInfo', client=client)

            feed = scan_feed(feeds[i]['url'])
            results = get_new_items_from_feed(feed=feed, last_checked=feeds[i]['lastChecked'])

            # if feed is unavailable, mark it as such with the current time
            if results == False:
                await log(f'{feeds[i]["name"]} is not available (url: \'{feeds[i]["url"]}\'.', 'spamInfo', client=client)
                # only mark it with the current time if it wasn't already marked as unavailable before
                if feeds[i]['unavailable'] == False:
                    feeds[i]['unavailable'] = t.struct_to_ms(current_time)

                    for c in feeds[i]['channels']:
                        time.sleep(post_delay)

                        channel = client.get_channel(int(c['channelID']))
                        await channel.send(f'**{c["feedName"]}** is not available (this message won\'t be posted again until it\'s available again). Feed URL: {feeds[i]["url"]}')

                continue

            # check if posts should be combined
            if len(results) > combine_posts and combine_posts != 0:
                if oldest_posts_first == True:
                    first_item = results[len(results) - 1]
                else:
                    first_item = results[0]

                embed = get_embed_from_item(item=first_item, db_item=feeds[i], feed=feed)

                for c in feeds[i]['channels']:
                    time.sleep(post_delay)

                    channel = client.get_channel(int(c['channelID']))
                    await channel.send(embed=embed)
                    await channel.send(f'...and {len(results) - combine_posts} more from {c["feedName"]}.')

            # post all items
            else:
                for r in range(len(results)):
                    results[r] = get_embed_from_item(item=results[r], db_item=feeds[i], feed=feed)

                # reverse the results list so the oldest items come first
                if oldest_posts_first == True:
                    results = results[::-1]

                for c in feeds[i]['channels']:
                    time.sleep(post_delay)

                    channel = client.get_channel(int(c['channelID']))
                    for r in results:
                        await channel.send(embed=r)

            feeds[i]['lastChecked'] = t.struct_to_ms(t.get_current_time())
            await log(f' Done scanning {feeds[i]["name"]}.', 'spamInfo', client=client)

        database['feeds'] = feeds
        database['general']['rss']['lastChecked'] = t.struct_to_ms(t.get_current_time())
        # reset file position to the beginning - stackoverflow copy, dont ask
        f.seek(0)
        json.dump(database, f, indent=4)
        f.truncate()
        await log('All feeds scanned.', 'info', client=client)