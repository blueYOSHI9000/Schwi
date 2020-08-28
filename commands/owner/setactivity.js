const { Command } = require('discord.js-commando');

const misc = require('../../misc.js');

const config = require('../../settings/config.json');
const db = require('../../settings/database.json');

module.exports = class AddCommand extends Command {
	constructor(client) {
		super(client, {
			name: 'setactivity',
			//aliases: ['kitty-cat'],
			group: 'owner',
			memberName: 'setactivity',
			description: 'Sets the bots activity. Use `' + config.bot.prefix + 'setactivity <activity type> <activity name>`. Activity type has to be "PLAYING", "WATCHING", "LISTENING" or "STREAMING", activity name can be anything. Bot-owner only. This will overwrite config.json.',
			ownerOnly: true,
			args: [
				{
					key: 'activityType',
					prompt: 'No activity type has been entered. Please enter a activity type now. It can be "PLAYING", "WATCHING", "LISTENING" or "STREAMING".',
					type: 'string',
					oneOf: ['PLAYING', 'WATCHING', 'LISTENING', 'STREAMING'],
				},
				{
					key: 'activityName',
					prompt: 'No activity name has been entered. Please enter a activity name now.',
					type: 'string',
				}
			],
		});
	}

	run(message, {activityType, activityName}) {
		activityType = activityType.toUpperCase();

		this.client.user.setActivity(activityName, {type: activityType, url: config.bot.activityURL});

		var output = 'Set bot activity to ' + activityType + ' ' + activityName;

		misc.log(this.client, output, 'info', true);

		config.bot.activityType = activityType;
		config.bot.activityName = activityName;
		misc.saveConfig(this.client);

		return message.say(output);
	}
};