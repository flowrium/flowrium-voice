## MODIFIED Requirements

### Requirement: Compare mode runs multiple rounds automatically
The script SHALL support a `--compare` flag that runs all combinations of modes and hotword configurations across all tested engines (FunASR, SenseVoice, WeNet), producing a combined Markdown report with three-engine comparison.

#### Scenario: Running compare mode with all defaults
- **WHEN** user runs `python test_funasr_batch.py --compare`
- **THEN** the script runs 6 rounds (3 modes × 2 hotword configs) for FunASR sequentially and produces a combined Markdown report

#### Scenario: Three-engine comparison report
- **WHEN** all three engine batch tests have been run
- **THEN** a three-engine comparison report is generated at verification-2-self/results/three-engine-comparison.md with side-by-side CER, latency, and hotword effectiveness for FunASR, SenseVoice, and WeNet

### Requirement: Category inference from directory name
The script SHALL infer the `category` of each audio file from its parent directory name. Directories matching `^[A-F]-` prefix are mapped to that category label; all others are mapped to `tts-baseline`.

#### Scenario: A-F categorized audio
- **WHEN** a file path is `audio/B-metrics/003.wav`
- **THEN** the category is inferred as `B-metrics`

#### Scenario: TTS baseline audio
- **WHEN** a file path is `audio/standard/principal/principal_001.wav`
- **THEN** the category is inferred as `tts-baseline`

### Requirement: By-category grouped statistics
The script SHALL compute and include by-category statistics (CER, exact match rate, norm exact match rate, avg latency, p95 latency) in both JSON output and Markdown report.

#### Scenario: Report includes per-category breakdown
- **WHEN** compare mode completes
- **THEN** the report contains a table with one row per category showing CER, exact match rate, and worst case

## ADDED Requirements

### Requirement: Three-engine comparison report
The system SHALL provide a script or report that compares FunASR, SenseVoice, and WeNet test results side-by-side, covering CER, latency, hotword effectiveness, and per-category breakdowns.

#### Scenario: Generating three-engine comparison
- **WHEN** batch tests for all three engines have been run and their JSON results are available
- **THEN** the comparison report includes an overall summary table with all three engines, per-category comparison, and hotword effect comparison
