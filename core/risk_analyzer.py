from typing import List, Dict


class RiskAnalyzer:
    """Context-aware risk scoring for generated NX-OS CLI."""

    SAFE_PREFIXES = ("!", "banner", "description", "name ")

    def __init__(self):
        self.risk_patterns = {
            "CRITICAL": ["reload", "reboot", "write erase", "no feature vpc"],
            "HIGH": ["vpc domain", "no vpc", "shutdown"],
            "MEDIUM": ["spanning-tree", "storm-control", "username ", "channel-group 1 mode"],
            "LOW": ["hostname", "ntp server", "logging server", "snmp-server location", "interface port-channel"],
        }

    def analyze(self, config_lines: List[str]) -> Dict:
        findings = []
        overall_score = "LOW"

        for line in config_lines:
            line_clean = line.strip()
            if not line_clean or line_clean.startswith("!"):
                continue
            lower = line_clean.lower()

            if lower.startswith("no shutdown"):
                continue
            if lower.startswith("vlan ") and " name " not in lower:
                continue

            for level, patterns in self.risk_patterns.items():
                for pattern in patterns:
                    if pattern in lower:
                        findings.append({
                            "level": level,
                            "command": line_clean,
                            "reason": f"Matches risk pattern: '{pattern}'",
                        })
                        if self._is_higher(level, overall_score):
                            overall_score = level
                        break

        return {"overall_risk": overall_score, "findings": findings}

    def _is_higher(self, level1: str, level2: str) -> bool:
        order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        return order.index(level1) > order.index(level2)

    def generate_report(self, analysis: Dict) -> str:
        report = [
            "==========================================",
            "       CONFIGURATION RISK ASSESSMENT      ",
            "==========================================",
            f"OVERALL RISK LEVEL: {analysis['overall_risk']}",
            f"TOTAL FINDINGS: {len(analysis['findings'])}",
            "------------------------------------------",
        ]
        if not analysis["findings"]:
            report.append("No high-risk commands detected.")
        else:
            for f in analysis["findings"]:
                report.append(f"[{f['level']}] {f['command']}")
                report.append(f"   ↳ {f['reason']}")
        report.append("==========================================")
        return "\n".join(report)
