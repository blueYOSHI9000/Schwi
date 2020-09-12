const { CommandoClient } = require('discord.js-commando');
const path = require('path');

const fs = require("fs");

const config = require('./settings/config.json');
const db = require('./settings/database.json');

module.exports = {
	/*
	* Log something to both console and to a discord channel (currently hardcoded).
	*
	* @param {object} client The original client from index.js.
	* @param {string} text The text that should be logged.
	* @param {string} level Level of importance, check logLevelToNum() for available levels.
	* @param {boolean} cliOnly If it should only be logged to commandline.
	*/
	log: function (client, text, level, cliOnly) {
		level = module.exports.logLevelToNum(level);
		var configLevel = module.exports.logLevelToNum(config.log.level);
		var discordLogLevelOverwrite = module.exports.logLevelToNum(config.log.discordLogLevelOverwrite);

		if (level < configLevel) {
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
	},
	/*
	* Transform a log level string into a number for easy comparing (like only do x if log level is important or higher).
	* Numbers shouldn't be used directly so more levels can be easily added if necessary.
	* Returns null if it couldn't transform the level.
	*
	* @param {string} level Level of importance, can be "debug" > "spamInfo" > "info" > "important".
	*/
	logLevelToNum: function (level) {
		switch (level) {
			case 'debug':
				level = 1;
				break;
			case 'spamInfo': //every bit of info without anything that's purely for debugging (like showing variables)
				level = 2;
				break;
			case 'info': //useful info like when RSS feeds get parsed but not too spammy like posting every single RSS feed being parsed
				level = 3;
				break;
			case 'warn':
				level = 4;
				break;
			default:
				return null;
		}
		return level;
	},
	/*
	* Saves the databse to database.json.
	* Has to be called after each edit to the DB so data doesn't get lost.
	*
	* @param {object} client The original client from index.js. Only needed for sendMessage().
	*/
	saveDB: function (client) {
		module.exports.saveFile(client, './settings/database.json', db);
	},
	/*
	* Saves the config to config.json.
	* Has to be called after each edit to config so data doesn't get lost.
	*
	* @param {object} client The original client from index.js. Only needed for sendMessage().
	*/
	saveConfig: function (client) {
		module.exports.saveFile(client, './settings/config.json', config);
	},
	/*
	* Save a file, mainly used to save updated JSON files.
	*
	* @param {object} client The original client from index.js. Only needed for sendMessage().
	* @param {string} filePath The path to the file.
	* @param {object} obj The object that the original file can be accessed with.
	*/
	saveFile: function (client, filePath, obj) {
		fs.writeFile(filePath, JSON.stringify(obj, null, '\t'), err => {

			// Checking for errors
			if (err) throw err;

			module.exports.log(client, filePath + ' saved.', 'info'); // Success
		});
	},
	/*
	* Sends a message to a specific channel.
	*
	* @param {object} client The original client from index.js. Messages can not be sent without this.
	* @param {string} channel The channel ID, has to be a string.
	* @param {string} text The text that should be sent.
	*/
	sendMessage: function (client, channel, text) {
		try {
			client.channels.cache.get(channel).send(text);
		} catch (e) {
			console.log('[ERROR] Could not send message.');
			console.log(e);
		}
	},
	/*
	* Stops execution for the specified amount of time.
	*
	* @param {number} ms Time in ms.
	*/
	sleep: function (ms) {
		return new Promise(resolve => setTimeout(resolve, ms));
	},
	/*
	* Copies a variable without it being a reference.
	*
	* @param {any variable} v The variable that has to be copied.
	*/
	copyVar: function (v) {
		return JSON.parse(JSON.stringify(v));
	},
	/*
	* Removes an item from an array.
	*
	* @param {array} array The array.
	* @param {number} index The index of the item that should be removed.
	*/
	removeArrayItem: function (array, index) {
		if (index > -1) {
			array.splice(index, 1);
		}
		return array;
	},
	/*
	* Checks if a URL is valid.
	*
	* @param {string} str The URL that should be checked.
	*/
	validUrl: function (str) {
		var pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
			'((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
			'((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
			'(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
			'(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
			'(\\#[-a-z\\d_]*)?$','i'); // fragment locator
		return !!pattern.test(str);
	}
};