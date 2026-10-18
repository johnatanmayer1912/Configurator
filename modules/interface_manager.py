from typing import List
from models.nexus_models import NexusModel
from models.interface_model import Interface

def get_vpc_ports(model: str):
    # Returns: {'peer_link': [list of ports], 'keepalive': [list of ports]}
    if model == NexusModel.N93180YC_EX:
        return {'peer_link': ['Ethernet1/51', 'Ethernet1/52'], 'keepalive': ['Ethernet1/49', 'Ethernet1/50']} 
    elif model == NexusModel.N9336C_FX2:
        return {'peer_link': ['Ethernet1/35', 'Ethernet1/36'], 'keepalive': ['Ethernet1/33', 'Ethernet1/34']}
    elif model == NexusModel.N9348GC_FXP:
        return {'peer_link': ['Ethernet1/51', 'Ethernet1/52'], 'keepalive': ['Ethernet1/47', 'Ethernet1/48']}
    return None

def generate_interfaces_generic(c_1g: int, c_10g: int, c_40g: int, exclude_ports: List[str] = []) -> List[Interface]:
    interfaces = []
    idx = 1
    
    for _ in range(c_1g):
        name = f"Ethernet1/{idx}"
        if name not in exclude_ports:
            interfaces.append(Interface(name=name, mode="access", description="1G Port", shutdown=False))
        idx += 1
        
    for _ in range(c_10g):
        name = f"Ethernet1/{idx}"
        if name not in exclude_ports:
            interfaces.append(Interface(name=name, mode="access", description="10G Port", shutdown=False))
        idx += 1
        
    for _ in range(c_40g):
        name = f"Ethernet1/{idx}"
        if name not in exclude_ports:
            interfaces.append(Interface(name=name, mode="access", description="40G Uplink", shutdown=False))
        idx += 1
        
    return interfaces

def generate_interfaces_model(model: str, exclude_ports: List[str] = []) -> List[Interface]:
    interfaces = []
    
    if model == NexusModel.N93180YC_EX:
        # 1-48: 10/25G SFP+
        for i in range(1, 49):
            name = f"Ethernet1/{i}"
            if name not in exclude_ports:
                interfaces.append(Interface(name=name, mode="access", description="Host Port (10/25G)"))
        # 49-54: 40/100G QSFP28
        for i in range(49, 55):
            name = f"Ethernet1/{i}"
            if name not in exclude_ports:
                interfaces.append(Interface(name=name, mode="trunk", description="Uplink (40/100G)"))
                
    elif model == NexusModel.N9336C_FX2:
        # 1-36: 40/100G QSFP28
        for i in range(1, 37):
            name = f"Ethernet1/{i}"
            if name not in exclude_ports:
                interfaces.append(Interface(name=name, mode="access", description="Port (40/100G)"))
                
    elif model == NexusModel.N9348GC_FXP:
        # 1-48: 100M/1G Base-T
        for i in range(1, 49):
            name = f"Ethernet1/{i}"
            if name not in exclude_ports:
                interfaces.append(Interface(name=name, mode="access", description="Host Port (1G Base-T)"))
        # 49-52: 10/25G SFP28
        for i in range(49, 53):
            name = f"Ethernet1/{i}"
            if name not in exclude_ports:
                interfaces.append(Interface(name=name, mode="trunk", description="Uplink (10/25G)"))
        # 53-54: 40/100G QSFP28
        for i in range(53, 55):
            name = f"Ethernet1/{i}"
            if name not in exclude_ports:
                interfaces.append(Interface(name=name, mode="trunk", description="Uplink (40/100G)"))
    
    return interfaces
