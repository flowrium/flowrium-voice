## ADDED Requirements

### Requirement: Real-time microphone transcription interface
The WeNet Demo SHALL provide a browser-based interface for real-time microphone recording with streaming transcription via WebSocket, displaying partial and final results.

#### Scenario: Starting real-time recording
- **WHEN** user clicks "Start Recording" and speaks into the microphone
- **THEN** the Demo sends audio frames via WebSocket to the WeNet service and displays partial transcription results in real-time

#### Scenario: Stopping recording and showing final result
- **WHEN** user clicks "Stop Recording"
- **THEN** the Demo sends the end signal and displays the final transcription result

#### Scenario: WebSocket connection failure
- **WHEN** the WeNet WebSocket service is unreachable
- **THEN** an error message is displayed indicating the connection failure

### Requirement: File upload transcription interface
The WeNet Demo SHALL provide a browser-based interface for uploading audio files (wav/mp3/m4a) and displaying transcription results from the WeNet WebSocket API.

#### Scenario: Uploading a single audio file
- **WHEN** user selects an audio file and clicks upload
- **THEN** the file is sent via WebSocket to the WeNet service and the transcription result is displayed

#### Scenario: Unsupported file format
- **WHEN** user selects a file with unsupported format (not wav/mp3/m4a)
- **THEN** an error message is displayed and the file is not sent

### Requirement: Engine address configuration
The Demo SHALL allow users to configure the WeNet WebSocket endpoint URL, defaulting to ws://localhost:10097.

#### Scenario: Custom WebSocket endpoint
- **WHEN** user changes the engine address field and starts recording
- **THEN** the WebSocket connects to the configured URL instead of the default

### Requirement: Hotword management
The Demo SHALL allow users to add and remove hotwords that are sent to the WeNet service with each transcription request.

#### Scenario: Adding hotwords
- **WHEN** user enters a hotword and clicks "Add"
- **THEN** the hotword is included in the start signal for subsequent transcriptions

#### Scenario: Removing hotwords
- **WHEN** user removes a hotword from the list
- **THEN** the hotword is excluded from subsequent transcription requests
