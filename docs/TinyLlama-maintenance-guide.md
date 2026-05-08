# TinyLlama Maintenance Guide

## Purpose
This guide keeps TinyLlama usage stable on low disk and low RAM systems in wiki-linux.

## Recommended Model
- `tinyllama:latest` for quick local prompts
- Keep only one TinyLlama variant unless you need quantization comparisons

## Daily Health Checks
Run:

```bash
ollama ps
ollama list
curl -fsS http://127.0.0.1:11434/api/tags | python3 -m json.tool | head -40
```

## Disk Hygiene
List model blob usage:

```bash
du -sh ~/.ollama/models
find ~/.ollama/models/blobs -type f -printf "%s %p\n" | sort -nr | head -20
```

Remove incomplete downloads safely:

```bash
find ~/.ollama/models/blobs -type f -name "*.partial" -delete
```

Remove unused models by name (preferred):

```bash
ollama rm <model-name>
```

## Performance Tuning
- Keep prompts short when disk or RAM is constrained.
- Avoid running multiple model sessions in parallel.
- Restart Ollama if response latency grows.

```bash
systemctl --user restart ollama
```

## Integration with wiki-linux
- Use TinyLlama for quick summarization and triage.
- Use larger models only when quality is required.
- Prefer writing intermediate outputs to `user/notes/` as markdown.

## Failure Recovery
If Ollama fails to start:

```bash
systemctl --user status ollama
journalctl --user -u ollama -n 100 --no-pager
```

If disk pressure causes failures:
1. Remove partial blobs
2. Remove unused large models with `ollama rm`
3. Run boot cleanup script:

```bash
python3 ~/Documents/wiki-linux/wiki-linux/bin/wiki-boot-cleanup.py
```

## Monthly Cleanup
```bash
ollama list
# Remove models you did not use in the last month
# ollama rm <model-name>
```
