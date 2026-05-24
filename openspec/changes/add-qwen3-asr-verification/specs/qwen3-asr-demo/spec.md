## ADDED Requirements

### Requirement: File-based transcription interface
The Qwen3-ASR Demo SHALL provide a browser-based interface for submitting audio files and displaying transcription results from the local Qwen3-ASR service.

#### Scenario: Uploading a supported audio file
- **WHEN** user selects a supported audio file and submits it through the Demo
- **THEN** the Demo sends the audio to the configured Qwen3-ASR service endpoint and displays the returned transcription result

#### Scenario: Unsupported file format
- **WHEN** user selects a file type not supported by the Demo
- **THEN** the Demo shows an error message and does not send the file to the service

#### Scenario: Service connection failure
- **WHEN** the configured Qwen3-ASR service endpoint is unreachable
- **THEN** the Demo shows a connection error message and keeps the current page usable for retry

### Requirement: Engine address configuration
The Demo SHALL allow users to configure the Qwen3-ASR service endpoint, defaulting to the localhost address exposed by the Qwen3-ASR Docker startup flow.

#### Scenario: Custom service endpoint
- **WHEN** user changes the engine address field before submitting audio
- **THEN** the Demo sends the request to the configured endpoint instead of the default one

### Requirement: Optional live transcription mode
If the underlying Qwen3-ASR service exposes a streaming interface, the Demo SHALL provide microphone-based live transcription using that interface.

#### Scenario: Streaming interface available
- **WHEN** the Qwen3-ASR service supports live streaming transcription
- **THEN** the Demo offers recording controls and displays incremental and final transcription updates

#### Scenario: Streaming interface unavailable
- **WHEN** the Qwen3-ASR service only supports offline transcription
- **THEN** the Demo omits or disables live recording controls and documents that only file-based verification is supported

### Requirement: Result management
The Demo SHALL support clearing displayed results and exporting the current session's transcription results.

#### Scenario: Clearing results
- **WHEN** user clicks the clear button
- **THEN** all displayed Qwen3-ASR transcription results are removed from the session view

#### Scenario: Exporting session results
- **WHEN** user clicks the export button
- **THEN** the Demo downloads a file containing the transcription results collected in the current session
