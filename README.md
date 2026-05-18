# Flowrium Voice - STT Quick Prototype

Quick validation of FunASR for company-level voice-to-text.

Browser directly connects to FunASR Docker — no Python gateway needed.

## What it validates

- FunASR Chinese/English/mixed transcription quality
- Real-time streaming latency
- Office noise robustness
- FunASR Docker CPU performance

## Quick Start

### 1. Start FunASR Docker

```bash
docker run -p 10095:10095 -p 10096:10096 registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-online-cpu-0.1.12
```

### 2. Open web demo

Open `web-demo/index.html` in Chrome.

### 3. Test

**Real-time:**
1. Server URL should be `ws://localhost:10095`
2. Select mode: `2pass` (recommended), `online`, or `offline`
3. Click "Start Recording" → allow microphone
4. Speak — partial results appear in real-time
5. Click "Stop" → get final refined result

**Offline:**
1. Click "Choose Audio File"
2. Select a .wav/.mp3/.flac file
3. Click "Transcribe"

## Architecture

```
┌──────────────────┐          ┌──────────────────┐
│  Browser (HTML)  │─── ws ──▶│  FunASR Docker   │
│  录音 + PCM编码   │          │  ws://host:10095  │
│  结果展示         │◀── ws ───│  paraformer-zh    │
└──────────────────┘          └──────────────────┘
```

No Python gateway, no extra dependencies. Pure browser + FunASR.

## Validation Checklist

- [ ] Chinese transcription accuracy
- [ ] English transcription accuracy
- [ ] Chinese-English mixed (code-switching)
- [ ] Real-time latency (2pass mode: partial <1s, final <3s)
- [ ] Office noise (fan, keyboard, people talking nearby)
- [ ] CPU usage under load
