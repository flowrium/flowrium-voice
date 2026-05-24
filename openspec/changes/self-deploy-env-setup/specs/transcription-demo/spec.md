## ADDED Requirements

### Requirement: WebSocket connection management
The Demo SHALL allow users to input a WebSocket address, connect, and disconnect from an ASR service, displaying the current connection status.

#### Scenario: Successful connection
- **WHEN** user enters a valid WebSocket URL and clicks connect
- **THEN** the Demo establishes a WebSocket connection and displays "connected" status with the server address

#### Scenario: Connection failure
- **WHEN** user enters an invalid URL or the server is unreachable
- **THEN** the Demo displays a "disconnected" or "error" status

#### Scenario: Disconnect
- **WHEN** user clicks disconnect while connected
- **THEN** the WebSocket connection is closed and status updates to "disconnected"

### Requirement: Real-time microphone recording
The Demo SHALL capture audio from the microphone via MediaRecorder API and stream PCM data to the connected ASR WebSocket endpoint in real-time.

#### Scenario: Start and stop recording
- **WHEN** user clicks "start recording" and speaks into the microphone, then clicks "stop"
- **THEN** PCM audio is streamed to the ASR service during recording, and streaming stops when "stop" is clicked

#### Scenario: Recording requires active connection
- **WHEN** user clicks "start recording" without an active WebSocket connection
- **THEN** the Demo displays a warning that connection is required first

### Requirement: Audio file upload
The Demo SHALL allow users to upload local audio files (wav/mp3/m4a) and send them to the ASR service for transcription.

#### Scenario: Upload and transcribe audio file
- **WHEN** user uploads a supported audio file while connected
- **THEN** the Demo reads the file, sends audio data to the ASR service, and displays transcription results

#### Scenario: Unsupported format
- **WHEN** user uploads a file with an unsupported format
- **THEN** the Demo displays an error message indicating unsupported format

### Requirement: Partial and final result display
The Demo SHALL distinguish between partial (real-time) and final (corrected) transcription results, displaying them with visual differentiation.

#### Scenario: Partial result appears during speech
- **WHEN** a partial result message is received from the ASR service
- **THEN** the Demo displays the partial text with a visual indicator (e.g., trailing underscore or distinct styling)

#### Scenario: Final result replaces partial
- **WHEN** a final result message is received after a partial result
- **THEN** the Demo replaces or appends the final text, visually distinct from partial results

#### Scenario: Auto-scroll
- **WHEN** new transcription results appear
- **THEN** the result area automatically scrolls to show the latest content

### Requirement: Mode switching
The Demo SHALL allow switching between 2pass, online, and offline ASR modes, and allow changing the engine WebSocket address.

#### Scenario: Switch ASR mode
- **WHEN** user selects a different mode (2pass/online/offline) from a dropdown
- **THEN** subsequent audio input uses the selected mode

#### Scenario: Switch engine address
- **WHEN** user changes the WebSocket URL input and reconnects
- **THEN** the Demo connects to the new engine address

### Requirement: Hotword management
The Demo SHALL allow adding and removing hotwords, sending hotword configuration to the ASR engine, and providing preset school management scenario hotwords.

#### Scenario: Add hotword
- **WHEN** user types a hotword and clicks add
- **THEN** the hotword appears in the hotword list and is sent to the ASR engine on next audio submission

#### Scenario: Remove hotword
- **WHEN** user removes a hotword from the list
- **THEN** the hotword is no longer sent to the ASR engine

#### Scenario: Load preset hotwords
- **WHEN** user clicks "load presets"
- **THEN** a predefined set of school management hotwords (出勤率, 合格率, 平均分, 教务处, etc.) is added to the hotword list

### Requirement: Result management
The Demo SHALL provide controls to clear results, copy all transcription text, and export the session record.

#### Scenario: Clear results
- **WHEN** user clicks "clear results"
- **THEN** all displayed transcription text is removed

#### Scenario: Copy all text
- **WHEN** user clicks "copy all"
- **THEN** all final transcription text is copied to clipboard

#### Scenario: Export session record
- **WHEN** user clicks "export"
- **THEN** the Demo downloads a file containing all transcription results with timestamps and metadata (mode, hotwords used, partial vs final)

### Requirement: Pure frontend with no backend dependency
The Demo SHALL be implemented as a single HTML file with embedded CSS and JavaScript, requiring no build step or backend server.

#### Scenario: Open and use without server
- **WHEN** user opens the HTML file directly in a browser
- **THEN** the Demo loads and functions correctly (WebSocket connections may require serving via localhost due to browser security)
