## 1. FunASR Docker Service

- [x] 1.1 Install Docker Desktop (if not already installed) and verify `docker --version` works
- [x] 1.2 Pull FunASR CPU image: `docker pull registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-online-cpu-0.1.12`
- [x] 1.3 Start FunASR container with ports 10095 (streaming) and 10096 (offline) exposed
- [x] 1.4 Verify `ws://localhost:10095` and `ws://localhost:10096` accept WebSocket connections
- [x] 1.5 Record cold-start time (docker restart → WebSocket connectable)
- [x] 1.6 Record resource usage via `docker stats` (CPU, memory)

## 2. Demo - HTML Structure & Styling

- [x] 2.1 Create `verification-2-self/demo/index.html` with layout: connection panel, audio input panel, result panel, hotword panel
- [x] 2.2 Implement connection panel: WebSocket URL input, connect/disconnect buttons, connection status indicator
- [x] 2.3 Implement audio input panel: start/stop recording buttons, file upload input with format validation
- [x] 2.4 Implement result panel: scrollable transcription output area with partial/final visual differentiation
- [x] 2.5 Implement hotword panel: add/remove hotword UI, preset hotwords button, hotword tag list
- [x] 2.6 Implement action bar: clear results, copy all, export buttons

## 3. Demo - WebSocket Connection Logic

- [x] 3.1 Implement WebSocket connect/disconnect with configurable URL
- [x] 3.2 Handle connection state changes (connecting, connected, disconnected, error) and update UI
- [x] 3.3 Send ASR mode configuration (2pass/online/offline) on connection

## 4. Demo - Real-time Audio Recording

- [x] 4.1 Implement microphone access via `navigator.mediaDevices.getUserMedia`
- [x] 4.2 Implement AudioContext + ScriptProcessor/AudioWorklet to capture raw PCM samples
- [x] 4.3 Stream PCM chunks to WebSocket during active recording
- [x] 4.4 Handle recording start/stop with connection check

## 5. Demo - Audio File Upload

- [x] 5.1 Implement file input accepting wav/mp3/m4a formats
- [x] 5.2 Read and decode uploaded audio file to PCM using AudioContext
- [x] 5.3 Send decoded PCM data to WebSocket (chunked for streaming or whole for offline)
- [x] 5.4 Show error for unsupported formats

## 6. Demo - Transcription Result Handling

- [x] 6.1 Parse incoming WebSocket messages and distinguish partial vs final results
- [x] 6.2 Display partial results with visual indicator (trailing underscore or distinct color)
- [x] 6.3 Replace partial with final result when final message arrives
- [x] 6.4 Auto-scroll result area on new content

## 7. Demo - Hotword Management

- [x] 7.1 Implement add/remove hotword in local list
- [x] 7.2 Send hotword configuration to ASR engine via WebSocket `hotwords` field
- [x] 7.3 Implement preset school management hotwords (出勤率, 合格率, 平均分, 升学率, 及格率, 三年级, 二年级一班, 教务处, 后勤处, 德育处, 教学楼A栋, 张老师, 李校长, 导出报表, 月视图, 周视图)

## 8. Demo - Result Management

- [x] 8.1 Implement clear results (wipe displayed transcription)
- [x] 8.2 Implement copy all (copy final transcription text to clipboard)
- [x] 8.3 Implement export session record (download JSON/text file with timestamps, mode, hotwords, partial and final results)

## 9. Integration Verification

- [x] 9.1 Start FunASR Docker and Demo, connect via WebSocket
- [ ] 9.2 Test real-time recording: speak and verify partial + final results appear
- [ ] 9.3 Test file upload: upload a wav file and verify transcription result
- [ ] 9.4 Test mode switching: verify 2pass/online/offline produce expected behavior differences
- [ ] 9.5 Test hotwords: verify preset hotwords improve domain-specific term recognition
- [ ] 9.6 Test export: verify exported record contains all session data
