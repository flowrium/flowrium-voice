## ADDED Requirements

### Requirement: SenseVoice Docker service deployment
The system SHALL provide a Docker deployment configuration for SenseVoice using the yiminger/sensevoice:latest image, exposing an HTTP API on port 8000 for offline speech recognition.

#### Scenario: Starting SenseVoice service
- **WHEN** user runs the SenseVoice Docker startup command
- **THEN** the container starts and the HTTP API becomes available at http://localhost:8000

#### Scenario: Health check endpoint
- **WHEN** user sends GET request to http://localhost:8000/docs
- **THEN** the FastAPI documentation page is returned, confirming the service is running

#### Scenario: Transcribe audio via API
- **WHEN** user sends POST request to /extract_text with an audio file
- **THEN** the API returns JSON with `results` (clean text) and `label_result` (text with language/emotion tags)

### Requirement: SenseVoice Docker startup script
The system SHALL provide a shell script at verification-2-self/sensevoice/docker/start.sh that starts the yiminger/sensevoice container with appropriate configuration.

#### Scenario: Running the startup script
- **WHEN** user executes `bash verification-2-self/sensevoice/docker/start.sh`
- **THEN** the SenseVoice Docker container starts with port 8000 mapped to localhost

#### Scenario: Container already running
- **WHEN** user runs start.sh and a SenseVoice container is already running on port 8000
- **THEN** the script prints a warning and does not start a duplicate container

### Requirement: Language configuration
The SenseVoice service SHALL default to "auto" language detection and allow configuration of specific languages (zh, en, ja, ko, yue) via environment variable.

#### Scenario: Default auto language detection
- **WHEN** SenseVoice service starts without LANGUAGE env var
- **THEN** language is set to "auto" and the model auto-detects the language of input audio

#### Scenario: Specific language configuration
- **WHEN** SenseVoice service starts with LANGUAGE=zh env var
- **THEN** language is set to "zh" and the model processes input as Chinese
