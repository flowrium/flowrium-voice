## ADDED Requirements

### Requirement: WeNet Docker service deployment
The system SHALL provide a Docker deployment configuration for WeNet using the wenet-e2e/wenet:latest image, exposing a WebSocket API on port 10097 for streaming and offline speech recognition.

#### Scenario: Starting WeNet service
- **WHEN** user runs the WeNet Docker startup command
- **THEN** the container starts and the WebSocket API becomes available at ws://localhost:10097

#### Scenario: Transcribe audio via WebSocket
- **WHEN** user connects to ws://localhost:10097, sends start signal, audio frames, and end signal
- **THEN** the service returns JSON with transcription text in nbest format

#### Scenario: Service with hotword support
- **WHEN** WeNet service starts with hotwords configured
- **THEN** the LM rescoring applies hotword bias during decoding

### Requirement: WeNet Docker startup script
The system SHALL provide a shell script at verification-2-self/wenet/docker/start.sh that starts the WeNet container with appropriate configuration.

#### Scenario: Running the startup script
- **WHEN** user executes `bash verification-2-self/wenet/docker/start.sh`
- **THEN** the WeNet Docker container starts with port 10097 mapped to localhost

#### Scenario: Container already running
- **WHEN** user runs start.sh and a WeNet container is already running on port 10097
- **THEN** the script prints a warning and does not start a duplicate container

### Requirement: WeNet Docker stop script
The system SHALL provide a shell script at verification-2-self/wenet/docker/stop.sh that stops and removes the WeNet container.

#### Scenario: Stopping the service
- **WHEN** user executes `bash verification-2-self/wenet/docker/stop.sh`
- **THEN** the WeNet Docker container is stopped and removed
