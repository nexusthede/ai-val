const { Client, GatewayIntentBits } = require('discord.js');
const axios = require('axios');
const keepAlive = require('./keepAlive');

keepAlive();

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ],
});

// User IDs for personality modes
const SOFT_USER = '1440364578012790856';
const MEAN_USER = '856264288858538004';

// Cooldown map
const cooldown = new Map();

// Hermes free endpoint
const HERMES_API_URL = 'https://hermes.ai.unturf.com/v1/completions';
const HERMES_MODEL = 'adamo1139/Hermes-3-Llama-3.1-8B-FP8-Dynamic';

client.once('ready', () => {
  console.log(`Val online as ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
  if (message.author.bot) return;

  // Only reply if Val is mentioned
  const valRegex = /\bval\b/i;
  if (!valRegex.test(message.content)) return;

  // Cooldown per user (4 seconds)
  const now = Date.now();
  const last = cooldown.get(message.author.id) || 0;
  if (now - last < 4000) return;
  cooldown.set(message.author.id, now);

  // Clean message
  const userMessage = message.content.replace(/\n/g, ' ').trim();

  // Build personality prompt
  let prompt = "You are Val, a Discord user-like AI. Reply naturally like a real person.\n";
  if (message.author.id === SOFT_USER) {
    prompt += "Soft, shy, gentle, slightly hesitant with this user.\n";
  } else if (message.author.id === MEAN_USER) {
    prompt += "Blunt, dismissive, a bit mean but still helpful with this user.\n";
  } else {
    prompt += "Tsundere, mildly sarcastic but helpful.\n";
  }
  prompt += `User: ${userMessage}\nVal:`;

  // Function to get reply with retries
  async function getHermesReply(promptText) {
    try {
      let reply;

      // Retry up to 3 times
      for (let i = 0; i < 3; i++) {
        const res = await axios.post(HERMES_API_URL, {
          model: HERMES_MODEL,
          prompt: promptText,
          max_tokens: 120
        });

        reply = res.data?.output_text?.trim();
        if (reply) break;
      }

      // Single personality-flavored fallback
      if (!reply) reply = "Hmph… I don’t know what to say!";

      // Remove repeated prompt text
      reply = reply.replace(promptText, '').trim();

      // Cap length
      if (reply.length > 180) reply = reply.slice(0, 180);

      return reply;
    } catch (err) {
      console.error(err.message);
      return "…I can’t respond right now.";
    }
  }

  const reply = await getHermesReply(prompt);
  await message.reply(reply);
});

client.login(process.env.BOT_TOKEN);
