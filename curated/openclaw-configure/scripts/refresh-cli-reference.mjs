#!/usr/bin/env node
// Regenerate only the two CLI reference files, using help from the installed CLI.
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const skillDir = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const extras = [];
for (let i = 2; i < process.argv.length; i++) {
  if (process.argv[i] !== '--extra' || !/^[a-z][a-z0-9-]*$/.test(process.argv[i + 1] ?? '')) {
    throw new Error('Usage: node refresh-cli-reference.mjs [--extra <plugin-command>]');
  }
  extras.push(process.argv[++i]);
}

function cli(args) {
  return execFileSync('openclaw', args, {
    encoding: 'utf8', timeout: 60_000, maxBuffer: 2 * 1024 * 1024,
    env: { ...process.env, NO_COLOR: '1', TERM: 'dumb' },
    stdio: ['ignore', 'pipe', 'pipe'],
  }).replace(/\x1b\[[0-9;]*[A-Za-z]/g, '').trim();
}

function help(args) {
  const result = cli([...args, '--help']);
  const offset = result.indexOf('Usage: openclaw');
  if (offset < 0) throw new Error(`No CLI usage in help for ${args.join(' ') || 'root'}`);
  return result.slice(offset);
}

function commandBlock(content) {
  const lines = content.split('\n');
  const start = lines.indexOf('Commands:');
  if (start < 0) return '';
  const block = [];
  for (const line of lines.slice(start + 1)) {
    if (line && !/^\s/.test(line)) break;
    block.push(line);
  }
  return block.join('\n').trimEnd();
}

const version = cli(['--version']);
const root = help([]);
const advertised = [...commandBlock(root).matchAll(/^  ([a-z][a-z0-9-]*)(?:\s|$)/gm)].map(m => m[1]);
if (advertised.length === 0) throw new Error('Top-level command discovery returned no commands');
const commands = [...new Set([...advertised, ...extras])].sort();
const oldSummary = readFileSync(resolve(skillDir, 'commands.md'), 'utf8');
const oldCommands = [...oldSummary.matchAll(/^## `([^`]+)`$/gm)].map(m => m[1]);
const pages = [];
for (const command of commands) {
  pages.push([command, help([command])]);
  process.stdout.write(`Captured ${command} (${pages.length}/${commands.length})\n`);
}
if (cli(['--version']) !== version) throw new Error('OpenClaw changed during capture; references were not written');

const date = new Date().toLocaleDateString('en-CA');
const stamp = `Generated from \`${version}\` on ${date}.`;
const supplemental = extras.length ? ` Explicit plugin-command help: ${extras.map(c => `\`${c}\``).join(', ')}.` : '';
let full = `# OpenClaw CLI Reference\n\n${stamp} Help for ${commands.length} command entry points, plus root help.${supplemental} Nested command names are listed; run their own \`--help\` for leaf options.\n\n`;
full += `## \`openclaw\`\n\n\`\`\`text\n${root}\n\`\`\`\n`;
let condensed = `# OpenClaw CLI Commands (Condensed Reference)\n\n${stamp} Usage and first-level subcommands; see \`cli-reference.md\` for entry-point options.${supplemental}\n\n`;
condensed += `## Top-Level Commands\n\n\`\`\`text\n${commandBlock(root)}\n\`\`\`\n`;
for (const [command, content] of pages) {
  full += `\n## \`openclaw ${command}\`\n\n\`\`\`text\n${content}\n\`\`\`\n`;
  const usage = content.match(/^Usage:.*$/m)[0];
  const nested = commandBlock(content);
  condensed += `\n## \`${command}\`\n\n\`\`\`text\n${usage}${nested ? `\n\n${nested}` : ''}\n\`\`\`\n`;
}

// These are mechanically generated references; preserve the hand-authored skill.
writeFileSync(resolve(skillDir, 'cli-reference.md'), full);
writeFileSync(resolve(skillDir, 'commands.md'), condensed);
process.stdout.write(JSON.stringify({
  version, date, entryPoints: commands.length,
  added: commands.filter(c => !oldCommands.includes(c)),
  removed: oldCommands.filter(c => !commands.includes(c)),
  files: ['commands.md', 'cli-reference.md'],
}, null, 2) + '\n');
