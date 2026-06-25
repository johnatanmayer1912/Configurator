import re
from typing import List

def expand_interface_range(range_str: str) -> List[str]:
    """
    Expands NX-OS interface ranges into a list of individual interfaces.
    Example inputs:
      "Eth1/1-4" -> ["Eth1/1", "Eth1/2", "Eth1/3", "Eth1/4"]
      "Eth1/1, Eth1/3" -> ["Eth1/1", "Eth1/3"]
      "Eth1/1-2, Eth1/10-12" -> ["Eth1/1", "Eth1/2", "Eth1/10", "Eth1/11", "Eth1/12"]
    """
    interfaces: List[str] = []
    seen = set()
    # Split by commas first
    parts = [p.strip() for p in range_str.split(",")]
    
    for part in parts:
        # Check for range pattern: (Name)(Slot)/(Start)-(End)
        # e.g., Ethernet1/1-4 or Eth1/1-4
        match = re.match(r"([a-zA-Z]+)(\d+/\d+)-(\d+)", part)
        if match:
            prefix = match.group(1)
            slot_base = match.group(2).split("/")[0]
            start = int(match.group(2).split("/")[1])
            end = int(match.group(3))
            if end < start:
                start, end = end, start

            for i in range(start, end + 1):
                candidate = f"{prefix}{slot_base}/{i}"
                if candidate not in seen:
                    seen.add(candidate)
                    interfaces.append(candidate)
        else:
            # Single interface
            if part:
                normalized = part.strip()
                if normalized not in seen:
                    seen.add(normalized)
                    interfaces.append(normalized)
                
    return interfaces

if __name__ == "__main__":
    # Test cases
    print(expand_interface_range("Eth1/1-4"))
    print(expand_interface_range("Eth1/1, Eth1/3"))
    print(expand_interface_range("Eth1/1-2, Eth1/10-12"))
