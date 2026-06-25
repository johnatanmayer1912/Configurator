"""
Build offline-capable single-file exe for the web-based NX-OS Configurator.
Bundles templates, static assets, data catalogs, and hardware profiles.
"""
import datetime
import os
import subprocess
import sys


def read_version() -> str:
    try:
        from utils.version import get_app_version
        return get_app_version()
    except Exception:
        if os.path.exists("VERSION"):
            with open("VERSION", encoding="utf-8") as fh:
                return fh.read().strip()
        return "2.7.0"


def run_build(*, skip_qa_gate: bool = False):
    if not skip_qa_gate and os.environ.get("NXOS_SKIP_QA_GATE") != "1":
        print(">>> Running enterprise QA gate (pre-exe mandatory stages)...")
        gate = subprocess.run(
            [sys.executable, "scripts/enterprise_qa_gate.py"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        if gate.returncode != 0:
            print("ABORT: Enterprise QA gate failed. Fix tests or set NXOS_SKIP_QA_GATE=1 to override.")
            sys.exit(gate.returncode)

    version = read_version()
    date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    name = f"NXOS_Configurator_Web_v{version}_{date_str}"

    hidden_imports = [
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "fastapi",
        "starlette",
        "starlette.routing",
        "starlette.responses",
        "starlette.staticfiles",
        "pydantic",
        "pydantic_core",
        "yaml",
        "jinja2",
        "jinja2.ext",
        "email_validator",
        "anyio",
        "anyio._backends",
        "anyio._backends._asyncio",
        "sniffio",
        "httptools",
        "websockets",
        "watchfiles",
        "h11",
        "click",
    ]

    datas = [
        ("templates", "templates"),
        ("static", "static"),
        ("data", "data"),
        ("hardware_profiles.yaml", "."),
        ("VERSION", "."),
        ("docs", "docs"),
    ]

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--console",
        "--exclude-module",
        "tkinter",
        "--exclude-module",
        "matplotlib",
        "--exclude-module",
        "pytest",
        "--name",
        name,
        "--collect-all",
        "uvicorn",
        "--collect-all",
        "fastapi",
        "--collect-all",
        "starlette",
        "--collect-all",
        "pydantic",
        "--collect-all",
        "anyio",
    ]

    for module in hidden_imports:
        cmd.extend(["--hidden-import", module])

    for src, dst in datas:
        cmd.extend(["--add-data", f"{src};{dst}"])

    cmd.append("web_launcher.py")

    print(f">>> Building offline web exe: {name}")
    subprocess.run(cmd, check=True)
    print(f"SUCCESS: dist/{name}.exe")
    print("Run the exe — browser opens at http://127.0.0.1:9000 (fully offline).")


if __name__ == "__main__":
    run_build()
