## ADDED Requirements

### Requirement: WebSocket batch test script
The system SHALL provide a Python script at verification-2-self/wenet/scripts/test_wenet_batch.py that reads audio manifests and sends audio to the WeNet WebSocket service for batch transcription testing.

#### Scenario: Running batch test with default manifest
- **WHEN** user runs `python3 test_wenet_batch.py --ws-url ws://127.0.0.1:10097`
- **THEN** the script reads all manifests from audio/*/manifest.csv, sends each audio file to the WeNet service, and computes CER against expected text

#### Scenario: Specifying custom manifest
- **WHEN** user runs `python3 test_wenet_batch.py --manifest audio/standard/manifest.csv`
- **THEN** the script only processes files from the specified manifest

### Requirement: WeNet WebSocket protocol implementation
The batch test script SHALL implement the WeNet WebSocket protocol: send start signal with `{"signal": "start", "nbest": 1}`, stream audio as binary frames (960 samples per frame at 16kHz), and send end signal with `{"signal": "end"}`.

#### Scenario: Full WebSocket transcription cycle
- **WHEN** the script sends a complete audio file through the WebSocket
- **THEN** it follows the protocol: start → audio frames → end, and receives the final transcription

#### Scenario: Parsing response
- **WHEN** WeNet returns `{"status": "ok", "nbest": [{"sentence": "今天出勤率多少"}]}`
- **THEN** the script extracts "今天出勤率多少" as the transcription result

### Requirement: Output format aligned with FunASR batch test
The batch test script SHALL output JSON and CSV files with the same core field structure as the FunASR batch test (id, expected, actual, cer, category, etc.) to enable direct comparison.

#### Scenario: JSON output structure
- **WHEN** batch test completes
- **THEN** the JSON output contains meta, summary (overall/by_version/by_role/by_category/worst_cases), and results array with fields: id, role, version, category, expected, actual, cer, char_distance, expected_chars, norm_exact_match, audio_ms, first_partial_ms, final_latency_ms

#### Scenario: CSV output structure
- **WHEN** batch test completes with --output-csv flag
- **THEN** the CSV file has columns: id, role, version, category, file_path, expected, actual, norm_exact_match, char_distance, expected_chars, cer, audio_ms, first_partial_ms, final_latency_ms

### Requirement: Hotword support
The batch test script SHALL support passing hotwords to the WeNet service via the --hotword flag and --hotwords-file flag, mirroring the FunASR batch test interface.

#### Scenario: Running with hotwords from file
- **WHEN** user runs `python3 test_wenet_batch.py --hotwords-file config/hotwords.txt`
- **THEN** the script reads hotwords from the file and includes them in the WeNet request

#### Scenario: Running with inline hotwords
- **WHEN** user runs `python3 test_wenet_batch.py --hotword 出勤率 --hotword 合格率`
- **THEN** the specified hotwords are included in the WeNet request

### Requirement: Filtering and limiting options
The batch test script SHALL support --limit, --version, and --role filtering options, identical to the FunASR batch test.

#### Scenario: Limiting test count
- **WHEN** user runs `python3 test_wenet_batch.py --limit 10`
- **THEN** only the first 10 matching manifest rows are tested

#### Scenario: Filtering by role
- **WHEN** user runs `python3 test_wenet_batch.py --role principal`
- **THEN** only rows with role=principal are tested
