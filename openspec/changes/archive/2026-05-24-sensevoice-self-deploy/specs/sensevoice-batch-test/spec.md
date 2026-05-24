## ADDED Requirements

### Requirement: HTTP batch test script
The system SHALL provide a Python script at verification-2-self/sensevoice/scripts/test_sensevoice_batch.py that reads audio manifests and sends files to the SenseVoice HTTP API for batch transcription testing.

#### Scenario: Running batch test with default manifest
- **WHEN** user runs `python3 test_sensevoice_batch.py --api-url http://localhost:8000`
- **THEN** the script reads all manifests from audio/*/manifest.csv, sends each audio file to the SenseVoice API, and computes CER against expected text

#### Scenario: Specifying custom manifest
- **WHEN** user runs `python3 test_sensevoice_batch.py --manifest audio/standard/manifest.csv`
- **THEN** the script only processes files from the specified manifest

### Requirement: Output format aligned with FunASR batch test
The batch test script SHALL output JSON and CSV files with the same field structure as the FunASR batch test (id, expected, actual, cer, category, etc.) to enable direct comparison.

#### Scenario: JSON output structure
- **WHEN** batch test completes
- **THEN** the JSON output contains fields: id, expected, actual, cer, category, language_detected, emotion_detected, latency_ms

#### Scenario: CSV output structure
- **WHEN** batch test completes with --output-csv flag
- **THEN** the CSV file has columns: id, category, expected, actual, cer, passed, language_detected, latency_ms

### Requirement: Language and emotion metadata capture
The batch test script SHALL capture the language and emotion tags from the label_result field and include them in the output.

#### Scenario: Parsing label_result
- **WHEN** SenseVoice returns label_result `<|zh|NEUTRAL|>今天出勤率多少`
- **THEN** the script records language_detected="zh" and emotion_detected="NEUTRAL" in the output

### Requirement: Role and version filtering
The batch test script SHALL support --role and --version filters consistent with the FunASR batch test.

#### Scenario: Filtering by role
- **WHEN** user runs `python3 test_sensevoice_batch.py --role principal --role teacher`
- **THEN** only audio files matching those roles are tested

#### Scenario: Filtering by version
- **WHEN** user runs `python3 test_sensevoice_batch.py --version standard`
- **THEN** only audio files from the standard version directory are tested

### Requirement: Result file output paths
The batch test script SHALL write results to verification-2-self/sensevoice/results/ with configurable output file names.

#### Scenario: Default output path
- **WHEN** user runs batch test without specifying output path
- **THEN** results are written to verification-2-self/sensevoice/results/sensevoice-results.json and sensevoice-results.csv

#### Scenario: Custom output path
- **WHEN** user runs `python3 test_sensevoice_batch.py --output-json custom.json`
- **THEN** results are written to the specified path

### Requirement: Language parameter support
The batch test script SHALL support a --language parameter to set the language for the SenseVoice API (default: auto).

#### Scenario: Auto language detection
- **WHEN** user runs batch test without --language flag
- **THEN** each request uses language="auto"

#### Scenario: Specifying Chinese
- **WHEN** user runs `python3 test_sensevoice_batch.py --language zh`
- **THEN** each request uses language="zh"
