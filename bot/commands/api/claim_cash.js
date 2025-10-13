const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');
const apiUrl = process.env.FLASK_API_URL;

module.exports = {
    data: new SlashCommandBuilder()
        .setName('krev')
        .setDescription('Krev inn den søte kontantstøtten!'),

    async execute(interaction) {
        const discordId = interaction.user.id;

        await interaction.deferReply({ ephemeral: true });

        try {
            // 1️⃣ Hent selskapet som brukeren eier
            const queryResponse = await axios.get(`${apiUrl}/company`, {
                params: { ownerId: discordId },
            });

            const companies = queryResponse.data;
            if (!companies || companies.length === 0) {
                await interaction.editReply('⚠️ Du eier ikke noe selskap.');
                return;
            }

            const company = companies[0];
            const externalGuid = company.externalId;

            // 2️⃣ Gjør POST-kallet for å kreve kontantstøtte
            const response = await axios.post(`${apiUrl}/company/${externalGuid}/claim`);

            const data = response.data;
            const amount = data.amount ?? 0;

            await interaction.editReply(
                `✅ Selskapet **${company.name}** mottok en utbetaling på **${amount} JOC** fra staten! 💰`
            );

        } catch (error) {
            console.error('Error claiming cash:', error.response?.data || error.message);

            const errData = error.response?.data;
            const errCode = errData?.error;
            let translatedMessage = 'Kunne ikke kreve kontantstøtte akkurat nå. Prøv igjen senere.';

            switch (errCode) {
                case 'companyNotFoundError':
                    translatedMessage = 'Fant ikke selskapet ditt.';
                    break;
                case 'ledgerEntryNotFoundError':
                    translatedMessage = 'Fant ikke kontoen for selskapet.';
                    break;
                case 'claimCooldownActiveError': {
                    const remaining = errData?.cooldownRemainingMinutes ?? 0;
                    translatedMessage = `⏳ Du må vente **${remaining} minutt(er)** før du kan kreve kontantstøtte igjen.`;
                    break;
                }
                case 'invalidExternalGuid':
                    translatedMessage = 'Ugyldig selskaps-ID.';
                    break;
                default:
                    // fallback to API’s own message if it’s descriptive
                    if (errData?.errorDescription) {
                        translatedMessage = `⚠️ ${errData.errorDescription}`;
                    }
            }

            await interaction.editReply(`⚠️ ${translatedMessage}`);
        }
    },
};
