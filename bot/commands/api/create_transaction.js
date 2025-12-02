const { SlashCommandBuilder } = require("discord.js");
const axios = require("axios");
const apiUrl = process.env.FLASK_API_URL;

module.exports = {
  data: new SlashCommandBuilder()
    .setName("send_penger")
    .setDescription("Send penger til et annet selskap.")
    .addIntegerOption((option) =>
      option
        .setName("amount")
        .setDescription("Beløpet som skal sendes.")
        .setRequired(true)
    )
    .addStringOption((option) =>
      option
        .setName("receiver_company_name")
        .setDescription("Navnet på selskapet som skal motta penger.")
        .setRequired(true)
    ),

  async execute(interaction) {
    const owner_id = interaction.user.id;
    const receiverCompanyName = interaction.options.getString(
      "receiver_company_name"
    );
    const amount = interaction.options.getInteger("amount");

    await interaction.deferReply();

    try {
      // 1️⃣ Hent avsenderens selskap
      const senderResponse = await axios.get(`${apiUrl}/company`, {
        params: { ownerId: owner_id },
      });

      const senderCompanies = senderResponse.data;
      if (!senderCompanies || senderCompanies.length === 0) {
        await interaction.editReply(
          "⚠️ Du eier ikke noe selskap å sende penger fra."
        );
        return;
      }

      const senderCompanyId = senderCompanies[0].companyId;

      // 2️⃣ Hent mottakerens selskap basert på navn
      const receiverResponse = await axios.get(`${apiUrl}/company`, {
        params: { name: receiverCompanyName },
      });

      const receiverCompanies = receiverResponse.data;
      if (!receiverCompanies || receiverCompanies.length === 0) {
        await interaction.editReply(
          `⚠️ Fant ikke noe selskap med navnet **${receiverCompanyName}**.`
        );
        return;
      }

      const receiverCompanyId = receiverCompanies[0].companyId;

      // 3️⃣ Send POST til backend
      const payload = {
        senderCompanyId,
        receiverCompanyId,
        amount,
      };

      const response = await axios.post(
        `${apiUrl}/company-transaction`,
        payload
      );

      if (response.status === 201) {
        const data = response.data;
        await interaction.editReply(
          `✅ Transaksjonen på **${amount} JOC** ble sendt fra **${senderCompanyId}** til **${receiverCompanyName}**.\n` +
            `Transaksjons-ID: \`${data.externalId}\``
        );
      } else {
        await interaction.editReply(
          `⚠️ Uventet svar fra API: ${response.status}`
        );
      }
    } catch (error) {
      console.error(
        "Feil under sending av transaksjon:",
        error.response?.data || error.message
      );

      const errMsg = error.response?.data?.error || "En ukjent feil oppstod.";
      await interaction.editReply(
        `⚠️ Kunne ikke sende transaksjonen. ${errMsg}`
      );
    }
  },
};
