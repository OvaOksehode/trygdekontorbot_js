const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');

module.exports = {
	data: new SlashCommandBuilder()
		.setName('registrer')
		.setDescription('Registrerer et selskap knyttet til din Discord konto.')
		.addStringOption(option =>
			option.setName('navn')
				.setDescription('Selskapets navn.')
				.setRequired(false)),
	async execute(interaction) {
		// Hent parametrene fra kommandoen
		const ownerId = interaction.user.id;
		const username = interaction.user.username;

		const name = interaction.options.getString('navn') || `${username} inc.`;
		const balance = null;

		try {
			// Send en POST-forespørsel til Flask-API-et
			const response = await axios.post(`http://127.0.0.1:5000/createcompany/${ownerId}`, null, {
				params: {
					name: name,
					balance: balance
				}
			});

			// Send svar tilbake til Discord med suksessmeldingen
			await interaction.reply(`Selskapet '${name}' ble opprettet med eier-ID ${ownerId}.`);
		} catch (error) {
			console.error(error);
			await interaction.reply('Kunne ikke opprette selskapet. Vennligst prøv igjen senere.');
		}
	},
};
