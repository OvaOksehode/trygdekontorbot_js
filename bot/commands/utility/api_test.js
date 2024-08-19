const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');

module.exports = {
	data: new SlashCommandBuilder()
		.setName('joke')
		.setDescription('Replies with a random joke!'),
	async execute(interaction) {
		try {
			// Send API-kall med axios
			const response = await axios.get('https://official-joke-api.appspot.com/random_joke');
			
			// Hent vitsen fra API-responsen
			const joke = response.data;

			// Send svaret tilbake til Discord
			await interaction.reply(`${joke.setup} - ${joke.punchline}`);
		} catch (error) {
			console.error(error);
			await interaction.reply('Kunne ikke hente en vits akkurat nå, prøv igjen senere!');
		}
	},
};
