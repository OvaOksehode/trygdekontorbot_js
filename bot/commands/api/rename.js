const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');
const apiUrl = process.env.FLASK_API_URL;

module.exports = {
    data: new SlashCommandBuilder()
        .setName('rebrand')
        .setDescription('Gi selskapet ditt et nytt navn!')
        .addStringOption(option =>
            option.setName('nytt_navn')
                .setDescription('Selskapets nye navn.')
                .setRequired(true)
        ),

    async execute(interaction) {
        const discordId = interaction.user.id;
        const newName = interaction.options.getString('nytt_navn');

        await interaction.deferReply({ ephemeral: true }); // gir botten tid til å gjøre API kall

        try {
            // 1️⃣ Hent selskapet til brukeren
            const queryResponse = await axios.get(`${apiUrl}/company`, {
                params: { ownerId: discordId },
            });

            const companies = queryResponse.data;
            if (!companies || companies.length === 0) {
                await interaction.editReply('⚠️ Fant ikke noe selskap registrert på deg.');
                return;
            }

            // 2️⃣ Ta externalId fra selskapet
            const companyExternalId = companies[0].externalId;

            // 3️⃣ Patch selskapet med nytt navn
            await axios.patch(`${apiUrl}/company/${companyExternalId}`, {
                name: newName
            });

            await interaction.editReply(`✅ Selskapet ditt ble omdøpt til **${newName}**!`);
        } catch (error) {
            console.error('Error rebranding company:', error.response?.data || error.message);

            let translatedMessage = 'Kunne ikke endre navnet på selskapet. Prøv igjen senere.';
            const errCode = error.response?.data?.error;

            if (errCode === 'companyNotFoundError')
                translatedMessage = 'Fant ikke noe selskap registrert på deg.';
            else if (errCode === 'companyAlreadyExistsError')
                translatedMessage = 'Et selskap med det navnet finnes allerede.';
            else if (errCode === 'databaseError')
                translatedMessage = 'En databasefeil oppstod under oppdateringen.';

            await interaction.editReply(`⚠️ ${translatedMessage}`);
        }
    },
};
