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
                .setRequired(true)),
    async execute(interaction) {
        // Hent parametrene fra kommandoen
        const companyId = interaction.user.id;
        const newName = interaction.options.getString('nytt_navn');

        try {
            // Send en POST-forespørsel til Flask-API-et for å endre navnet på selskapet
            const response = await axios.post('${apiUrl}/rename_company', {
                company_id: companyId,
                new_name: newName
            });

            // Hvis det er suksess, svar med en suksessmelding til Discord
            await interaction.reply(response.data.message);
        } catch (error) {
            console.error(error);
            // Håndter feil og svar med en feilmelding
            if (error.response && error.response.data && error.response.data.error) {
                await interaction.reply(`Error: ${error.response.data.error}`);
            } else {
                await interaction.reply('An error occurred while renaming the company.');
            }
        }
    },
};
