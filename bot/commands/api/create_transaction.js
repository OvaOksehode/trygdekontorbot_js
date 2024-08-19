const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('send_penger')
        .setDescription('Send penger til en annen konto.')
        .addIntegerOption(option =>
            option.setName('amount')
                .setDescription('Beløpet som skal sendes.')
                .setRequired(true))
        .addUserOption(option =>
            option.setName('receiver_user')
                .setDescription('Mottakeren (en Discord-bruker).')
                .setRequired(false))
        .addStringOption(option =>
            option.setName('receiver_name')
                .setDescription('Navnet på selskapet som skal motta penger.')
                .setRequired(false)),
    async execute(interaction) {
        // Hent parametrene fra kommandoen
        const senderId = interaction.user.id;
        const receiverUser = interaction.options.getUser('receiver_user');
        const receiverName = interaction.options.getString('receiver_name');
        const amount = interaction.options.getInteger('amount');

        try {
            // Sett opp data til API-kallet
            const data = {
                sender_owner_id: senderId,
                amount: amount
            };

            // Legg til mottakerinformasjon basert på input
            if (receiverUser) {
                data.receiver_user = { user_id: receiverUser.id, username: receiverUser.username };
            } else if (receiverName) {
                data.receiver_name = receiverName;
            } else {
                await interaction.reply('Du må spesifisere en mottaker ved bruk av enten en Discord-bruker eller et selskapsnavn.');
                return;
            }

            // Send en POST-forespørsel til Flask-API-et for å utføre transaksjonen
            const response = await axios.post('http://127.0.0.1:5000/create_transaction', data);

            // Hvis det er suksess, svar med en suksessmelding til Discord
            if (response.data.success) {
                await interaction.reply(`Transaksjonen på ${amount} ble vellykket sendt til mottakeren.`);
            } else {
                await interaction.reply(`Feil: ${response.data.error}`);
            }
        } catch (error) {
            console.error(error);
            // Håndter feil og svar med en feilmelding
            await interaction.reply('En feil oppstod under forsøket på å sende penger. Prøv igjen senere.');
        }
    },
};
