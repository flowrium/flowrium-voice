# Vosk Models

This directory should contain the Vosk Chinese ASR models.

## Required Models

| Model | Size | Description |
|-------|------|-------------|
| `vosk-model-small-cn-0.22` | ~50MB | Small Chinese model (fast, lower accuracy) |
| `vosk-model-cn-0.22` | ~1.3GB | Full Chinese model (slower, higher accuracy) |

## Download

Run the download script from the project root:

```bash
bash verification-3-edge/vosk/setup/download_models.sh
```

Or download manually from <https://alphacephei.com/vosk/models>:

- <https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip>
- <https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip>

Extract into this directory so the structure is:

```
models/
├── vosk-model-small-cn-0.22/
│   ├── am/
│   ├── conf/
│   ├── graph/
│   └── ivector/
└── vosk-model-cn-0.22/
    ├── am/
    ├── conf/
    ├── graph/
    ├── ivector/
    ├── rescore/
    └── rnnlm/
```
