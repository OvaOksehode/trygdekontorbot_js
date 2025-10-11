const { SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const axios = require('axios');
const apiUrl = process.env.FLASK_API_URL;

module.exports = {
	data: new SlashCommandBuilder()
		.setName('pensjoner')
		.setDescription('Sletter selskapet ditt permanent. Er du sikker på at du vil gi deg på topp?'),

	async execute(interaction) {
		const discordId = interaction.user.id;

		const row = new ActionRowBuilder().addComponents(
			new ButtonBuilder()
				.setCustomId('confirm_delete')
				.setLabel('Bekreft')
				.setStyle(ButtonStyle.Danger),
			new ButtonBuilder()
				.setCustomId('cancel_delete')
				.setLabel('Avbryt')
				.setStyle(ButtonStyle.Secondary)
		);

		// ⚠️ Non-ephemeral so button collector works
		const message = await interaction.reply({
			content: '⚠️ Er du sikker på at du vil slette selskapet ditt? Dette kan **ikke angres**!',
			components: [row],
			ephemeral: false,
		});

		const filter = i => i.user.id === discordId;
		const collector = message.createMessageComponentCollector({ filter, time: 15000 });

		collector.on('collect', async i => {
			if (i.customId === 'confirm_delete') {
				try {
					// 1️⃣ Query the company belonging to this user
					const queryResponse = await axios.get(`${apiUrl}/company`, {
						params: { ownerId: discordId },
					});

					const companies = queryResponse.data;

					if (!companies || companies.length === 0) {
						await i.update({
							content: '⚠️ Fant ikke noe selskap registrert på deg.',
							components: [],
						});
						return;
					}

					// Assuming one company per user
					const companyUuid = companies[0].externalId;

					// 2️⃣ Delete the company using its UUID
					await axios.delete(`${apiUrl}/company/${companyUuid}`);

					await i.update({
						content: '✅ Selskapet ditt ble slettet permanent.',
						components: [],
					});
				} catch (error) {
					console.error('Error deleting company:', error.response?.data || error.message);

					let translatedMessage = 'Kunne ikke slette selskapet ditt. Prøv igjen senere.';
					const errCode = error.response?.data?.error;

					if (errCode === 'companyNotFoundError')
						translatedMessage = 'Fant ikke noe selskap registrert på deg.';
					else if (errCode === 'databaseError')
						translatedMessage = 'En databasefeil oppstod under slettingen.';

					await i.update({
						content: `⚠️ ${translatedMessage}`,
						components: [],
					});
				}
			} else if (i.customId === 'cancel_delete') {
				await i.update({
					content: '❎ Sletting av selskap avbrutt.',
					components: [],
				});
			}
		});

		collector.on('end', async collected => {
			if (collected.size === 0) {
				await interaction.editReply({
					content: '⌛ Ingen handling ble utført. Sletting av selskap avbrutt.',
					components: [],
				});
			}
		});
	},
};
