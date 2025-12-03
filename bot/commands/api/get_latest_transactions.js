const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const axios = require('axios');
const apiUrl = process.env.FLASK_API_URL;

function toOsloTime(utcString) {
    const date = new Date(utcString);
    
    return new Intl.DateTimeFormat('nb-NO', {
        dateStyle: 'short',
        timeStyle : 'medium',
        timeZone: 'Europe/Oslo'
    }).format(date);
}

module.exports = {
    data: new SlashCommandBuilder()
        .setName('transaksjoner')
        .setDescription('Henter de nyligste transaksjonene for selskapet ditt.')
        .addIntegerOption(option =>
            option.setName('antall')
                .setDescription('Antallet transaksjoner som skal hentes.')
                .setRequired(false)
                .setMaxValue(10)
                .setMinValue(1)
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
            const embeds = transactions.map(tx => {
                const isOutgoing = tx.senderCompanyExternalId === companyExternalId
                const direction = isOutgoing ? 'Utgående' : 'Innkommende';

                const counterpartName = isOutgoing
                        ? tx.receiverCompanyName || tx.receiverCompanyExternalId
                        : tx.senderCompanyName || tx.senderCompanyExternalId;
                
                return new EmbedBuilder()
                .setTitle(`${direction} transaksjon`)
                .setColor(isOutgoing ? 0xff4cd2 : 0x35ed7e)
                .addFields(
                    {name: "Beløp", value: `${tx.amount} JOC`, inline: true},
                    {name: "Transaksjons-ID", value: `${tx.externalId}`, inline: true},
                    {name: isOutgoing ? "Sendt til" : "Mottatt fra", value: `${counterpartName}`, inline: true},
                    {name: "Tidspunkt", value: toOsloTime(tx.createdAt), inline: true}
                )
            })

            await interaction.editReply({
                content : `📜 De nyligste transaksjonene for selskapet ditt`,
                embeds
            });

        } catch (error) {
            console.error('Error fetching transactions:', error.response?.data || error.message);
            await interaction.editReply('Kunne ikke hente transaksjonene. Prøv igjen senere.');
        }
    },
};
