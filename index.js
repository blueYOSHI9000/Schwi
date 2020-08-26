const Discord = require('discord.js');
const client = new Discord.Client();

const Parser = require('rss-parser');
const parser = new Parser();

const fs = require("fs");

const config = require('./config.json');
const {token} = require('./token.json');
const db = require('./database.json');

function saveDB () {
	fs.writeFile('./database.json', JSON.stringify(db, null, '\t'), err => {

	// Checking for errors
	if (err) throw err;

	console.log("Done writing"); // Success
});
}

function copyVar (v) {
	return JSON.parse(JSON.stringify(v));
}

function removeArrayItem (array, index) {
	if (index > -1) {
		array.splice(index, 1);
	}
	return array;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function sendMessage (channel, text) {
	client.channels.cache.get(channel).send(text);
}

function parseMessage (message) {
	if (message.author.bot === true) {
		//return;
	}
	var args = message.content.slice(config.prefix.length).trim().split(/ +/);
	var command = args.shift().toLowerCase();

	switch (command) {
		case 'add':
			var url = args[0]
			var channelID = args[1].slice(2, args[1].length - 1);
			args = removeArrayItem(removeArrayItem(args, 0), 0);
			var name = args.join(' ');

			var feed = {
				name: name,
				url: url,
				channel: channelID
			}

			db.g431975254525739008.rss.feeds.push(feed);
			saveDB();

			sendMessage(channelID, 'Added **' + name + '** to this channel.');
	}
}

async function rss_parseAllFeeds (guild) {
	//var test = parseInt(db.general.rss.lastChecked) + 1800000; //1598445307526 1800000
	if (Date.now() > db.general.rss.lastChecked + 1800000) {
		var feeds = db.g431975254525739008.rss.feeds;
		for (var num = 0; num < feeds.length; num++) {
			await rss_parseFeed(feeds[num]);
			await sleep(5000); //sleep for 5s to not spam
		}

		db.general.rss.lastChecked = Date.now();
		saveDB();
		console.log('Last checked date has been updated to ' + new Date(Date.now()).toISOString() + '.');
	} else {
		console.log('Skipped parsing RSS feeds as 30mins haven\'t passed yet.');
	}
}

async function rss_parseFeed (feedObj) {
	var url = feedObj.url;
	var channel = feedObj.channel;
	var name = feedObj.name;

	console.log('Parsing ' + name + '...');

	var feed = await parser.parseURL(url);

	var result = [];

	for (var num = 0; num < feed.items.length; num++) {
		var item = feed.items[num];
		if (Date.parse(item.pubDate) > db.general.rss.lastChecked) {
			result.push(item);
		}
	}

	if (result.length > 0) {
		sendMessage(channel, ':newspaper: | **' + result[0].title + '**\n\n' + result[0].link);
	}
	if (result.length === 2) {
		sendMessage(channel, ':newspaper: | **' + result[1].title + '**\n\n' + result[1].link);
	} else if (result.length > 2) {
		sendMessage(channel, '...and ' + (parseInt(result.length) - 1) + ' more entries from **' + name + '**: ' + url);
	}
	console.log('Finished parsing ' + name + '.');
}

client.once('ready', () => {
	console.log('Ready!');

	rss_parseAllFeeds();
	setInterval(rss_parseAllFeeds, config.interval * 60000); //convert minutes to milliseconds
});

client.on('message', message => {
	if (message.content.startsWith(config.prefix) === true) {
		parseMessage(message);
	}
});

client.login(token);