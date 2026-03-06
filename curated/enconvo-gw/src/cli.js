import { Command } from 'commander';
import { loadConfig, saveConfig, getConfigValue, setConfigValue } from './config.js';
import { startGateway, stopGateway, gatewayStatus } from './gateway.js';
import { listPairings, approvePairing } from './pairing/pairing.js';

export function createCLI() {
  const program = new Command();
  program
    .name('enconvo-gw')
    .description('Direct Telegram & Discord ↔ EnConvo Gateway')
    .version('1.0.0');

  // --- gateway ---
  const gw = program.command('gateway')
    .description('Start the gateway (foreground)')
    .option('--force', 'Kill existing gateway first')
    .action((opts) => {
      // Only start if no subcommand was matched
      if (!opts._subcommand) startGateway(opts);
    });

  // Override action to detect subcommands
  gw.hook('preAction', (thisCommand, actionCommand) => {
    if (actionCommand !== thisCommand) thisCommand.setOptionValue('_subcommand', true);
  });

  gw.command('stop')
    .description('Stop the running gateway')
    .action(() => stopGateway());

  gw.command('status')
    .description('Show gateway status')
    .action(() => gatewayStatus());

  // --- channels ---
  const channels = program.command('channels').description('Manage channel accounts');

  channels.command('add')
    .description('Add a channel account')
    .requiredOption('--channel <channel>', 'Channel type (telegram, discord)')
    .requiredOption('--account <id>', 'Account identifier')
    .requiredOption('--token <token>', 'Bot token')
    .requiredOption('--agent <agentId>', 'Agent to route to')
    .option('--dm-policy <policy>', 'DM policy: open, allowlist, pairing', 'pairing')
    .option('--group-policy <policy>', 'Group policy: open', 'open')
    .action((opts) => {
      const config = loadConfig();
      if (!config.channels[opts.channel]) {
        config.channels[opts.channel] = { accounts: {} };
      }
      config.channels[opts.channel].accounts[opts.account] = {
        enabled: true,
        botToken: opts.token,
        agentId: opts.agent,
        dmPolicy: opts.dmPolicy,
        groupPolicy: opts.groupPolicy,
        allowFrom: []
      };
      saveConfig(config);
      console.log(`Added ${opts.channel} account: ${opts.account} → agent ${opts.agent}`);
    });

  channels.command('remove')
    .description('Remove a channel account')
    .requiredOption('--channel <channel>', 'Channel type')
    .requiredOption('--account <id>', 'Account identifier')
    .action((opts) => {
      const config = loadConfig();
      if (config.channels[opts.channel]?.accounts[opts.account]) {
        delete config.channels[opts.channel].accounts[opts.account];
        saveConfig(config);
        console.log(`Removed ${opts.channel} account: ${opts.account}`);
      } else {
        console.log(`Account not found: ${opts.channel}/${opts.account}`);
      }
    });

  channels.command('list')
    .description('List all channel accounts')
    .action(() => {
      const config = loadConfig();
      for (const [channelType, channelConfig] of Object.entries(config.channels)) {
        const accounts = channelConfig.accounts || {};
        for (const [id, acc] of Object.entries(accounts)) {
          const agent = config.agents[acc.agentId];
          const status = acc.enabled ? '✓' : '✗';
          console.log(`  ${status} ${channelType}/${id} → ${acc.agentId} (${agent?.name || 'unknown agent'}) [dm:${acc.dmPolicy}]`);
        }
      }
    });

  channels.command('status')
    .description('Probe live bot connections')
    .action(async () => {
      const config = loadConfig();

      // Telegram
      const tgAccounts = config.channels?.telegram?.accounts || {};
      if (Object.keys(tgAccounts).length) {
        console.log('Telegram:');
        const { Bot } = await import('grammy');
        for (const [id, acc] of Object.entries(tgAccounts)) {
          if (!acc.enabled) {
            console.log(`  ✗ ${id}: disabled`);
            continue;
          }
          try {
            const bot = new Bot(acc.botToken);
            const me = await bot.api.getMe();
            console.log(`  ✓ ${id}: @${me.username} (${me.first_name})`);
          } catch (err) {
            console.log(`  ✗ ${id}: ${err.message}`);
          }
        }
      }

      // Discord
      const dcAccounts = config.channels?.discord?.accounts || {};
      if (Object.keys(dcAccounts).length) {
        console.log('Discord:');
        const { Client, GatewayIntentBits } = await import('discord.js');
        for (const [id, acc] of Object.entries(dcAccounts)) {
          if (!acc.enabled) {
            console.log(`  ✗ ${id}: disabled`);
            continue;
          }
          try {
            const client = new Client({ intents: [GatewayIntentBits.Guilds] });
            const user = await new Promise((resolve, reject) => {
              client.once('clientReady', () => resolve(client.user));
              client.login(acc.botToken).catch(reject);
            });
            console.log(`  ✓ ${id}: @${user.tag}`);
            client.destroy();
          } catch (err) {
            console.log(`  ✗ ${id}: ${err.message}`);
          }
        }
      }
    });

  // --- agents ---
  const agents = program.command('agents').description('Manage agents');

  agents.command('add')
    .description('Add an agent')
    .requiredOption('--id <id>', 'Agent identifier')
    .requiredOption('--name <name>', 'Display name')
    .option('--model <model>', 'EnConvo model path (ext/cmd) or claude model alias')
    .option('--type <type>', 'Agent type: enconvo (default) or claude-code', 'enconvo')
    .option('--system-prompt <prompt>', 'System prompt (claude-code only)')
    .option('--permission-mode <mode>', 'Permission mode: plan, auto, bypassPermissions (claude-code only)', 'plan')
    .option('--allowed-tools <tools...>', 'Allowed tools, space-separated (claude-code only)')
    .option('--working-dir <dir>', 'Working directory for claude (claude-code only)')
    .option('--timeout <ms>', 'Timeout in milliseconds (claude-code only)')
    .action((opts) => {
      const config = loadConfig();
      const agent = { name: opts.name, type: opts.type };
      if (opts.model) agent.model = opts.model;
      if (opts.type === 'claude-code') {
        if (opts.systemPrompt) agent.systemPrompt = opts.systemPrompt;
        if (opts.permissionMode) agent.permissionMode = opts.permissionMode;
        if (opts.allowedTools) agent.allowedTools = opts.allowedTools;
        if (opts.workingDir) agent.workingDir = opts.workingDir;
        if (opts.timeout) agent.timeout = parseInt(opts.timeout, 10);
      }
      config.agents[opts.id] = agent;
      saveConfig(config);
      const target = opts.type === 'claude-code'
        ? `claude-code (model=${opts.model || 'default'}, permission=${opts.permissionMode || 'plan'})`
        : opts.model;
      console.log(`Added ${opts.type} agent: ${opts.id} (${opts.name}) → ${target}`);
    });

  agents.command('list')
    .description('List configured agents')
    .action(() => {
      const config = loadConfig();
      for (const [id, agent] of Object.entries(config.agents)) {
        const type = agent.type || 'enconvo';
        const target = type === 'claude-code'
          ? `claude-code model=${agent.model || 'default'} perm=${agent.permissionMode || 'plan'}`
          : (agent.model || '(no model)');
        console.log(`  ${id}: ${agent.name} [${type}] → ${target}`);
      }
    });

  agents.command('remove')
    .description('Remove an agent')
    .requiredOption('--id <id>', 'Agent identifier')
    .action((opts) => {
      const config = loadConfig();
      if (config.agents[opts.id]) {
        delete config.agents[opts.id];
        saveConfig(config);
        console.log(`Removed agent: ${opts.id}`);
      } else {
        console.log(`Agent not found: ${opts.id}`);
      }
    });

  // --- pairing ---
  const pairing = program.command('pairing').description('Manage pairing requests');

  pairing.command('list')
    .description('List pending pairing requests')
    .argument('[channel]', 'Channel type filter')
    .action((channel) => {
      const config = loadConfig();
      const channelTypes = channel ? [channel] : Object.keys(config.channels);
      let found = false;
      for (const ct of channelTypes) {
        const accounts = config.channels[ct]?.accounts || {};
        for (const accountId of Object.keys(accounts)) {
          const pairings = listPairings(accountId);
          if (pairings.length) {
            found = true;
            console.log(`\n${ct}/${accountId}:`);
            for (const p of pairings) {
              const age = Math.round((Date.now() - p.createdAt) / 60000);
              console.log(`  ${p.code}  ${p.senderName} (${p.senderId})  ${age}m ago`);
            }
          }
        }
      }
      if (!found) console.log('No pending pairing requests.');
    });

  pairing.command('approve')
    .description('Approve a pairing request')
    .argument('<channel>', 'Channel type')
    .argument('<code>', 'Pairing code')
    .action((channel, code) => {
      const config = loadConfig();
      const accounts = config.channels[channel]?.accounts || {};
      for (const accountId of Object.keys(accounts)) {
        const result = approvePairing(accountId, code);
        if (result) {
          console.log(`Approved ${result.senderName} (${result.senderId}) for ${channel}/${accountId}`);
          return;
        }
      }
      console.log(`Pairing code not found: ${code}`);
    });

  // --- config ---
  const configCmd = program.command('config').description('Read/write config values');

  configCmd.command('get')
    .description('Read a config value')
    .argument('<path>', 'Dot-separated config path')
    .action((path) => {
      const val = getConfigValue(path);
      if (val === undefined) {
        console.log('(not set)');
      } else if (typeof val === 'object') {
        console.log(JSON.stringify(val, null, 2));
      } else {
        console.log(val);
      }
    });

  configCmd.command('set')
    .description('Set a config value')
    .argument('<path>', 'Dot-separated config path')
    .argument('<value>', 'Value to set')
    .action((path, value) => {
      setConfigValue(path, value);
      console.log(`Set ${path} = ${value}`);
    });

  return program;
}
