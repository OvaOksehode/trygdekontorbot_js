const { SlashCommandBuilder, ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');
const axios = require('axios');
const apiUrl = process.env.FLASK_API_URL;

module.exports = {
    data: new SlashCommandBuilder()
        .setName('pensjoner')
        .setDescription('Skriner hele selskapet ditt. Ingen bedre måte å gjøre det på enn å gi seg på topp!'),
    async execute(interaction) {
        // Få brukerens Discord ID, som vil fungere som company_id / owner_id
        const ownerId = interaction.user.id;

        // Lag to knapper: Bekreft og Avbryt
        const row = new ActionRowBuilder()
            .addComponents(
                new ButtonBuilder()
                    .setCustomId('confirm_delete')
                    .setLabel('Bekreft')
                    .setStyle(ButtonStyle.Danger),
                new ButtonBuilder()
                    .setCustomId('cancel_delete')
                    .setLabel('Avbryt')
                    .setStyle(ButtonStyle.Secondary)
            );

        // Send en melding med bekreftelsesknappene
        const message = await interaction.reply({
            content: 'Er du sikker på at du vil slette selskapet ditt? Dette kan ikke angres!',
            components: [row],
            ephemeral: true  // Denne meldingen vil kun være synlig for brukeren selv
        });

        // Opprett en listener for knappeinteraksjonen
        const filter = i => i.user.id === interaction.user.id;

        const collector = message.createMessageComponentCollector({ filter, time: 15000 }); // Gir brukeren 15 sekunder å reagere

        collector.on('collect', async i => {
            if (i.customId === 'confirm_delete') {
                // Brukeren bekreftet slettingen
                try {
                    // Send DELETE-forespørsel til Flask API for å slette selskapet
                    await axios.delete(`${apiUrl}/deletecompany/${ownerId}`);

                    await i.update({ content: 'Selskapet ditt ble slettet.', components: [] });
                } catch (error) {
                    console.error(error);
                    await i.update({ content: 'Kunne ikke slette selskapet ditt. Vennligst prøv igjen senere.', components: [] });
                }
            } else if (i.customId === 'cancel_delete') {
                // Brukeren avbrøt slettingen
                await i.update({ content: 'Sletting av selskap avbrutt.', components: [] });
            }
        });

        collector.on('end', async collected => {
            if (collected.size === 0) {
                await interaction.editReply({ content: 'Ingen handling ble utført. Sletting av selskap avbrutt.', components: [] });
            }
        });
    },
};
