# Submission Guide

Complete this template before zipping your submission. Keep the file at the
project root.

## Team details
- Team name: Sentinel Innovators
- Members: Team Lead (AI Architect), Data Engineer, Full-Stack Developer, ML Specialist
- Primary contact email: team01.sentinel@innovatex.com

## Judge run command
Judges will `cd evidence/executables/` and run **one command** on Ubuntu 24.04:

```
python3 run_demo.py
```

The script automatically:
1. Installs dependencies (flask, flask-cors)
2. Locates data directory (auto-detects or use: `python3 run_demo.py /path/to/data/input`)
3. Runs event detection engine with all algorithms
4. Generates events.jsonl in both `evidence/output/test/` and `evidence/output/final/`
5. Creates summary.json with statistics
6. Offers to start the dashboard at http://localhost:5000

All artifacts are written to `./results/` and automatically copied to `../output/test/` and `../output/final/`.

## Checklist before zipping and submitting
- Algorithms tagged with `# @algorithm Name | Purpose` comments: ✅ YES - 9 algorithms tagged in algorithms.py
- Evidence artefacts present in `evidence/`: ✅ YES - events.jsonl, summary.json, screenshots in evidence/
- Source code complete under `src/`: ✅ YES - All modules with comprehensive documentation
