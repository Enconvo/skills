import "dotenv/config";
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

const XAI_API_KEY = process.env.XAI_API_KEY;
if (!XAI_API_KEY || XAI_API_KEY === "your-xai-api-key-here") {
  console.error("Set XAI_API_KEY in .env file");
  process.exit(1);
}

wss.on("connection", (clientWs) => {
  console.log("Browser connected");

  const xaiWs = new WebSocket("wss://api.x.ai/v1/realtime", {
    headers: { Authorization: `Bearer ${XAI_API_KEY}` },
  });

  xaiWs.on("open", () => {
    console.log("Connected to xAI realtime API");

    // Configure session
    xaiWs.send(
      JSON.stringify({
        type: "session.update",
        session: {
          modalities: ["text", "audio"],
          voice: "Eve",
          instructions:
            "You are a friendly, conversational voice assistant. Keep responses concise and natural. You can help with questions, have casual conversations, and provide information.",
          turn_detection: {
            type: "server_vad",
            threshold: 0.5,
            silence_duration_ms: 800,
            prefix_padding_ms: 300,
          },
          input_audio: { format: { type: "audio/pcm", rate: 24000 } },
          output_audio: { format: { type: "audio/pcm", rate: 24000 } },
          input_audio_transcription: { model: "grok-2-audio" },
          tools: [{ type: "web_search" }],
        },
      })
    );

    clientWs.send(JSON.stringify({ type: "connected" }));
  });

  // Forward xAI events to browser
  xaiWs.on("message", (data) => {
    if (clientWs.readyState === WebSocket.OPEN) {
      clientWs.send(data.toString());
    }
  });

  // Forward browser audio to xAI
  clientWs.on("message", (data) => {
    if (xaiWs.readyState === WebSocket.OPEN) {
      xaiWs.send(data.toString());
    }
  });

  xaiWs.on("error", (err) => {
    console.error("xAI WS error:", err.message);
    clientWs.send(JSON.stringify({ type: "error", message: err.message }));
  });

  xaiWs.on("close", (code, reason) => {
    console.log("xAI disconnected:", code, reason.toString());
    if (clientWs.readyState === WebSocket.OPEN) clientWs.close();
  });

  clientWs.on("close", () => {
    console.log("Browser disconnected");
    if (xaiWs.readyState === WebSocket.OPEN) xaiWs.close();
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Voice chat running at http://localhost:${PORT}`);
});
