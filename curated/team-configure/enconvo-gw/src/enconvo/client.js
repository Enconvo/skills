import { log } from '../utils.js';

const TIMEOUT_MS = 90_000; // 90 seconds

export class EnConvoClient {
  constructor(baseUrl = 'http://localhost:54535') {
    this.baseUrl = baseUrl;
  }

  async call(model, inputText, sessionId) {
    const [ext, cmd] = model.split('/');
    const url = `${this.baseUrl}/${ext}/${cmd}`;

    log('enconvo', `POST ${ext}/${cmd} session=${sessionId}`);

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input_text: inputText, sessionId }),
      signal: AbortSignal.timeout(TIMEOUT_MS)
    });

    if (!res.ok) {
      const body = await res.text();
      throw new Error(`EnConvo ${res.status}: ${body}`);
    }

    const data = await res.json();
    return this.extractText(data);
  }

  extractText(data) {
    // Try messages[].content[].text
    if (Array.isArray(data?.messages)) {
      const texts = [];
      for (const msg of data.messages) {
        if (Array.isArray(msg.content)) {
          for (const block of msg.content) {
            if (block.text) texts.push(block.text);
          }
        } else if (typeof msg.content === 'string') {
          texts.push(msg.content);
        }
      }
      if (texts.length) return texts.join('\n\n');
    }

    // Try direct text field
    if (typeof data?.text === 'string') return data.text;
    if (typeof data?.content === 'string') return data.content;

    // Empty response from EnConvo (stale session)
    if (Array.isArray(data?.messages) && data.messages.every(m => Array.isArray(m.content) && m.content.length === 0)) {
      throw new Error('EnConvo returned empty response — the agent may need a restart in EnConvo app.');
    }

    // Fallback: stringify
    return JSON.stringify(data, null, 2);
  }
}
