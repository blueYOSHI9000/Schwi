const { CommandoClient } = require('discord.js-commando');
const path = require('path');

const Parser = require('rss-parser');
const parser = new Parser();

const misc = require('./misc.js');

const config = require('./settings/config.json');
const db = require('./settings/database.json');

module.exports = {
	/*
	* Calls parseFeed() on all feeds found in the database.
	*
	* @param {object} client The original client from index.js. Required for sendMessage().
	*/
	parseAllFeeds: async function (client) {
		if (Date.now() > db.general.rss.lastChecked + 1800000) {
			misc.log(client, 'Start parsing all RSS feeds...', 'info');

			var lastChecked = Date.now() - 5000; //-5s so it doesn't hit the interval cooldown

			var feeds = db.feeds;
			for (var num = 0; num < feeds.length; num++) {
				try {
					await module.exports.parseFeed(client, feeds[num]);
					//mark feed as available
					db.feeds[num].unavailable = false;
				} catch (e) {
					//pass the unavailable variable as the cliOnly one so discord doesn't get spammed with 'feed unavailable' messages
					misc.log(client, 'Could not parse ' + feeds[num].name + '.', 'warn', db.feeds[num].unavailable);
					misc.log(client, e, 'warn', true);

					//mark feed as unavailable
					db.feeds[num].unavailable = true;
				}
				await misc.sleep(config.rss.scanDelay); //delay next scan as to not spam sites
			}

			db.general.rss.lastChecked = lastChecked;
			misc.saveDB();
			misc.log(client, 'All RSS feeds have been parsed. Last checked date has been updated to ' + new Date(Date.now()).toISOString() + '.', 'info');
		} else {
			misc.log(client, 'Skipped parsing RSS feeds as ' + config.rss.interval + 'min haven\'t passed yet.', 'info');
		}
	},
	/*
	* Parses a single feed and posts new entries.
	* An entry is determined to be new if it's been published after the bot checked last.
	*
	* @param {object} client The original client from index.js. Required for sendMessage().
	* @param {object} feedObj The feed's object from the database (feeds > *feed*).
	*/
	parseFeed: async function (client, feedObj) {
		var name = feedObj.name;
		var url = feedObj.url;
		var channels = feedObj.channels;

		misc.log(client, 'Parsing ' + name + '...', 'spamInfo');

		var feed = await parser.parseURL(url);

		var result = [];

		for (var num = 0; num < feed.items.length; num++) {
			var item = feed.items[num];

			//console.log('pubDate: ' + Date.parse(item.pubDate));
			//console.log('lastChe: ' + db.general.rss.lastChecked);

			if (Date.parse(item.pubDate) > db.general.rss.lastChecked) {
				result.push(item);
			}
		}

		module.exports.postFeeds(client, result, channels, url);

		misc.log(client, 'Finished parsing ' + name + '.', 'spamInfo');
	},
	/*
	* Parses a single feed and posts new entries.
	* An entry is determined to be new if it's been published after the bot checked last.
	*
	* @param {object} client The original client from index.js. Required for sendMessage().
	* @param {array} items Array of all new feed items to post.
	* @param {array} channels The 'channels' array from the feed in the database.
	* @param {string} url The URL for the feed.
	*/
	postFeeds: async function (client, items, channels, url) {
		for (var num = 0; num < channels.length; num++) {
			if (items.length > 0) {
				misc.sendMessage(client, channels[num].channelID, ':newspaper: | **' + items[0].title + '**\n\n' + items[0].link);
			}
			if (items.length === 2) {
				misc.sendMessage(client, channels[num].channelID, ':newspaper: | **' + items[1].title + '**\n\n' + items[1].link);
			} else if (items.length > 2) {
				misc.sendMessage(client, channels[num].channelID, '...and ' + (parseInt(items.length) - 1) + ' more entries from **' + channels[num].feedName + '**: ' + url);
			}
		}
	},
	/*
	* Finds all RSS feeds with a certain name.
	* If it can't find an exact match it tries again while removing all special characters and without being case-sensitive.
	*
	* @param {string} name The name of the feed to find.
	* @param {boolean} inaccurate If it should skip trying to find an exact match.
	*/
	findFeedByName: function (name, inaccurate) {
		var feeds = db.g431975254525739008.rss.feeds;
		var results = [];

		if (name) {
			if (inaccurate != true) {
				for (var num = 0; num < feeds.length; num++) {
					if (name === feeds[num].name) {
						results.push(feeds[num]);
					}
				}
			}
			//if there are no results, check again while removing all special characters and transforming it to lowercase
			if (results.length === 0) {
				for (var num = 0; num < feeds.length; num++) {
					if (name.replace(/[^a-zA-Z0-9]/g, '').toLowerCase() === feeds[num].name.replace(/[^a-zA-Z0-9]/g, '').toLowerCase()) {
						results.push(feeds[num]);
					}
				}
			}
		}

		return results;
	},
	/*
	* Finds all RSS feeds with a certain url.
	*
	* @param {string} url The url of the feed to find.
	*/
	findFeedByURL: function (url) {
		var feeds = db.feeds;

		if (url) {
			for (var num = 0; num < feeds.length; num++) {
				if (url === feeds[num].url) {
					return feeds[num]
				}
			}
		}
		return null;
	},
	/*
	* Finds all RSS feeds that post in a certain channel.
	*
	* @param {string} channel The channel the feed posts in.
	*/
	findFeedByChannel: function (channel) {
		var feeds = db.g431975254525739008.rss.feeds;
		var results = [];

		if (channel) {
			for (var num = 0; num < feeds.length; num++) {
				if (channel === feeds[num].channel) {
					results.push(feeds[num]);
				}
			}
		}

		return results;
	}
}