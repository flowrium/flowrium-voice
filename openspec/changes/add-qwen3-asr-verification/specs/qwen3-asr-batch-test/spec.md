## ADDED Requirements

### Requirement: Qwen3-ASR batch test script
The system SHALL provide a Python script at `verification-2-self/qwen3-asr/scripts/test_qwen3_asr_batch.py` that reads audio manifests and submits each sample to the local Qwen3-ASR service for transcription testing.

#### Scenario: Running batch test with default manifests
- **WHEN** user runs the batch test script with only the service endpoint parameter
- **THEN** the script reads all manifests from `audio/*/manifest.csv`, transcribes each matching audio file through Qwen3-ASR, and computes CER against expected text

#### Scenario: Specifying custom manifest
- **WHEN** user runs the batch test script with one or more `--manifest` arguments
- **THEN** only the specified manifests are processed

### Requirement: Filtering and limiting options
The batch test script SHALL support `--limit`, `--version`, and `--role` filters consistent with the existing self-deploy engine batch tests.

#### Scenario: Limiting test count
- **WHEN** user runs the batch test script with `--limit 10`
- **THEN** only the first 10 matching manifest rows are tested

#### Scenario: Filtering by role
- **WHEN** user runs the batch test script with `--role principal`
- **THEN** only manifest rows whose role is `principal` are tested

### Requirement: Output format aligned with existing engine tests
The batch test script SHALL write JSON, CSV, and Markdown outputs to `verification-2-self/qwen3-asr/results/` using the same core comparison fields as the existing self-deploy engine tests.

#### Scenario: JSON output structure
- **WHEN** the batch test completes
- **THEN** the JSON output contains metadata, summary statistics, and per-file results including `id`, `role`, `version`, `category`, `expected`, `actual`, and `cer`

#### Scenario: CSV output structure
- **WHEN** the batch test completes with CSV output enabled
- **THEN** the CSV file includes one row per tested file with the core comparison fields needed for cross-engine analysis

### Requirement: Protocol-specific adapter isolation
The batch test script SHALL isolate Qwen3-ASR protocol handling inside its own request adapter while keeping manifest loading, text normalization, CER calculation, and result summarization aligned with the existing verification scripts.

#### Scenario: Reusing shared evaluation behavior
- **WHEN** the script processes a transcription result from Qwen3-ASR
- **THEN** normalization, CER calculation, grouping, and worst-case reporting follow the same evaluation rules used by the existing self-deploy engine tests
