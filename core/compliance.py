import re
from typing import List, Dict
from models.device_model import Device

class ComplianceEngine:
    def __init__(self):
        self.findings = [] # Each finding: {"level": "warning|error", "message": "..."}

    def audit(self, device: Device) -> List[Dict]:
        """
        Audits a Device model against institutional compliance rules.
        """
        self.findings = []
        
        # 1. VLAN Naming Convention
        # Rule: VLAN names should not contain spaces, use UPPER_CASE
        for vlan in device.vlans:
            if " " in vlan.name:
                self.findings.append({
                    "level": "warning",
                    "message": f"VLAN {vlan.id} name '{vlan.name}' contains spaces. Remediation: use UPPER_CASE with underscores (example: PROD_SERVERS)."
                })
            elif not vlan.name.isupper():
                self.findings.append({
                    "level": "warning",
                    "message": f"VLAN {vlan.id} name '{vlan.name}' is not uppercase. Remediation: normalize to UPPER_CASE for naming consistency."
                })

        # 2. Reserved VLAN Ranges
        # NX-OS reserved: 3968-4047, 4094
        reserved_ranges = range(3968, 4048)
        for vlan in device.vlans:
            if vlan.id in reserved_ranges or vlan.id == 4094:
                self.findings.append({
                    "level": "error",
                    "message": f"VLAN {vlan.id} is reserved in NX-OS (3968-4047 or 4094). Remediation: choose a service VLAN outside reserved ranges."
                })

        # 3. Management IP Format
        if "/" not in device.mgmt_ip:
            self.findings.append({
                "level": "error",
                "message": "Management IP must use CIDR notation (e.g., /24). Remediation: enter an address like 10.10.10.10/24."
            })

        # 4. Hostname Convention
        # Rule: Must be alphanumeric + hyphens
        if not re.match(r"^[a-zA-Z0-9-]+$", device.hostname):
            self.findings.append({
                "level": "error",
                "message": f"Hostname '{device.hostname}' contains invalid characters. Remediation: use letters, numbers, and hyphens only."
            })

        return self.findings
