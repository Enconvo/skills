#!/usr/bin/env python3
"""
Video Captioner — Generate visual captions/descriptions from video frames.

Uses Enconvo's MLX VLM runtime (MCP server) as primary backend,
with standalone mlx-vlm as fallback.

Usage:
    python3 video_captioner.py <video_path> [options]

Options:
    --model MODEL       HuggingFace model ID (default: mlx-community/Qwen2.5-VL-3B-Instruct-8bit)
    --interval N        Extract 1 frame every N seconds (default: 3)
    --max-frames N      Maximum number of frames to process (default: 60)
    --prompt TEXT       Custom prompt for frame description
    --language LANG     Output language: english/chinese (default: english)
    --output FILE       Output SRT file path (default: <video>_captions.srt)
    --max-tokens N      Max tokens per frame description (default: 100)
    --backend BACKEND   Force backend: enconvo/standalone/auto (default: auto)
    --merge-window N    Merge similar consecutive captions within N seconds (default: 0, disabled)
    
Output:
    SRT subtitle file with visual descriptions synced to video timestamps.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", video_path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def extract_frames(video_path: str, interval: int, max_frames: int, output_dir: str) -> list:
    """Extract frames from video at specified interval."""
    duration = get_video_duration(video_path)
    timestamps = []
    t = 0.0
    while t < duration and len(timestamps) < max_frames:
        timestamps.append(t)
        t += interval
    
    frames = []
    for i, ts in enumerate(timestamps):
        frame_path = os.path.join(output_dir, f"frame_{i:04d}.jpg")
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(ts), "-i", video_path,
             "-frames:v", "1", "-q:v", "2", frame_path],
            capture_output=True
        )
        if os.path.exists(frame_path) and os.path.getsize(frame_path) > 0:
            frames.append({"path": frame_path, "timestamp": ts, "index": i})
    
    return frames


def format_timestamp(seconds: float) -> str:
    """Format seconds to SRT timestamp format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def try_enconvo_backend(model_id: str, frames: list, prompt: str, max_tokens: int) -> list | None:
    """Try using Enconvo's MLX VLM MCP server."""
    try:
        # Check if Enconvo MLX VLM server is available
        mlx_manage_path = os.path.expanduser("~/.config/enconvo/extension/mlx_manage")
        if not os.path.exists(mlx_manage_path):
            print("  Enconvo MLX VLM not found, skipping...", file=sys.stderr)
            return None
        
        # Use the MCP server via subprocess (STDIO transport)
        server_script = os.path.join(mlx_manage_path, "python", "mlx_vlm_server.py")
        if not os.path.exists(server_script):
            print("  MLX VLM server script not found, skipping...", file=sys.stderr)
            return None
        
        venv_python = os.path.join(mlx_manage_path, ".venv", "bin", "python3")
        if not os.path.exists(venv_python):
            print("  Enconvo MLX VLM venv not found, skipping...", file=sys.stderr)
            return None
        
        # Start MCP server
        print(f"  Starting Enconvo MLX VLM MCP server...", file=sys.stderr)
        proc = subprocess.Popen(
            [venv_python, server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.join(mlx_manage_path, "python")
        )
        
        request_id = 0
        
        def send_request(method: str, params: dict) -> dict:
            nonlocal request_id
            request_id += 1
            msg = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params
            }
            line = json.dumps(msg) + "\n"
            proc.stdin.write(line.encode())
            proc.stdin.flush()
            
            # Read response
            while True:
                resp_line = proc.stdout.readline().decode().strip()
                if not resp_line:
                    continue
                resp = json.loads(resp_line)
                if "id" in resp and resp["id"] == request_id:
                    return resp
        
        # Initialize MCP
        init_resp = send_request("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "video-captioner", "version": "1.0.0"}
        })
        
        # Send initialized notification
        notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        proc.stdin.write((json.dumps(notif) + "\n").encode())
        proc.stdin.flush()
        
        results = []
        total = len(frames)
        
        for i, frame in enumerate(frames):
            print(f"  [{i+1}/{total}] Processing frame at {frame['timestamp']:.1f}s...", file=sys.stderr)
            
            try:
                resp = send_request("tools/call", {
                    "name": "generate",
                    "arguments": {
                        "hf_model_id": model_id,
                        "prompt": prompt,
                        "image": [frame["path"]],
                        "max_tokens": max_tokens,
                        "temperature": 0.1
                    }
                })
                
                if "result" in resp:
                    content = resp["result"]
                    # Handle structured content or text content
                    if isinstance(content, dict):
                        if "structuredContent" in content:
                            text = content["structuredContent"].get("text", "")
                        elif "content" in content:
                            # MCP tool result format
                            for item in content.get("content", []):
                                if item.get("type") == "text":
                                    text = item.get("text", "")
                                    break
                            else:
                                text = str(content)
                        elif "text" in content:
                            text = content["text"]
                        else:
                            text = str(content)
                    else:
                        text = str(content)
                    
                    results.append({
                        "timestamp": frame["timestamp"],
                        "text": text.strip()
                    })
                elif "error" in resp:
                    print(f"  Error on frame {i}: {resp['error'].get('message', 'Unknown')}", file=sys.stderr)
                    results.append({
                        "timestamp": frame["timestamp"],
                        "text": f"[Error: {resp['error'].get('message', 'Unknown')}]"
                    })
            except Exception as e:
                print(f"  Error processing frame {i}: {e}", file=sys.stderr)
                results.append({
                    "timestamp": frame["timestamp"],
                    "text": f"[Error: {e}]"
                })
        
        # Cleanup
        proc.stdin.close()
        proc.terminate()
        proc.wait(timeout=5)
        
        return results
        
    except Exception as e:
        print(f"  Enconvo backend failed: {e}", file=sys.stderr)
        return None


def try_standalone_backend(model_id: str, frames: list, prompt: str, max_tokens: int) -> list | None:
    """Try using standalone mlx-vlm directly."""
    try:
        # Check if mlx-vlm is available
        try:
            import mlx_vlm
            print("  Using standalone mlx-vlm...", file=sys.stderr)
        except ImportError:
            print("  mlx-vlm not installed. Install: pip install mlx-vlm", file=sys.stderr)
            return None
        
        from mlx_vlm import load, generate
        from mlx_vlm.prompt_utils import apply_chat_template
        
        print(f"  Loading model {model_id}...", file=sys.stderr)
        model, processor = load(model_id)
        
        config = model.config
        results = []
        total = len(frames)
        
        for i, frame in enumerate(frames):
            print(f"  [{i+1}/{total}] Processing frame at {frame['timestamp']:.1f}s...", file=sys.stderr)
            
            formatted_prompt = apply_chat_template(
                processor, config,
                prompt=prompt,
                num_images=1,
            )
            
            result = generate(
                model, processor,
                prompt=formatted_prompt,
                image=[frame["path"]],
                max_tokens=max_tokens,
                temperature=0.1,
                verbose=False,
            )
            
            text = result.text if hasattr(result, 'text') else str(result)
            results.append({
                "timestamp": frame["timestamp"],
                "text": text.strip()
            })
        
        return results
        
    except Exception as e:
        print(f"  Standalone backend failed: {e}", file=sys.stderr)
        return None


def merge_similar_captions(results: list, interval: int, merge_window: int) -> list:
    """Merge consecutive captions with identical or very similar text."""
    if not results or merge_window <= 0:
        return results
    
    merged = [results[0].copy()]
    for i in range(1, len(results)):
        curr = results[i]
        prev = merged[-1]
        
        # If same text and within merge window
        if curr["text"] == prev["text"] and (curr["timestamp"] - prev["timestamp"]) <= merge_window:
            prev["end_timestamp"] = curr["timestamp"] + interval
        else:
            merged.append(curr.copy())
    
    return merged


def write_srt(results: list, output_path: str, interval: int):
    """Write results to SRT file."""
    with open(output_path, "w", encoding="utf-8") as f:
        for i, r in enumerate(results):
            start = r["timestamp"]
            end = r.get("end_timestamp", start + interval)
            
            f.write(f"{i+1}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            
            # Wrap long lines
            text = r["text"]
            if len(text) > 40:
                mid = len(text) // 2
                best = mid
                for j in range(max(0, mid-10), min(len(text), mid+10)):
                    if text[j] in '，。、；：！？,. ':
                        best = j + 1
                        break
                text = text[:best].strip() + "\n" + text[best:].strip()
            
            f.write(f"{text}\n\n")


def main():
    parser = argparse.ArgumentParser(description="Generate visual captions from video frames")
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("--model", default="mlx-community/Qwen2.5-VL-3B-Instruct-8bit",
                       help="HuggingFace model ID")
    parser.add_argument("--interval", type=int, default=3,
                       help="Extract 1 frame every N seconds")
    parser.add_argument("--max-frames", type=int, default=60,
                       help="Maximum frames to process")
    parser.add_argument("--prompt", default=None,
                       help="Custom prompt for frame description")
    parser.add_argument("--language", default="english", choices=["english", "chinese"],
                       help="Output language")
    parser.add_argument("--output", default=None, help="Output SRT path")
    parser.add_argument("--max-tokens", type=int, default=100,
                       help="Max tokens per description")
    parser.add_argument("--backend", default="auto", choices=["enconvo", "standalone", "auto"],
                       help="Backend: enconvo (MCP), standalone (mlx-vlm), auto")
    parser.add_argument("--merge-window", type=int, default=0,
                       help="Merge similar captions within N seconds (0=disabled)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.video):
        print(f"Error: Video not found: {args.video}", file=sys.stderr)
        sys.exit(1)
    
    # Default prompt
    if args.prompt is None:
        if args.language == "chinese":
            args.prompt = "用简洁的中文描述这个画面中正在发生什么。只描述关键动作和内容，不超过30个字。"
        else:
            args.prompt = "Describe what is happening in this frame in one concise sentence. Focus on the key action or content."
    
    # Output path
    if args.output is None:
        base = os.path.splitext(args.video)[0]
        args.output = f"{base}_captions.srt"
    
    duration = get_video_duration(args.video)
    print(f"Video: {args.video} ({duration:.1f}s)", file=sys.stderr)
    print(f"Model: {args.model}", file=sys.stderr)
    print(f"Interval: {args.interval}s, Max frames: {args.max_frames}", file=sys.stderr)
    
    # Extract frames
    with tempfile.TemporaryDirectory(prefix="vidcap_") as tmpdir:
        print("Extracting frames...", file=sys.stderr)
        frames = extract_frames(args.video, args.interval, args.max_frames, tmpdir)
        print(f"Extracted {len(frames)} frames", file=sys.stderr)
        
        if not frames:
            print("Error: No frames extracted", file=sys.stderr)
            sys.exit(1)
        
        # Process frames with VLM
        results = None
        
        if args.backend in ("enconvo", "auto"):
            print("Trying Enconvo MLX VLM backend...", file=sys.stderr)
            results = try_enconvo_backend(args.model, frames, args.prompt, args.max_tokens)
        
        if results is None and args.backend in ("standalone", "auto"):
            print("Trying standalone mlx-vlm backend...", file=sys.stderr)
            results = try_standalone_backend(args.model, frames, args.prompt, args.max_tokens)
        
        if results is None:
            print("Error: All backends failed", file=sys.stderr)
            sys.exit(1)
    
    # Merge similar consecutive captions
    if args.merge_window > 0:
        before = len(results)
        results = merge_similar_captions(results, args.interval, args.merge_window)
        print(f"Merged {before} → {len(results)} captions", file=sys.stderr)
    
    # Write SRT
    write_srt(results, args.output, args.interval)
    print(f"Captions saved: {args.output}", file=sys.stderr)
    print(f"Total: {len(results)} captions", file=sys.stderr)


if __name__ == "__main__":
    main()
