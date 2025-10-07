const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');
const apiUrl = process.env.FLASK_API_URL;

module.exports = {
	data: new SlashCommandBuilder()
		.setName('registrer')
		.setDescription('Registrerer et selskap knyttet til din Discord-konto.')
		.addStringOption(option =>
			option
				.setName('navn')
				.setDescription('Selskapets navn.')
				.setRequired(true)
		),

	async execute(interaction) {
		const owner_id = interaction.user.id;
		const username = interaction.user.username;
		const name = interaction.options.getString('navn') || `${username} inc.`;

		await interaction.deferReply({ ephemeral: true });

		try {
			const response = await axios.post(`${apiUrl}/company`, {
				name,
				ownerId: owner_id,
			});

			await interaction.editReply(
				`✅ Selskapet **${response.data.name || name}** ble opprettet med eier-ID \`${owner_id}\`.`
			);
		} catch (error) {
			console.error('Error creating company:', error.response?.data || error.message);

			const errCode = error.response?.data?.error || 'unknownError';
			let translatedMessage;

			switch (errCode) {
				case 'validationError':
					translatedMessage = 'Ugyldige eller manglende felt. Kontroller at du har fylt ut alt riktig.';
					break;
				case 'companyAlreadyExistsError':
					translatedMessage = `Selskap med navn "${name}" finnes allerede.`;
					break;
				case 'ownerAlreadyHasCompanyError':
					translatedMessage = 'Du eier allerede et selskap.';
					break;
				case 'claimCooldownActiveError':
					translatedMessage = 'Du må vente før du kan kreve trygd igjen.';
					break;
				default:
					translatedMessage = 'Kunne ikke opprette selskapet. Vennligst prøv igjen senere.';
			}

			await interaction.editReply(`⚠️ ${translatedMessage}`);
		}
	},
};
