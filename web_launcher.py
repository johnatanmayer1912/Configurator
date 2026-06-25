import uvicorn
import socket
import webbrowser
import threading
import time
import os
import sys
import signal
import secrets
import traceback
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from utils.instance_control import (
    DEFAULT_PORT,
    describe_port_conflict,
    remove_pid_file,
    stop_listeners_on_port,
    write_pid_file,
)


def bootstrap_log(message: str) -> None:
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", "startup_bootstrap.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} | {message}\n")


def fatal_startup_error(message: str, error: Exception) -> None:
    detail = f"{message}: {error}\n{traceback.format_exc()}"
    bootstrap_log(detail)
    print(detail)


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def build_web_app():
    from api.main import app
    from utils.web_logger import logger

    static_dir = get_resource_path("static")
    template_index = get_resource_path("templates/web/index.html")

    logger.info(f"Initializing Static Assets from: {static_dir}")
    bootstrap_log(f"Initializing static assets from {static_dir}")
    if not os.path.exists(static_dir):
        logger.error(f"CRITICAL: Static directory not found at {static_dir}")
        raise FileNotFoundError(f"Static directory missing: {static_dir}")

    if not os.path.exists(template_index):
        logger.error(f"CRITICAL: UI template not found at {template_index}")
        raise FileNotFoundError(f"UI template missing: {template_index}")

    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    admin_page = get_resource_path("templates/web/admin.html")

    @app.get("/")
    async def read_index():
        return FileResponse(template_index)

    @app.get("/admin")
    async def read_admin():
        if os.path.exists(admin_page):
            return FileResponse(admin_page)
        raise FileNotFoundError("Admin template missing")

    return app, logger


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def open_browser(url: str, logger) -> None:
    time.sleep(2)
    if is_port_in_use(DEFAULT_PORT):
        logger.info(f"Opening browser at: {url}")
        webbrowser.open(url)
    else:
        logger.warning("Browser open skipped — server is no longer listening.")


def parse_cli_flags(argv: list[str]) -> dict:
    flags = {arg.lower() for arg in argv[1:]}
    return {
        "stop": "--stop" in flags or "stop" in flags,
        "replace": "--replace" in flags or os.getenv("NXOS_REPLACE_INSTANCE", "").strip() in {"1", "true", "yes"},
        "no_browser": "--no-browser" in flags or os.getenv("NXOS_NO_BROWSER", "").strip() in {"1", "true", "yes"},
    }


def run_server() -> None:
    port = DEFAULT_PORT
    host = "127.0.0.1"
    bootstrap_log(
        f"Runtime info: python={sys.version.split()[0]} frozen={hasattr(sys, '_MEIPASS')} cwd={os.getcwd()}"
    )
    # Token authentication removed for offline use
    url = f"http://{host}:{port}/"

    app, logger = build_web_app()

    from utils.version import get_app_version

    version = get_app_version()

    logger.info("--------------------------------------------------")
    logger.info(f"     NX-OS CONFIGURATION AUTHORITY ({version})")
    logger.info("           Web Platform — Offline Ready")
    logger.info("--------------------------------------------------")
    bootstrap_log("Application banners and logger initialized.")

    flags = parse_cli_flags(sys.argv)
    if flags["replace"] and is_port_in_use(port):
        stopped = stop_listeners_on_port(port)
        message = f"Replaced prior instance on port {port}: PIDs {stopped or 'none'}"
        logger.warning(message)
        bootstrap_log(message)
        time.sleep(0.75)

    if is_port_in_use(port):
        message = describe_port_conflict(port)
        logger.error(message)
        bootstrap_log(message)
        print(message)
        sys.exit(1)

    write_pid_file()

    server_holder: dict = {}

    def request_shutdown() -> None:
        server = server_holder.get("server")
        if server is not None:
            server.should_exit = True
            if hasattr(server, "force_exit"):
                server.force_exit = True

        def hard_exit() -> None:
            time.sleep(2.0)
            bootstrap_log("Hard exit after shutdown request.")
            remove_pid_file()
            os._exit(0)

        threading.Thread(target=hard_exit, daemon=True).start()

    app.state.request_shutdown = request_shutdown

    if not flags["no_browser"]:
        threading.Thread(target=open_browser, args=(url, logger), daemon=True).start()

    logger.info(f"Starting Production Server at http://{host}:{port}")
    logger.info(f"Session URL (bookmark this tab): {url}")
    bootstrap_log(f"Starting uvicorn server on {host}:{port}")
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    server_holder["server"] = server

    def handle_console_stop(signum, frame) -> None:
        logger.info("Console stop signal received — shutting down.")
        bootstrap_log(f"Signal {signum} received.")
        request_shutdown()

    signal.signal(signal.SIGINT, handle_console_stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_console_stop)

    try:
        server.run()
    finally:
        remove_pid_file()


if __name__ == "__main__":
    try:
        flags = parse_cli_flags(sys.argv)
        if flags["stop"]:
            stopped = stop_listeners_on_port(DEFAULT_PORT)
            if stopped:
                print(f"Stopped NX-OS Configurator (PID(s): {', '.join(str(p) for p in stopped)})")
            else:
                print("No listener found on port 9000.")
            sys.exit(0)
        run_server()
    except Exception as e:
        remove_pid_file()
        fatal_startup_error("SERVER CRASH", e)
        sys.exit(1)
