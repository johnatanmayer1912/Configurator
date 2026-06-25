from dataclasses import dataclass

@dataclass
class VLAN:
    id: int
    name: str

    def __post_init__(self):
        # Basic validation
        if not (1 <= self.id <= 4094):
            raise ValueError(f"VLAN ID {self.id} must be between 1 and 4094")
