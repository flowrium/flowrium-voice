## ADDED Requirements

### Requirement: FunASR Docker container provides streaming transcription service
The system SHALL run FunASR in a Docker container exposing a WebSocket endpoint for real-time streaming ASR on port 10095.

#### Scenario: Container starts and streaming WebSocket is accessible
- **WHEN** user runs the documented docker run command
- **THEN** the container starts and `ws://localhost:10095` accepts WebSocket connections within 60 seconds

#### Scenario: Streaming transcription returns results
- **WHEN** PCM audio data is sent to the streaming WebSocket endpoint
- **THEN** the service returns partial and final transcription results as JSON messages

### Requirement: FunASR Docker container provides offline transcription service
The system SHALL expose a WebSocket endpoint for offline (non-streaming) ASR on port 10096.

#### Scenario: Offline transcription returns results
- **WHEN** a complete audio segment is sent to the offline WebSocket endpoint
- **THEN** the service returns a final transcription result

### Requirement: FunASR supports runtime hotwords
The system SHALL accept hotword configuration via the WebSocket protocol without requiring container restart.

#### Scenario: Hotwords improve transcription accuracy
- **WHEN** hotwords are sent before audio data and the spoken content contains hotword terms
- **THEN** transcription results preferentially recognize hotword terms over homophones

### Requirement: FunASR supports 2pass mode
The system SHALL support 2pass mode which combines online (partial) and offline (final) recognition in a single WebSocket connection.

#### Scenario: 2pass mode provides partial then final results
- **WHEN** audio is streamed in 2pass mode
- **THEN** partial results appear in real-time, followed by a corrected final result after utterance completion

### Requirement: CPU-only operation
The system SHALL run entirely on CPU without requiring GPU, compatible with Mac Docker Desktop (both Apple Silicon and Intel).

#### Scenario: Container runs on Mac without GPU
- **WHEN** the Docker container is started on a Mac with Docker Desktop
- **THEN** the FunASR service operates correctly using CPU only, with memory usage below 4GB
