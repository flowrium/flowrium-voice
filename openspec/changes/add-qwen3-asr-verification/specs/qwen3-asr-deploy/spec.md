## ADDED Requirements

### Requirement: Qwen3-ASR Docker service deployment
The system SHALL provide a Docker deployment flow for Qwen3-ASR using the `qwenllm/qwen3-asr` image, exposing a local transcription service endpoint that can be used by the verification Demo and batch test script.

#### Scenario: Starting Qwen3-ASR service
- **WHEN** user runs the Qwen3-ASR Docker startup command
- **THEN** the container starts successfully and the transcription service becomes reachable on a documented localhost endpoint

#### Scenario: Documenting the service endpoint
- **WHEN** the startup script finishes successfully
- **THEN** it prints the local endpoint and protocol information needed by the Demo and batch test script

### Requirement: Qwen3-ASR Docker startup script
The system SHALL provide a shell script at `verification-2-self/qwen3-asr/docker/start.sh` that starts the Qwen3-ASR container and waits until the local service is ready.

#### Scenario: Running the startup script
- **WHEN** user executes `bash verification-2-self/qwen3-asr/docker/start.sh`
- **THEN** the script starts the container, performs a readiness check appropriate to the exposed service protocol, and prints a success message

#### Scenario: Container already running
- **WHEN** user runs `start.sh` while the Qwen3-ASR container is already serving on the configured local endpoint
- **THEN** the script reports that the service is already available and does not start a duplicate container

### Requirement: Qwen3-ASR Docker stop script
The system SHALL provide a shell script at `verification-2-self/qwen3-asr/docker/stop.sh` that stops and removes the Qwen3-ASR container.

#### Scenario: Stopping the service
- **WHEN** user executes `bash verification-2-self/qwen3-asr/docker/stop.sh`
- **THEN** the Qwen3-ASR container is stopped and removed from Docker
