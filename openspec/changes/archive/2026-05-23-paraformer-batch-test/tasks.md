## 1. Category inference from directory name

- [x] 1.1 Add `infer_category(file_path)` function: extract parent directory name, match `^[A-F]-` prefix → use as category, else `tts-baseline`
- [x] 1.2 Add `category` field to each result dict in `run_batch()`
- [x] 1.3 Add `by_category` grouping in summary output (alongside existing `by_version`, `by_role`)

## 2. Hotword file support

- [x] 2.1 Create `config/hotwords.txt` with preset school management hotwords (出勤率 合格率 平均分 升学率 及格率 三年级 二年级一班 教务处 后勤处 德育处 教学楼A栋 张老师 李校长 导出报表 月视图 周视图)
- [x] 2.2 Add `load_hotwords_file(path)` function: read file, strip whitespace, skip empty lines, return list
- [x] 2.3 In `--compare` mode, load hotwords from `config/hotwords.txt` if no `--hotword` args given; warn and use empty list if file missing

## 3. Compare mode: multi-round orchestration

- [x] 3.1 Add `--compare` flag to argparse
- [x] 3.2 Implement `run_compare(args)` function: iterate modes=[2pass, online, offline] × hotword_configs=[none, from_file], calling existing `run_batch()` for each combination
- [x] 3.3 Print round progress: `[Round 2/6] mode=online hotword=none ...`
- [x] 3.4 Handle per-round errors gracefully: catch exception, mark round as failed, continue to next round
- [x] 3.5 Write per-round JSON to `verification-2-self/results/paraformer-{mode}-{hotword|no-hotword}.json`

## 4. Markdown report generation

- [x] 4.1 Implement `generate_report(rounds, output_path)` function that writes a Markdown file
- [x] 4.2 Test configuration section: ws_url, modes tested, hotwords used, manifest paths, total count
- [x] 4.3 Mode comparison table: rows=metrics (CER, norm_exact_match_rate, avg_final_latency_ms, p95_final_latency_ms), columns=modes, values from hotword=on rounds
- [x] 4.4 Hotword effect table: rows=metrics, columns=without-hotword / with-hotword / improvement%, values from 2pass mode
- [x] 4.5 Category breakdown table (2pass + hotword): rows=categories, columns=CER / exact_match_rate / worst case
- [x] 4.6 Worst 15 cases table: id / expected / actual / CER, from 2pass+hotword round
- [x] 4.7 Write report to `verification-2-self/results/paraformer-report.md`

## 5. Backward compatibility

- [x] 5.1 When `--compare` is not set, `main()` calls existing `run_batch()` path unchanged
- [x] 5.2 Single-run mode still adds `category` field to result dicts and JSON/CSV output
- [x] 5.3 Single-run mode still prints `by_category` in terminal summary

## 6. Verify

- [x] 6.1 Run `python test_funasr_batch.py --mode 2pass --limit 3` to confirm single-run still works
- [x] 6.2 Run `python test_funasr_batch.py --compare --limit 2` to confirm compare mode produces 6 rounds + report
- [x] 6.3 Check `verification-2-self/results/paraformer-report.md` renders correctly
