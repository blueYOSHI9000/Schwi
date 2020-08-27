const { CommandoClient } = require('discord.js-commando');
const path = require('path');

const Parser = require('rss-parser');
const parser = new Parser();

const misc = require('./misc.js');

const config = require('./config.json');
const db = require('./database.json');

module.exports = {
	/*
	* Calls parseFeed() on all feeds found in the database.
	*
	* @param {object} client The original client from index.js. Required for sendMessage().
	*/
	parseAllFeeds: async function (client) {
		//var test = parseInt(db.general.rss.lastChecked) + 1800000; //1598445307526 1800000
		if (Date.now() > db.general.rss.lastChecked + 1800000) {
			misc.log(client, 'Start parsing all RSS feeds...');

			var feeds = db.g431975254525739008.rss.feeds;
			for (var num = 0; num < feeds.length; num++) {
				await module.exports.parseFeed(client, feeds[num]);
				await misc.sleep(5000); //sleep for 5s to not spam
			}

			db.general.rss.lastChecked = Date.now() - 5000; //-5s so it doesn't hit the 30min cooldown
			misc.saveDB();
			misc.log(client, 'All RSS feeds have been parsed. Last checked date has been updated to ' + new Date(Date.now()).toISOString() + '.');
		} else {
			misc.log(client, 'Skipped parsing RSS feeds as 30mins haven\'t passed yet.');
		}
	},
	/*
	* Parses a single feed and posts new entries.
	* An entry is determined to be new if it's been published after the bot checked last.
	*
	* @param {object} client The original client from index.js. Required for sendMessage().
	* @param {object} feedObj The feed's object from the database (*guild* > rss > feeds > *feed*).
	*/
	parseFeed: async function (client, feedObj) {
		var url = feedObj.url;
		var channel = feedObj.channel;
		var name = feedObj.name;

		misc.log(client, 'Parsing ' + name + '...', true);

		var feed = await parser.parseURL(url);

		var result = [];

		for (var num = 0; num < feed.items.length; num++) {
			var item = feed.items[num];
			if (Date.parse(item.pubDate) > Date.now()) {
				result.push(item);
			}
		}

		if (result.length > 0) {
			misc.sendMessage(client, channel, ':newspaper: | **' + result[0].title + '**\n\n' + result[0].link);
		}
		if (result.length === 2) {
			misc.sendMessage(client, channel, ':newspaper: | **' + result[1].title + '**\n\n' + result[1].link);
		} else if (result.length > 2) {
			misc.sendMessage(client, channel, '...and ' + (parseInt(result.length) - 1) + ' more entries from **' + name + '**: ' + url);
		}
		misc.log(client, 'Finished parsing ' + name + '.');
	}
}