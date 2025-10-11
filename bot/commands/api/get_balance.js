const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');
const apiUrl = process.env.FLASK_API_URL;

module.exports = {
    data: new SlashCommandBuilder()
        .setName('balance')
        .setDescription('Viser saldoen til selskapet ditt.'),
    
    async execute(interaction) {
        const owner_id = interaction.user.id;

        await interaction.deferReply({ ephemeral: true });

        try {
            // Query the company owned by this user
            const response = await axios.get(`${apiUrl}/company`, {
                params: { ownerId: owner_id }
            });

            const companies = response.data;

            if (!companies || companies.length === 0) {
                await interaction.editReply('⚠️ Du eier ikke noe selskap.');
                return;
            }

            // Assuming one company per owner
            const company = companies[0];
            const balance = company.balance ?? 0;

            await interaction.editReply(
                `💰 Selskapet **${company.name}** har en saldo på **${balance}** JOC.`
            );
        } catch (error) {
            console.error('Error fetching company balance:', error.response?.data || error.message);

            const errCode = error.response?.data?.error || 'unknownError';
            let translatedMessage;

            switch (errCode) {
                case 'companyNotFoundError':
                    translatedMessage = 'Du eier ikke noe selskap.';
                    break;
                default:
                    translatedMessage = 'Kunne ikke hente saldoen. Vennligst prøv igjen senere.';
            }

            await interaction.editReply(`⚠️ ${translatedMessage}`);
        }
    },
};
