## Multi-engine ASR Comparison

This report aggregates the latest available self-deploy results for FunASR, SenseVoice, WeNet, and Qwen3-ASR.

### Overall
| Engine | Count | Success Rate | CER | Avg Latency | P95 Latency | Notes | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FunASR | 2 | 100.00% | 0.00% | 1888.0ms | 1369.4ms | supports hotwords and 2pass | verification-2-self/funasr/results/paraformer-2pass-hotword.json |
| SenseVoice | 240 | 72.08% | 3.71% | 247.4ms | 424.8ms | offline only, no hotwords | verification-2-self/sensevoice/results/sensevoice-results.json |
| WeNet | 240 | 29.58% | 14.80% | 217.8ms | 342.3ms | supports hotwords and streaming | verification-2-self/wenet/results/wenet-results.json |
| Qwen3-ASR | 0 | 0.00% | 0.00% | — | — | OpenAI-compatible offline transcription API | verification-2-self/qwen3-asr/results/qwen3-asr-results.json |

### By Category
| Category | Engine | Success Rate | CER |
| --- | --- | --- | --- |
| myvoice/director | FunASR | — | — |
| myvoice/director | SenseVoice | 65.00% | 4.73% |
| myvoice/director | WeNet | — | — |
| myvoice/director | Qwen3-ASR | — | — |
| myvoice/principal | FunASR | — | — |
| myvoice/principal | SenseVoice | 65.00% | 5.09% |
| myvoice/principal | WeNet | — | — |
| myvoice/principal | Qwen3-ASR | — | — |
| myvoice/staff | FunASR | — | — |
| myvoice/staff | SenseVoice | 86.67% | 1.45% |
| myvoice/staff | WeNet | — | — |
| myvoice/staff | Qwen3-ASR | — | — |
| myvoice/teacher | FunASR | — | — |
| myvoice/teacher | SenseVoice | 71.67% | 3.19% |
| myvoice/teacher | WeNet | — | — |
| myvoice/teacher | Qwen3-ASR | — | — |
| tts-baseline | FunASR | 100.00% | 0.00% |
| tts-baseline | SenseVoice | — | — |
| tts-baseline | WeNet | 29.58% | 14.80% |
| tts-baseline | Qwen3-ASR | — | — |

### Availability
All four engine result files are present.
