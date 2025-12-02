const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');
const apiUrl = process.env.FLASK_API_URL;

module.exports = {
    data: new SlashCommandBuilder()
        .setName('transactions')
        .setDescription('Henter de nyeste transaksjonene for selskapet ditt!')
        .addIntegerOption(option =>
            option.setName('limit')
                .setDescription('Hvor mange transaksjoner som skal hentes (max 50)')
                .setRequired(false)
        ),

    async execute(interaction) {
        const discordId = interaction.user.id;
        const limit = Math.min(interaction.options.getInteger('limit') || 20, 50);

        await interaction.deferReply({ ephemeral: true });

        try {
            // 1️⃣ Hent selskapet til brukeren
            const queryRes = await axios.get(`${apiUrl}/company`, {
                params: { ownerId: discordId },
            });

            const companies = queryRes.data;
            if (!companies || companies.length === 0) {
                await interaction.editReply('⚠️ Fant ikke noe selskap registrert på deg.');
                return;
            }

            const companyExternalId = companies[0].externalId;

            // 2️⃣ Hent transaksjoner for selskapet
            const txRes = await axios.get(`${apiUrl}/company/${companyExternalId}/transaction`, {
                params: { limit },
            });

            const transactions = txRes.data;
            if (!transactions || transactions.length === 0) {
                await interaction.editReply('ℹ️ Ingen transaksjoner funnet for selskapet ditt.');
                return;
            }

            // 3️⃣ Format melding
            const formatted = transactions.map(tx => {
                const direction = tx.senderCompanyExternalId === companyExternalId ? 'Utgående' : 'Innkommende';
                return `• [${direction}] ${tx.amount} 💰 - ID: ${tx.externalId} - ${tx.createdAt}`;
            }).join('\n');

            await interaction.editReply(`📜 De nyeste transaksjonene for selskapet ditt:\n${formatted}`);

        } catch (error) {
            console.error('Error fetching transactions:', error.response?.data || error.message);
            await interaction.editReply('⚠️ Kunne ikke hente transaksjonene. Prøv igjen senere.');
        }
    },
};
