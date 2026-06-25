"""Release engineer — offline exe bundle and VERSION discipline."""

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "templates" / "web"
STATIC = ROOT / "static"


@pytest.mark.mandatory
def test_version_file_present_and_semver():
    version_path = ROOT / "VERSION"
    assert version_path.is_file()
    version = version_path.read_text(encoding="utf-8").strip()
    parts = version.split(".")
    assert len(parts) == 3, "VERSION must be semver major.minor.patch"
    assert all(p.isdigit() for p in parts)


@pytest.mark.mandatory
def test_build_exe_datas_include_offline_assets():
    build_exe = ROOT / "utils" / "build_exe.py"
    src = build_exe.read_text(encoding="utf-8")
    tree = ast.parse(src)
    datas: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "datas":
                    if isinstance(node.value, ast.List):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Tuple) and elt.elts:
                                if isinstance(elt.elts[0], ast.Constant):
                                    datas.append(str(elt.elts[0].value))
    required = {"templates", "static", "data", "hardware_profiles.yaml", "VERSION"}
    assert required.issubset(set(datas)), f"build_exe datas missing: {required - set(datas)}"


@pytest.mark.mandatory
def test_web_launcher_has_replace_and_stop_flags():
    src = (ROOT / "web_launcher.py").read_text(encoding="utf-8")
    assert "--replace" in src
    assert "--stop" in src
    assert "instance_control" in src


@pytest.mark.mandatory
def test_stop_script_exists():
    assert (ROOT / "scripts" / "stop_configurator.ps1").is_file()


@pytest.mark.mandatory
def test_all_referenced_static_assets_exist():
    """Every /static and icon asset referenced by the served pages must exist locally.

    Offline guarantee: a missing local asset = broken page with no network fallback.
    """
    pages = [WEB / "index.html", WEB / "admin.html"]
    ref_re = re.compile(r'(?:src|href)\s*=\s*["\'](/static/[^"\']+)["\']')
    missing = []
    for page in pages:
        html = page.read_text(encoding="utf-8")
        for rel in ref_re.findall(html):
            asset = ROOT / rel.lstrip("/")
            if not asset.is_file():
                missing.append(f"{page.name} -> {rel}")
    assert not missing, f"Referenced offline assets missing: {missing}"


@pytest.mark.mandatory
def test_no_external_resource_references_for_offline():
    """No CDN/web-font/external stylesheet or script references anywhere in the UI.

    These would silently fail (or hang) in an air-gapped environment.
    """
    banned = [
        'href="http', "href='http",
        'src="http', "src='http",
        "fonts.googleapis", "fonts.gstatic",
        "cdn.jsdelivr", "cdnjs.cloudflare", "unpkg.com",
        "@import url(http", "url(http",
        "preconnect",
    ]
    offenders = []
    targets = list(WEB.rglob("*.html")) + list(STATIC.rglob("*.css")) + list(STATIC.rglob("*.js")) + list(STATIC.rglob("*.html"))
    for path in targets:
        text = path.read_text(encoding="utf-8")
        for token in banned:
            if token in text:
                offenders.append(f"{path.name}: {token}")
    assert not offenders, f"External references break offline use: {offenders}"


@pytest.mark.mandatory
def test_js_fetches_are_relative_only():
    """All fetch() calls target the local server via relative paths (offline-safe)."""
    offenders = []
    fetch_re = re.compile(r"""fetch\(\s*[`"']([^`"')]+)""")
    for js in STATIC.rglob("*.js"):
        for url in fetch_re.findall(js.read_text(encoding="utf-8")):
            if url.startswith("http://") or url.startswith("https://") or url.startswith("//"):
                offenders.append(f"{js.name}: {url}")
    assert not offenders, f"Absolute/external fetch() breaks offline use: {offenders}"


@pytest.mark.mandatory
def test_app_code_has_no_outbound_network_calls():
    """Program packages must not import internet clients (offline integrity).

    Local socket bind (port check) is allowed; outbound HTTP clients are not.
    """
    banned = ("import requests", "import httpx", "urllib.request", "urlopen", "smtplib")
    offenders = []
    for pkg in ("api", "core", "utils", "pipelines", "models"):
        pkg_dir = ROOT / pkg
        if not pkg_dir.exists():
            continue
        for py in pkg_dir.rglob("*.py"):
            text = py.read_text(encoding="utf-8")
            for token in banned:
                if token in text:
                    offenders.append(f"{py.relative_to(ROOT)}: {token}")
    assert not offenders, f"Outbound network usage in app code: {offenders}"


@pytest.mark.mandatory
def test_fonts_use_system_fallbacks_only():
    """CSS font stacks must end in a generic family so they render with no web fonts."""
    css = (STATIC / "styles.css").read_text(encoding="utf-8")
    assert "@font-face" not in css, "No bundled/remote @font-face — rely on system fonts"
    for m in re.findall(r"font-family:\s*([^;]+);", css):
        stack = m.strip().lower()
        assert any(stack.endswith(g) for g in ("sans-serif", "serif", "monospace")), (
            f"font stack must end with a generic family: {m.strip()}"
        )


@pytest.mark.mandatory
def test_hardware_profiles_vpc_ports_for_tier_models():
    import yaml

    hw = yaml.safe_load((ROOT / "hardware_profiles.yaml").read_text(encoding="utf-8"))
    profiles = {p["display_name"]: p for p in hw.get("profiles", [])}
    assert profiles["Nexus 9336C-FX2"].get("vpc_peer_link")
    assert profiles["Nexus 93180YC-EX"].get("vpc_peer_link")
    assert profiles["Nexus 9348GC-FXP"].get("vpc_peer_link")
