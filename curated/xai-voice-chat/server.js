import express from "express";
import { createServer } from "http";
import { WebSocketServer, WebSocket } from "ws";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

app.use(express.static(join(__dirname, "public")));
app.use(express.json());

// ── Fetch live model lists from provider APIs ──
async function fetchModels(provider, apiKey) {
  switch (provider) {
    case "xai": {
      const r = await fetch("https://api.x.ai/v1/models", {
        headers: { Authorization: `Bearer ${apiKey}` },
      });
      if (!r.ok) return null;
      const data = await r.json();
      return (data.data || [])
        .map((m) => m.id)
        .filter((id) => !id.includes("image") && !id.includes("embed") && !id.includes("audio"))
        .sort();
    }
    case "openai": {
      const r = await fetch("https://api.openai.com/v1/models", {
        headers: { Authorization: `Bearer ${apiKey}` },
      });
      if (!r.ok) return null;
      const data = await r.json();
      return (data.data || [])
        .map((m) => m.id)
        .filter((id) => {
          if (id.includes("embed") || id.includes("tts") || id.includes("whisper")) return false;
          if (id.includes("dall-e") || id.includes("moderation") || id.includes("davinci")) return false;
          if (id.includes("babbage") || id.includes("canary") || id.includes("search")) return false;
          return true;
        })
        .sort();
    }
    case "anthropic": {
      const r = await fetch("https://api.anthropic.com/v1/models", {
        headers: { "x-api-key": apiKey, "anthropic-version": "2023-06-01" },
      });
      if (!r.ok) {
        const test = await fetch("https://api.anthropic.com/v1/messages", {
          method: "POST",
          headers: { "x-api-key": apiKey, "anthropic-version": "2023-06-01", "content-type": "application/json" },
          body: JSON.stringify({ model: "claude-haiku-4-5-20251001", max_tokens: 1, messages: [{ role: "user", content: "." }] }),
        });
        if (test.status === 401) return null;
        return [
          "claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5-20251001",
          "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022",
          "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307",
        ];
      }
      const data = await r.json();
      return (data.data || []).map((m) => m.id).sort();
    }
    case "gemini": {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`);
      if (!r.ok) return null;
      const data = await r.json();
      return (data.models || [])
        .map((m) => m.name.replace("models/", ""))
        .filter((id) => {
          if (id.includes("embed") || id.includes("aqa") || id.includes("image")) return false;
          if (id.includes("vision") || id.includes("code")) return false;
          return true;
        })
        .sort();
    }
    default:
      return null;
  }
}

// ── Key validation endpoint ──
app.post("/api/validate-key", async (req, res) => {
  const { provider, apiKey } = req.body;
  if (!provider || !apiKey) return res.json({ valid: false, error: "Missing provider or key" });
  try {
    const models = await fetchModels(provider, apiKey);
    if (models === null) return res.json({ valid: false, error: "Invalid API key" });
    return res.json({ valid: true, models });
  } catch (err) {
    return res.json({ valid: false, error: err.message });
  }
});

// ── External LLM call ──
async function callExternalLLM(provider, apiKey, model, messages) {
  const systemMsg = "You are a friendly, conversational voice assistant. Keep responses concise and natural — they will be spoken aloud.";

  switch (provider) {
    case "openai": {
      const r = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({ model, messages: [{ role: "system", content: systemMsg }, ...messages] }),
      });
      const data = await r.json();
      if (data.error) throw new Error(data.error.message);
      return data.choices[0].message.content;
    }
    case "anthropic": {
      const r = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "x-api-key": apiKey, "anthropic-version": "2023-06-01", "Content-Type": "application/json" },
        body: JSON.stringify({ model, max_tokens: 1024, system: systemMsg, messages }),
      });
      const data = await r.json();
      if (data.error) throw new Error(data.error.message);
      return data.content[0].text;
    }
    case "gemini": {
      const geminiMessages = messages.map((m) => ({
        role: m.role === "assistant" ? "model" : "user",
        parts: [{ text: m.content }],
      }));
      const r = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ systemInstruction: { parts: [{ text: systemMsg }] }, contents: geminiMessages }),
        }
      );
      const data = await r.json();
      if (data.error) throw new Error(data.error.message);
      return data.candidates[0].content.parts[0].text;
    }
    case "xai": {
      // Grok custom model mode — use xAI chat API
      const r = await fetch("https://api.x.ai/v1/chat/completions", {
        method: "POST",
        headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({ model, messages: [{ role: "system", content: systemMsg }, ...messages] }),
      });
      const data = await r.json();
      if (data.error) throw new Error(data.error.message);
      return data.choices[0].message.content;
    }
    default:
      throw new Error("Unknown provider");
  }
}

// ── Streaming TTS via xAI WebSocket (wss://api.x.ai/v1/tts) ──
function streamTTS(text, voice, clientWs, setActiveTts, xaiKey) {
  return new Promise((resolve, reject) => {
    const params = new URLSearchParams({
      language: "auto",
      voice: voice,
      codec: "pcm",
      sample_rate: "24000",
    });

    const ttsWs = new WebSocket(`wss://api.x.ai/v1/tts?${params}`, {
      headers: { Authorization: `Bearer ${xaiKey}` },
    });

    if (setActiveTts) setActiveTts(ttsWs);

    ttsWs.on("open", () => {
      console.log("TTS WS: connected, streaming text...");
      // Send text in chunks for faster first-byte
      const chunkSize = 200;
      for (let i = 0; i < text.length; i += chunkSize) {
        ttsWs.send(JSON.stringify({
          type: "text.delta",
          delta: text.substring(i, i + chunkSize),
        }));
      }
      ttsWs.send(JSON.stringify({ type: "text.done" }));
    });

    ttsWs.on("message", (data) => {
      const msg = JSON.parse(data.toString());

      if (msg.type === "audio.delta" && clientWs.readyState === WebSocket.OPEN) {
        // Forward PCM audio chunk to browser
        clientWs.send(JSON.stringify({
          type: "response.output_audio.delta",
          delta: msg.delta,
        }));
      }

      if (msg.type === "audio.done") {
        console.log("TTS WS: audio complete");
        ttsWs.close();
        resolve();
      }

      if (msg.type === "error") {
        console.error("TTS WS error:", msg.message);
        ttsWs.close();
        reject(new Error(msg.message));
      }
    });

    ttsWs.on("error", (err) => {
      console.error("TTS WS connection error:", err.message);
      reject(err);
    });

    ttsWs.on("close", () => {
      resolve(); // in case audio.done wasn't received
    });
  });
}

// ── REST TTS fallback ──
async function restTTS(text, voice, clientWs, xaiKey) {
  console.log("REST TTS: speaking", text.substring(0, 50) + "...");
  const ttsResp = await fetch("https://api.x.ai/v1/tts", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${xaiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      text,
      voice_id: voice,
      language: "auto",
    }),
  });

  if (!ttsResp.ok) {
    throw new Error(`TTS failed: ${ttsResp.status} ${await ttsResp.text()}`);
  }

  const audioBuffer = await ttsResp.arrayBuffer();
  const base64Audio = Buffer.from(audioBuffer).toString("base64");
  clientWs.send(JSON.stringify({ type: "tts.audio", audio: base64Audio, format: "mp3" }));
  clientWs.send(JSON.stringify({ type: "tts.done" }));
}

// ── WebSocket handler ──
wss.on("connection", (clientWs) => {
  console.log("Browser connected");

  let llmProvider = "xai";
  let llmApiKey = "";
  let llmModel = "";
  let xaiApiKey = "";
  let selectedVoice = "eve";
  let ttsMode = "realtime";
  let grokMode = "allinone"; // "allinone" or "custom"
  let conversationHistory = [];
  let xaiWs = null;
  let activeTtsWs = null;

  function connectXai() {
    if (!xaiApiKey) {
      clientWs.send(JSON.stringify({ type: "error", message: "xAI API key required. Set it in Settings." }));
      return;
    }
    xaiWs = new WebSocket("wss://api.x.ai/v1/realtime", ["realtime", "openai-beta.realtime-v1"], {
      headers: { Authorization: `Bearer ${xaiApiKey}` },
    });

    xaiWs.on("open", () => {
      console.log("Connected to xAI realtime API");
    });

    let sessionConfigured = false;

    xaiWs.on("message", async (data) => {
      if (clientWs.readyState !== WebSocket.OPEN) return;
      const msg = JSON.parse(data.toString());

      // Configure session on conversation.created
      if (msg.type === "conversation.created" && !sessionConfigured) {
        sessionConfigured = true;
        const isExternalLLM = llmProvider !== "xai" || grokMode === "custom";

        xaiWs.send(JSON.stringify({
          type: "session.update",
          session: {
            voice: selectedVoice.charAt(0).toUpperCase() + selectedVoice.slice(1),
            instructions: isExternalLLM
              ? "Transcribe user audio. Do not generate responses."
              : "You are a friendly, conversational voice assistant. Keep responses concise and natural.",
            turn_detection: {
              type: "server_vad",
              threshold: 0.5,
              silence_duration_ms: 800,
              prefix_padding_ms: 300,
            },
            audio: {
              input: { format: { type: "audio/pcm", rate: 24000 } },
              output: { format: { type: "audio/pcm", rate: 24000 } },
            },
            input_audio_transcription: { model: "grok-2-audio" },
            tools: isExternalLLM ? [] : [{ type: "web_search" }],
          },
        }));
        return;
      }

      // Session ready
      if (msg.type === "session.updated") {
        clientWs.send(JSON.stringify({ type: "connected" }));
        return;
      }

      // ── External LLM mode ──
      if (llmProvider !== "xai" || grokMode === "custom") {
        // Cancel ALL Grok auto-responses immediately
        if (msg.type === "response.created") {
          xaiWs.send(JSON.stringify({ type: "response.cancel" }));
        }

        // WHITELIST: only forward these specific events to client.
        // Everything else from Grok (audio, transcript, responses) is dropped.
        const allowedEvents = [
          "input_audio_buffer.speech_started",
          "input_audio_buffer.speech_stopped",
          "input_audio_buffer.committed",
          "conversation.item.input_audio_transcription.completed",
        ];

        if (!allowedEvents.includes(msg.type)) {
          return; // drop everything else
        }

        // Forward VAD events directly
        if (msg.type === "input_audio_buffer.speech_started" ||
            msg.type === "input_audio_buffer.speech_stopped") {
          clientWs.send(data.toString());
          return;
        }

        // Transcription ready → call external LLM → TTS
        if (msg.type === "conversation.item.input_audio_transcription.completed") {
          const userText = msg.transcript?.trim();
          if (!userText) return;

          clientWs.send(data.toString());
          conversationHistory.push({ role: "user", content: userText });
          clientWs.send(JSON.stringify({ type: "llm.thinking" }));

          try {
            const llmResponse = await callExternalLLM(llmProvider, llmApiKey, llmModel, conversationHistory);
            conversationHistory.push({ role: "assistant", content: llmResponse });

            clientWs.send(JSON.stringify({ type: "llm.response", text: llmResponse }));

            // TTS: use selected mode
            if (ttsMode === "realtime") {
              // Streaming WebSocket TTS — sends PCM chunks as response.output_audio.delta
              clientWs.send(JSON.stringify({ type: "tts.speaking" }));
              await streamTTS(llmResponse, selectedVoice, clientWs, (ws) => { activeTtsWs = ws; }, xaiApiKey);
              clientWs.send(JSON.stringify({ type: "tts.done" }));
            } else {
              // REST TTS — sends full MP3
              await restTTS(llmResponse, selectedVoice, clientWs, xaiApiKey);
            }
          } catch (err) {
            console.error("LLM/TTS error:", err.message);
            clientWs.send(JSON.stringify({ type: "error", message: err.message }));
          }
          return;
        }
      }

      // Forward everything else to client (Grok all-in-one mode)
      clientWs.send(data.toString());
    });

    xaiWs.on("error", (err) => {
      console.error("xAI WS error:", err.message);
      if (clientWs.readyState === WebSocket.OPEN) {
        clientWs.send(JSON.stringify({ type: "error", message: err.message }));
      }
    });

    xaiWs.on("close", (code, reason) => {
      console.log("xAI disconnected:", code, reason.toString());
      if (clientWs.readyState === WebSocket.OPEN) clientWs.close();
    });
  }

  clientWs.on("message", (data) => {
    const msg = JSON.parse(data.toString());

    // Handle stop request from client
    if (msg.type === "stop") {
      console.log("Client requested stop");
      if (activeTtsWs && activeTtsWs.readyState === WebSocket.OPEN) {
        activeTtsWs.close();
        activeTtsWs = null;
      }
      // Also cancel any Grok response in progress
      if (xaiWs && xaiWs.readyState === WebSocket.OPEN) {
        xaiWs.send(JSON.stringify({ type: "response.cancel" }));
      }
      return;
    }

    // Hot-swap LLM provider/model mid-session (no reconnect)
    if (msg.type === "config.update") {
      if (msg.provider != null) llmProvider = msg.provider;
      if (msg.apiKey != null) llmApiKey = msg.apiKey;
      if (msg.model != null) llmModel = msg.model;
      if (msg.ttsMode != null) ttsMode = msg.ttsMode;
      if (msg.grokMode != null) grokMode = msg.grokMode;
      if (msg.voice) selectedVoice = msg.voice.toLowerCase();
      conversationHistory = [];
      console.log(`Hot-swap: LLM=${llmProvider}/${llmModel} key=${llmApiKey ? llmApiKey.substring(0, 8) + "..." : "MISSING"} tts=${ttsMode}`);
      clientWs.send(JSON.stringify({ type: "config.updated" }));
      return;
    }

    // Initial connection config (connects xAI Realtime)
    if (msg.type === "config") {
      llmProvider = msg.provider || "xai";
      llmApiKey = msg.apiKey || "";
      llmModel = msg.model || "";
      xaiApiKey = msg.xaiKey || "";
      selectedVoice = (msg.voice || "eve").toLowerCase();
      ttsMode = msg.ttsMode || "realtime";
      grokMode = msg.grokMode || "allinone";
      conversationHistory = [];
      console.log(`Config: LLM=${llmProvider}/${llmModel} voice=${selectedVoice} tts=${ttsMode} grokMode=${grokMode}`);
      connectXai();
      return;
    }

    if (xaiWs && xaiWs.readyState === WebSocket.OPEN) {
      xaiWs.send(data.toString());
    }
  });

  clientWs.on("close", () => {
    console.log("Browser disconnected");
    if (xaiWs && xaiWs.readyState === WebSocket.OPEN) xaiWs.close();
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Voice chat running at http://localhost:${PORT}`);
});
