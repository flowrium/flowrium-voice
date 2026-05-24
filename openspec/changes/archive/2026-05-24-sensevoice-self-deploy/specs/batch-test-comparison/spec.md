## MODIFIED Requirements

### Requirement: Markdown report generation
The script SHALL generate a Markdown report at `verification-2-self/funasr/results/paraformer-report.md` when `--compare` is used. The report SHALL contain: test configuration, mode comparison table, hotword effect comparison table, category breakdown table, and worst 15 cases.

#### Scenario: Report structure matches verification plan
- **WHEN** compare mode completes
- **THEN** the Markdown report contains sections: test config, mode comparison, hotword effect, category breakdown, worst cases

#### Scenario: Hotword effect shows before/after comparison
- **WHEN** compare mode completes
- **THEN** the hotword effect table shows CER and exact match rate for both with-hotword and without-hotword runs, plus the improvement percentage

#### Scenario: Report output path updated for new directory structure
- **WHEN** compare mode completes
- **THEN** the report is written to verification-2-self/funasr/results/paraformer-report.md (not verification-2-self/results/)

### Requirement: Per-round JSON output preserved
The script SHALL write individual JSON result files for each round to `verification-2-self/funasr/results/` with naming pattern `paraformer-{mode}-{hotword-suffix}.json`.

#### Scenario: JSON files written for each round
- **WHEN** compare mode completes
- **THEN** 6 JSON files exist in verification-2-self/funasr/results/, one per mode×hotword combination

### Requirement: Hotword file support
The script SHALL read hotwords from `config/hotwords.txt` (one word per line) when `--compare` is used and no `--hotword` arguments are provided.

#### Scenario: Default hotword file
- **WHEN** user runs `--compare` without `--hotword` and `config/hotwords.txt` exists
- **THEN** hotwords are read from that file

#### Scenario: Missing hotword file
- **WHEN** user runs `--compare` without `--hotword` and `config/hotwords.txt` does not exist
- **THEN** the script prints a warning and runs with an empty hotword list for the hotword rounds

## ADDED Requirements

### Requirement: Skill rename to self-funasr-test
The FunASR batch test skill SHALL be renamed from `funasr-test` to `self-funasr-test`, and its internal paths SHALL be updated to reflect the new directory structure (verification-2-self/funasr/ instead of verification-2-self/).

#### Scenario: Skill invocation with new name
- **WHEN** user invokes the self-funasr-test skill
- **THEN** it runs the FunASR batch test with paths pointing to verification-2-self/funasr/scripts/ and verification-2-self/funasr/results/

#### Scenario: Skill description updated
- **WHEN** the skill is listed
- **THEN** it shows the self- prefix indicating it belongs to the self-deploy verification track
