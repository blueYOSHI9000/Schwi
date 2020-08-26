function saveGuilds () {
	fs.writeFile('./guilds.json', JSON.stringify(guilds, null, '\t'), err => {

	// Checking for errors
	if (err) throw err;

	console.log("Done writing"); // Success
});
}

function copyVar (v) {
	return JSON.parse(JSON.stringify(v));
}