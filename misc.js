const { CommandoClient } = require('discord.js-commando');
const path = require('path');

const fs = require("fs");

const config = require('./config.json');
const db = require('./database.json');

module.exports = {
	/*
	* Log something to both console and to a discord channel (currently hardcoded).
	*
	* @param {object} client The original client from index.js.
	* @param {string} text The text that should be logged.
	* @param {boolean} cliOnly If it should only be logged to commandline.
	*/
	log: function (client, text, cliOnly) {
		var time = new Date();
		time = time + '';
		time = time.slice(16,24);

		text = '[' + time + '] ' + text;

		console.log(text);
		if (client && cliOnly != true) {
			module.exports.sendMessage(client, '748143884911116328', text);
		}
	},
	/*
	* Saves the databse to database.json.
	* Has to be called after each edit to the DB so data doesn't get lost.
	*/
	saveDB: function () {
		fs.writeFile('./database.json', JSON.stringify(db, null, '\t'), err => {

			// Checking for errors
			if (err) throw err;

			module.exports.log(null, 'Database saved.'); // Success
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