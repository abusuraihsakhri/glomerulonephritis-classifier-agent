# Glomerulonephritis Classifier Agent

**Status:** Generic threshold-rule demonstration, not a validated glomerulonephritis classifier. The current code does **not** interpret renal light microscopy, immunofluorescence, electron microscopy or serology to establish a GN diagnosis. The demonstration thresholds are not KDIGO/KDOQI diagnostic criteria. **Do not use for clinical decisions or patient data.**

## What works

- `agents/`: three deterministic metric/descriptor workers, Pydantic validation, FastAPI endpoints, an in-process HMAC-SHA256 audit chain, and heuristic PHI-pattern screening.
- `web/index.html`: entirely local JavaScript demonstration of the same three worker conditions with JSON export. No backend, Python, tracking, or remote scripts.
- `glomerulo_mind.py` and `glomerulonephritis_classifier_agent/`: separate legacy implementations, retained for compatibility; their thresholds and outputs differ from the main service.
- `enrichment.py`: additional generic scalar-threshold examples; feature names do not imply implemented GN/eGFR/dialysis algorithms.

## Start the Python service

CI tests Python 3.10, 3.11 and 3.12.

```bash
python -m pip install -e ".[dev]"
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
python cli.py audit --task-id TASK-DEMO-01 --target SYN-001 --primary 28 --secondary 13
python cli.py serve --host 127.0.0.1 --port 8000
```

In another terminal, open `http://127.0.0.1:8000/docs` for interactive API documentation. Available paths are `GET /health`, `POST /api/audit`, `POST /api/chat`, `GET /api/audit/logs`, `GET /metrics` (JSON), and `GET /metrics/prometheus` (Prometheus text). The chat endpoint is a deterministic test stub, not remote LLM inference.

For synthetic CSV processing:

```bash
python cli.py batch --input synthetic_tasks.csv --output results.csv
```

Expected CSV fields: `task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag`. Boolean values accept `true/false`, `yes/no` and `1/0` (case-insensitive).

The older package entry point is still available as `python -m glomerulonephritis_classifier_agent.cli --help` or after installation as `glomerulonephritis-classifier-engine --help`.

## Browser demo

Open `web/index.html` locally in a modern browser. Enter only synthetic IDs and generic metrics, select a status, and click **Evaluate rules**. The output can be exported as JSON. No browser-Python runtime is required; all calculations are client-side JavaScript.

The browser mirrors `agents/workers.py`: primary metric >25, secondary metric >12 or the explicit critical flag, and selected discordance descriptors. These are software test conditions, not GN diagnostic rules. There is no HMAC ledger in the browser demo.

## Security and privacy

- Set `AUDIT_SECRET_KEY` to a securely generated value of at least 16 characters. Never commit operational secrets. The chain exists only in process memory; it is not a durable or immutable audit log.
- The HMAC verifier authenticates logged entry fields and chain links, but audit keys and hosting require independent operational controls.
- PHI screening uses a limited list of regular expressions and does **not** establish HIPAA de-identification or absence of personal data. Do not process real patient information.
- The HTTP service has no user authentication and must not be exposed as a clinical production service. By default the CLI binds to localhost.
- Provider aliases (`ollama`, `claude`, `openai`) are currently deterministic mocks; no inference integration is implemented.

For container use, set `AUDIT_SECRET_KEY` in your environment before running `docker compose up --build`. The service listens on port 8000.

## Tests

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m compileall -q agents glomerulonephritis_classifier_agent
node web/smoke.test.cjs
```

CI runs the tests across Python 3.10–3.12 and checks the browser demo with Node.js. GitHub Pages can host only the independent static browser demo, not this FastAPI service.

**License:** [MIT](LICENSE).
