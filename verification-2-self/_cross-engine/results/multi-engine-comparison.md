## Multi-engine ASR Comparison

This report aggregates the latest available self-deploy results for FunASR, SenseVoice, WeNet, and Qwen3-ASR.

### Overall
| Engine | Count | Success Rate | CER | Avg Latency | P95 Latency | Notes | Source |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FunASR | 720 | 79.72% | 2.34% | 552.2ms | 853.5ms | supports hotwords and 2pass | verification-2-self/funasr/results/paraformer-results.json |
| SenseVoice | 720 | 85.69% | 1.89% | 753.6ms | 1013.9ms | offline only, no hotwords | verification-2-self/sensevoice/results/sensevoice-results.json |
| WeNet | 720 | 21.53% | 13.83% | 188.5ms | 240.5ms | supports hotwords and streaming | verification-2-self/wenet/results/wenet-results.json |
| Qwen3-ASR | 0 | 0.00% | 0.00% | — | — | OpenAI-compatible offline transcription API | verification-2-self/qwen3-asr/results/qwen3-asr-results.json |

### By Category
| Category | Engine | Success Rate | CER |
| --- | --- | --- | --- |
| humanized/director | FunASR | 76.67% | 2.44% |
| humanized/director | SenseVoice | 91.67% | 1.00% |
| humanized/director | WeNet | — | — |
| humanized/director | Qwen3-ASR | — | — |
| humanized/principal | FunASR | 86.67% | 1.74% |
| humanized/principal | SenseVoice | 90.00% | 1.07% |
| humanized/principal | WeNet | — | — |
| humanized/principal | Qwen3-ASR | — | — |
| humanized/staff | FunASR | 90.00% | 0.97% |
| humanized/staff | SenseVoice | 90.00% | 1.13% |
| humanized/staff | WeNet | — | — |
| humanized/staff | Qwen3-ASR | — | — |
| humanized/teacher | FunASR | 76.67% | 2.58% |
| humanized/teacher | SenseVoice | 95.00% | 0.76% |
| humanized/teacher | WeNet | — | — |
| humanized/teacher | Qwen3-ASR | — | — |
| myvoice/director | FunASR | 70.00% | 3.44% |
| myvoice/director | SenseVoice | 66.67% | 4.58% |
| myvoice/director | WeNet | — | — |
| myvoice/director | Qwen3-ASR | — | — |
| myvoice/principal | FunASR | 66.67% | 4.15% |
| myvoice/principal | SenseVoice | 66.67% | 4.95% |
| myvoice/principal | WeNet | — | — |
| myvoice/principal | Qwen3-ASR | — | — |
| myvoice/staff | FunASR | 90.00% | 0.97% |
| myvoice/staff | SenseVoice | 86.67% | 1.62% |
| myvoice/staff | WeNet | — | — |
| myvoice/staff | Qwen3-ASR | — | — |
| myvoice/teacher | FunASR | 73.33% | 3.19% |
| myvoice/teacher | SenseVoice | 73.33% | 3.03% |
| myvoice/teacher | WeNet | — | — |
| myvoice/teacher | Qwen3-ASR | — | — |
| standard/director | FunASR | 76.67% | 2.44% |
| standard/director | SenseVoice | 93.33% | 0.86% |
| standard/director | WeNet | — | — |
| standard/director | Qwen3-ASR | — | — |
| standard/principal | FunASR | 86.67% | 1.74% |
| standard/principal | SenseVoice | 91.67% | 1.20% |
| standard/principal | WeNet | — | — |
| standard/principal | Qwen3-ASR | — | — |
| standard/staff | FunASR | 90.00% | 1.13% |
| standard/staff | SenseVoice | 88.33% | 1.29% |
| standard/staff | WeNet | — | — |
| standard/staff | Qwen3-ASR | — | — |
| standard/teacher | FunASR | 73.33% | 2.88% |
| standard/teacher | SenseVoice | 95.00% | 0.76% |
| standard/teacher | WeNet | — | — |
| standard/teacher | Qwen3-ASR | — | — |
| tts-baseline | FunASR | — | — |
| tts-baseline | SenseVoice | — | — |
| tts-baseline | WeNet | 21.53% | 13.83% |
| tts-baseline | Qwen3-ASR | — | — |

### Availability
All four engine result files are present.
