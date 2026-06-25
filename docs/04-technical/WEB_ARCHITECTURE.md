# Technical Architecture

See also: [ARCHITECTURE.md](../ARCHITECTURE.md) (full module map)

## Web-first delivery (v2.3)

```
web_launcher.py
    └── FastAPI (api/main.py)
            ├── GET  /catalog          → YAML data (versions, scenarios, features)
            ├── POST /scenario/preview → ScenarioEngine dry-run
            ├── POST /scenario/generate→ Pipeline + optional vPC pair
            ├── POST /validate, /generate-config (advanced manual)
            └── GET  /history          → artifact vault

ScenarioEngine → IntentEngine → Device dataclass
ConfigurationPipeline → ConfigEngine → ConfigRenderer (Jinja2)
```

## Offline exe bundling

PyInstaller one-file includes:

- `templates/`, `static/`, `data/`, `hardware_profiles.yaml`, `VERSION`
- `--collect-all` for uvicorn, fastapi, pydantic, starlette, anyio

Build: `python utils/build_exe.py`

## Data-driven UI

The web wizard loads `/catalog` at startup. No hardcoded scenarios in HTML — all from `data/*.yaml`.
