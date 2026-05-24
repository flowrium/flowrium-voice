## ADDED Requirements

### Requirement: Compare mode runs multiple rounds automatically
The script SHALL support a `--compare` flag that runs all combinations of modes (2pass, online, offline) and hotword configurations (none, from hotwords file), producing a total of 6 rounds.

#### Scenario: Running compare mode with all defaults
- **WHEN** user runs `python test_funasr_batch.py --compare`
- **THEN** the script runs 6 rounds (3 modes × 2 hotword configs) sequentially and produces a combined Markdown report

#### Scenario: Compare mode with custom hotwords
- **WHEN** user runs `python test_funasr_batch.py --compare --hotword 出勤率 合格率`
- **THEN** the script uses the specified hotwords instead of reading from config/hotwords.txt

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

### Requirement: Markdown report generation
The script SHALL generate a Markdown report at `verification-2-self/results/paraformer-report.md` when `--compare` is used. The report SHALL contain: test configuration, mode comparison table, hotword effect comparison table, category breakdown table, and worst 15 cases.

#### Scenario: Report structure matches verification plan
- **WHEN** compare mode completes
- **THEN** the Markdown report contains sections: test config, mode comparison, hotword effect, category breakdown, worst cases

#### Scenario: Hotword effect shows before/after comparison
- **WHEN** compare mode completes
- **THEN** the hotword effect table shows CER and exact match rate for both with-hotword and without-hotword runs, plus the improvement percentage

### Requirement: Hotword file support
The script SHALL read hotwords from `config/hotwords.txt` (one word per line) when `--compare` is used and no `--hotword` arguments are provided.

#### Scenario: Default hotword file
- **WHEN** user runs `--compare` without `--hotword` and `config/hotwords.txt` exists
- **THEN** hotwords are read from that file

#### Scenario: Missing hotword file
- **WHEN** user runs `--compare` without `--hotword` and `config/hotwords.txt` does not exist
- **THEN** the script prints a warning and runs with an empty hotword list for the hotword rounds

### Requirement: Per-round JSON output preserved
The script SHALL write individual JSON result files for each round to `verification-2-self/results/` with naming pattern `paraformer-{mode}-{hotword-suffix}.json`.

#### Scenario: JSON files written for each round
- **WHEN** compare mode completes
- **THEN** 6 JSON files exist in the results directory, one per mode×hotword combination

### Requirement: Backward compatibility of single-run mode
When `--compare` is NOT used, the script SHALL behave exactly as before, with no changes to input arguments, output format, or exit behavior.

#### Scenario: Single-run mode unchanged
- **WHEN** user runs `python test_funasr_batch.py --mode 2pass --hotword 出勤率`
- **THEN** the script runs once, outputs JSON/CSV as before, with category field added to results
