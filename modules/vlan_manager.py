from typing import List
from models.vlan_model import VLAN

def generate_vlans(vlans: List[VLAN]):
    if not vlans: return ""
    lines = ["\n! VLAN Configuration"]
    for vlan in vlans:
        lines.append(f"vlan {vlan.id}")
        lines.append(f"  name {vlan.name}")
    return "\n".join(lines)
