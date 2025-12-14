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

// Cooldown map to prevent spam
const cooldown = new Map();

// Hermes free endpoint
const HERMES_API_URL = 'https://hermes.ai.unturf.com/v1/completions';
const HERMES_MODEL = 'adamo1139/Hermes-3-Llama-3.1-8B-FP8-Dynamic';

client.once('ready', () => {
  console.log(`Val online as ${client.user.tag}`);
});

client.on('messageCreate', async (message) => {
  if (message.author.bot) return;

  // Only reply when Val is mentioned
  const valRegex = /\bval\b/i;
  if (!valRegex.test(message.content)) return;

  // Cooldown per user (4 seconds)
  const now = Date.now();
  const last = cooldown.get(message.author.id) || 0;
  if (now - last < 4000) return;
  cooldown.set(message.author.id, now);

  // Build prompt for Hermes
  let prompt = "You are Val, a Discord user-like AI. Reply naturally like a real person.\n";

  if (message.author.id === SOFT_USER) {
    prompt += "You are soft, shy, gentle, slightly hesitant with this user.\n";
  } else if (message.author.id === MEAN_USER) {
    prompt += "You are blunt, dismissive, a bit mean but still helpful with this user.\n";
  } else {
    prompt += "You are tsundere — mildly sarcastic but helpful.\n";
  }

  prompt += `User: ${message.content}\nVal:`;

  try {
    const response = await axios.post(HERMES_API_URL, {
      model: HERMES_MODEL,
      prompt,
      max_tokens: 60
    });

    let reply = response.data?.output_text || "…I’m not sure…";

    // Remove repeated prompt text
    reply = reply.replace(prompt, '').trim();

    // Cap length to prevent overflow
    if (reply.length > 180) reply = reply.slice(0, 180);

    await message.reply(reply);
  } catch (err) {
    console.error(err.message);
    message.reply("…I can’t respond right now.");
  }
});

client.login(process.env.BOT_TOKEN);
