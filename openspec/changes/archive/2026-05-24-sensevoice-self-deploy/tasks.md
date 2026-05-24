## 1. Directory Restructuring

- [x] 1.1 Create funasr/ subdirectory structure: verification-2-self/funasr/{demo,docker,results,scripts}
- [x] 1.2 Move verification-2-self/demo/ → verification-2-self/funasr/demo/
- [x] 1.3 Move verification-2-self/results/ → verification-2-self/funasr/results/
- [x] 1.4 Move scripts/test_funasr_batch.py → verification-2-self/funasr/scripts/test_funasr_batch.py
- [x] 1.5 Move verification-2-self/docker/funasr/ contents → verification-2-self/funasr/docker/
- [x] 1.6 Create sensevoice/ subdirectory structure: verification-2-self/sensevoice/{demo,docker,results,scripts}
- [x] 1.7 Remove empty verification-2-self/docker/sensevoice/ (now under sensevoice/docker/)
- [x] 1.8 Remove empty top-level verification-2-self/demo/, results/, docker/ directories
- [x] 1.9 Update verification-2-self/README.md to show engine-grouped structure with links to funasr/ and sensevoice/

## 2. Skill Rename and Path Updates

- [x] 2.1 Rename .claude/skills/funasr-test/ → .claude/skills/self-funasr-test/
- [x] 2.2 Update self-funasr-test SKILL.md: change result paths to verification-2-self/funasr/results/, script paths to verification-2-self/funasr/scripts/
- [x] 2.3 Update test_funusar_batch.py internal paths: result output dir defaults to verification-2-self/funasr/results/
- [x] 2.4 Create .claude/skills/self-sensevoice-test/ with SKILL.md for SenseVoice batch testing

## 3. SenseVoice Docker Deployment

- [x] 3.1 Create verification-2-self/sensevoice/docker/start.sh with yiminger/sensevoice:latest startup command (port 8000, language env var)
- [x] 3.2 Add duplicate container detection to start.sh (check if port 8000 already in use)
- [x] 3.3 Create verification-2-self/sensevoice/docker/stop.sh for clean shutdown
- [x] 3.4 Test: run start.sh and verify http://localhost:8000/docs returns FastAPI docs
- [x] 3.5 Test: POST /extract_text with a sample audio file returns valid JSON

## 4. SenseVoice Demo

- [x] 4.1 Create verification-2-self/sensevoice/demo/index.html with engine address config (default http://localhost:8000)
- [x] 4.2 Implement file upload UI (single + batch, accept wav/mp3/m4a, reject unsupported formats)
- [x] 4.3 Implement language selector (auto, zh, en, ja, ko, yue)
- [x] 4.4 Implement HTTP POST /extract_text call with FormData (file + language param)
- [x] 4.5 Implement dual result display: clean text (results) and labeled text (label_result)
- [x] 4.6 Implement result management: clear, copy all, export session as JSON
- [x] 4.7 Test: upload audio file, verify transcription result displays correctly
- [x] 4.8 Test: upload batch of files, verify all results display
- [x] 4.9 Test: export session and verify JSON structure

## 5. SenseVoice Batch Test Script

- [x] 5.1 Create verification-2-self/sensevoice/scripts/test_sensevoice_batch.py with argparse CLI (--api-url, --manifest, --role, --version, --language, --limit, --output-json, --output-csv)
- [x] 5.2 Implement manifest CSV reading (reuse same format as FunASR: filepath,text,id,role,version)
- [x] 5.3 Implement HTTP POST /extract_text calls with file upload and language parameter
- [x] 5.4 Implement label_result parsing to extract language_detected and emotion_detected
- [x] 5.5 Implement CER calculation (reuse same logic as FunASR test)
- [x] 5.6 Implement JSON output with fields: id, expected, actual, cer, category, language_detected, emotion_detected, latency_ms
- [x] 5.7 Implement CSV output with columns: id, category, expected, actual, cer, passed, language_detected, latency_ms
- [x] 5.8 Implement --role and --version filtering
- [x] 5.9 Implement --limit flag
- [x] 5.10 Test: run against SenseVoice Docker with --limit 5 and verify output

## 6. Verification

- [x] 6.1 Verify FunASR batch test still works after directory restructuring (self-funasr-test skill)
- [x] 6.2 Verify SenseVoice Docker starts and responds correctly
- [x] 6.3 Verify SenseVoice Demo can transcribe uploaded files
- [x] 6.4 Verify SenseVoice batch test produces aligned output format
- [x] 6.5 Run SenseVoice batch test on full manifest and save results to verification-2-self/sensevoice/results/
