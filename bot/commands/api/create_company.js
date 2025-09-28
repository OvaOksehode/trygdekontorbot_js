const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');
const apiUrl = process.env.FLASK_API_URL;

module.exports = {
	data: new SlashCommandBuilder()
		.setName('registrer')
		.setDescription('Registrerer et selskap knyttet til din Discord konto.')
		.addStringOption(option =>
			option
				.setName('navn')
				.setDescription('Selskapets navn.')
				.setRequired(true)
		),
	async execute(interaction) {
		// Hent parametrene fra kommandoen
		const owner_id = interaction.user.id;
		const username = interaction.user.username;

		const name = interaction.options.getString('navn') || `${username} inc.`;

		try {
			// Send en POST-forespørsel til Flask-API-et
			const response = await axios.post(`${apiUrl}/company`, {
				name: name,
				ownerId: owner_id,
			});

			// Send svar tilbake til Discord med suksessmeldingen
			await interaction.reply(
				`✅ Selskapet **${response.data.name || name}** ble opprettet med eier-ID \`${owner_id}\`.`
			);
		} catch (error) {
			console.error('Error creating company:', error.response?.data || error.message);
			await interaction.reply(
				'⚠️ Kunne ikke opprette selskapet. Vennligst prøv igjen senere.'
			);
		}
	},
};