## MODIFIED Requirements

### Requirement: Compare mode runs multiple rounds automatically
The script SHALL support a `--compare` flag that runs all combinations of modes and hotword configurations across all tested engines (FunASR, SenseVoice, WeNet, and Qwen3-ASR), producing a combined Markdown report with four-engine comparison.

#### Scenario: Running compare mode with all defaults
- **WHEN** user runs `python test_funasr_batch.py --compare`
- **THEN** the script runs the FunASR comparison rounds and produces a combined Markdown report that includes all engines whose result files are available

#### Scenario: Four-engine comparison report
- **WHEN** batch tests for FunASR, SenseVoice, WeNet, and Qwen3-ASR have all been run
- **THEN** the combined report includes side-by-side CER, latency, hotword effectiveness when applicable, and per-category comparison across all four engines

### Requirement: Category inference from directory name
The script SHALL infer the `category` of each audio file from its parent directory name. Directories matching `^[A-F]-` prefix are mapped to that category label; all others are mapped to `tts-baseline`.

#### Scenario: A-F categorized audio
- **WHEN** a file path is `audio/B-metrics/003.wav`
- **THEN** the category is inferred as `B-metrics`

#### Scenario: TTS baseline audio
- **WHEN** a file path is `audio/standard/principal/principal_001.wav`
- **THEN** the category is inferred as `tts-baseline`

### Requirement: By-category grouped statistics
The script SHALL compute and include by-category statistics (CER, exact match rate, norm exact match rate, avg latency, p95 latency) in both JSON output and the combined Markdown report.

#### Scenario: Report includes per-category breakdown
- **WHEN** compare mode completes
- **THEN** the report contains a table with one row per category showing CER, exact match rate, and worst case for each participating engine

## ADDED Requirements

### Requirement: Multi-engine comparison report
The system SHALL provide a combined comparison artifact that summarizes FunASR, SenseVoice, WeNet, and Qwen3-ASR results side-by-side.

#### Scenario: Generating four-engine comparison
- **WHEN** batch tests for all four self-deploy engines have been run and their result files are available
- **THEN** the comparison artifact includes an overall summary table, per-category comparison, and engine-specific notes for unsupported dimensions such as hotwords or streaming
