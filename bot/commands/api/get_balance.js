const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('saldo')
        .setDescription('Se saldo for selskapet ditt.'),
    async execute(interaction) {
        // Hent owner_id fra kommandoen
        const ownerId = interaction.user.id;
        
        try {
            // Send en GET-forespørsel til Flask-API-et
            const response = await axios.get(`http://127.0.0.1:5000/get_balance/${ownerId}`);
            
            // Send svar tilbake til Discord med saldoen
            const balance = response.data.balance;
            await interaction.reply(`Saldoen for selskapet med owner_id ${ownerId} er: ${balance} JOC.`);
        } catch (error) {
            console.error(error);
            await interaction.reply('Kunne ikke hente saldo. Vennligst prøv igjen senere.');
        }
    },
};
