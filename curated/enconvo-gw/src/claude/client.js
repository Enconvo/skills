import { spawn } from 'node:child_process';
import { log } from '../utils.js';
import { getOutboundDir } from '../files.js';

const DEFAULT_TIMEOUT_MS = 120_000; // 2 minutes

export class ClaudeCodeClient {
  constructor(options = {}) {
    this.timeout = options.timeout || DEFAULT_TIMEOUT_MS;
    this.defaultModel = options.model || null;
    this.systemPrompt = options.systemPrompt || null;
    this.allowedTools = options.allowedTools || null;
    this.disallowedTools = options.disallowedTools || null;
    this.workingDir = options.workingDir || process.env.HOME;
    this.permissionMode = options.permissionMode || 'plan';
  }

  /**
   * Send a prompt to claude CLI and return the response text.
   *
   * @param {string} inputText   - The user's message
   * @param {string} sessionId   - UUID session ID for conversation continuity
   * @param {object} opts        - Per-call option overrides
   * @returns {Promise<string>}  - Claude's response text
   */
  async call(inputText, sessionId, opts = {}) {
    const args = ['-p', inputText, '--output-format', 'text'];

    if (sessionId) {
      // First call: --session-id creates the session
      // Subsequent calls: --resume continues it
      args.push(opts.resume ? '--resume' : '--session-id', sessionId);
    }

    const model = opts.model || this.defaultModel;
    if (model) {
      args.push('--model', model);
    }

    const outboundDir = getOutboundDir();
    const deliverablePrompt = `IMPORTANT: When you create any deliverable files (images, videos, audio, PDFs, documents, archives, etc.), always save them to: ${outboundDir}\nThis directory is used to automatically deliver files back to the user's chat channel.`;
    const userSystemPrompt = opts.systemPrompt || this.systemPrompt;
    const systemPrompt = userSystemPrompt
      ? `${deliverablePrompt}\n\n${userSystemPrompt}`
      : deliverablePrompt;
    args.push('--system-prompt', systemPrompt);

    const permMode = opts.permissionMode || this.permissionMode;
    if (permMode) {
      args.push('--permission-mode', permMode);
    }

    const allowed = opts.allowedTools || this.allowedTools;
    if (allowed && allowed.length) {
      args.push('--allowedTools', ...allowed);
    }

    const disallowed = opts.disallowedTools || this.disallowedTools;
    if (disallowed && disallowed.length) {
      args.push('--disallowedTools', ...disallowed);
    }

    log('claude', `Spawning: claude -p ... session=${sessionId || 'new'} model=${model || 'default'} perm=${permMode || 'default'}`);

    return new Promise((resolve, reject) => {
      const proc = spawn('claude', args, {
        cwd: this.workingDir,
        // CRITICAL: unset CLAUDECODE to avoid "nested session" error
        env: { ...process.env, CLAUDECODE: '' },
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      let stdout = '';
      let stderr = '';
      let timedOut = false;

      const timer = setTimeout(() => {
        timedOut = true;
        proc.kill('SIGTERM');
        reject(new Error(`Claude CLI timed out after ${this.timeout / 1000}s`));
      }, this.timeout);

      proc.stdout.on('data', (chunk) => { stdout += chunk; });
      proc.stderr.on('data', (chunk) => { stderr += chunk; });

      proc.on('error', (err) => {
        clearTimeout(timer);
        reject(new Error(`Failed to spawn claude: ${err.message}`));
      });

      proc.on('close', (code) => {
        clearTimeout(timer);
        if (timedOut) return; // already rejected
        if (stderr.trim()) {
          log('claude', `stderr: ${stderr.trim().slice(0, 200)}`);
        }
        const output = stdout.trim();
        if (code === 0) {
          resolve(output || '(No response)');
        } else {
          const errMsg = stderr.trim() || `claude exited with code ${code}`;
          reject(new Error(errMsg));
        }
      });

      proc.stdin.end();
    });
  }
}
