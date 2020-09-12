const { Command } = require('discord.js-commando');

const misc = require('../../misc.js');
const rss = require('../../rss.js');

const config = require('../../settings/config.json');
const db = require('../../settings/database.json');

module.exports = class AddCommand extends Command {
	constructor(client) {
		super(client, {
			name: 'add',
			//aliases: ['kitty-cat'],
			group: 'rss',
			memberName: 'add',
			description: 'Adds an RSS feed.',
			guildOnly: true,
			clientPermissions: ['MANAGE_CHANNELS'],
			args: [
				{
					key: 'url',
					prompt: 'No URL has been entered. Please enter a URL now.',
					type: 'string',
					validate: url => misc.validUrl(url),
				},
				{
					key: 'channel',
					prompt: 'No channel has been entered. Please enter a channel now.',
					type: 'channel',
				},
				{
					key: 'name',
					prompt: 'No name has been entered. Please enter a name now.',
					type: 'string',
				},
			],
		});
	}

	run(message, {url, channel, name}) {
		var feed = rss.findFeedByURL(url);
		var channelID = channel.id;

		if (feed == '') { //if feed is empty then the url hasn't been added to the DB yet
			var tempFeed = {
				name: name, //todo: get this name from rss feed
				url: url,
				unavailable: false,
				channels: [
					{
						feedName: name,
						channelID: channelID
					}
				]
			}
			feed = db.feeds[db.feeds.push(tempFeed) - 1]; //push() returns the new length of the array
		} else {
			//check if feed has already been added to channel
			var channels = feed.channels;
			for (var num = 0; num < channels.length; num++) {
				if (channels[num].channelID === channelID) {
					return message.say('**' + name + '** has already been added to <#' + channelID + '>.');
				}
			}

			var tempItem = {
				feedName: name,
				channelID: channelID
			}
			feed.channels.push(tempItem);
		}

		var output = 'Added **' + name + '** to <#' + channelID + '>.';
		misc.log(this.client, output, 'info', true);

		misc.saveDB(this.client);

		return message.say(output);
	}
};