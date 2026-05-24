## ADDED Requirements

### Requirement: File upload transcription interface
The SenseVoice Demo SHALL provide a browser-based interface for uploading audio files (wav/mp3/m4a) and displaying transcription results from the SenseVoice HTTP API.

#### Scenario: Uploading a single audio file
- **WHEN** user selects an audio file and clicks upload
- **THEN** the file is sent via HTTP POST to the SenseVoice API and the transcription result is displayed

#### Scenario: Unsupported file format
- **WHEN** user selects a file with unsupported format (not wav/mp3/m4a)
- **THEN** an error message is displayed and the file is not sent

#### Scenario: API connection failure
- **WHEN** the SenseVoice API is unreachable
- **THEN** an error message is displayed indicating the connection failure

### Requirement: Engine address configuration
The Demo SHALL allow users to configure the SenseVoice API endpoint URL, defaulting to http://localhost:8000.

#### Scenario: Custom API endpoint
- **WHEN** user changes the engine address field and uploads a file
- **THEN** the request is sent to the configured URL instead of the default

### Requirement: Language selection
The Demo SHALL provide a language selector with options: auto, zh, en, ja, ko, yue, defaulting to auto.

#### Scenario: Selecting a specific language
- **WHEN** user selects "zh" from the language dropdown and uploads a file
- **THEN** the language parameter is set to "zh" in the API request

### Requirement: Dual result display
The Demo SHALL display both the clean transcription text (results field) and the labeled text (label_result field with language and emotion tags).

#### Scenario: Displaying results with tags
- **WHEN** SenseVoice returns `<|zh|NEUTRAL|>今天出勤率多少`
- **THEN** the Demo shows "今天出勤率多少" as clean text and the full labeled version with language/emotion tags visible

### Requirement: Batch file upload
The Demo SHALL support uploading multiple audio files at once and displaying results for each file.

#### Scenario: Uploading multiple files
- **WHEN** user selects 5 audio files and uploads them
- **THEN** the Demo sends each file to the API sequentially and displays all 5 results

### Requirement: Session export
The Demo SHALL support exporting all transcription results from the current session as a JSON file.

#### Scenario: Exporting session results
- **WHEN** user clicks the export button
- **THEN** a JSON file is downloaded containing all transcription results with timestamps, file names, clean text, and labeled text

### Requirement: Result management
The Demo SHALL support clearing all results and copying all transcription text to clipboard.

#### Scenario: Clearing results
- **WHEN** user clicks the clear button
- **THEN** all displayed results are removed and the session history is cleared

#### Scenario: Copying all text
- **WHEN** user clicks the copy button and there are results
- **THEN** all clean transcription texts are copied to clipboard, one per line
