import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime

# Models
from models.nexus_models import NexusModel
from models.vlan_model import VLAN
from models.interface_model import Interface
from models.device_model import Device, VPCConfig

# Managers
from modules.interface_manager import generate_interfaces_generic, generate_interfaces_model, get_vpc_ports
from core.engine import ConfigEngine
from core.validator import ValidationError
from pipelines.build_pipeline import ConfigurationPipeline
from utils.logger import get_logger

logger = get_logger("GUI")

class NexusConfiguratorGUI:
    def __init__(self, root):
        self.root = root
        
        # Pipeline
        self.pipeline = ConfigurationPipeline()
        
        self.root.title(f"Configuration Authority System - v{self.pipeline.version}")
        self.root.geometry("1100x950")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.mode_var = tk.StringVar(value="Standalone")
        self.model_var = tk.StringVar(value=NexusModel.GENERIC)
        
        # Admin User Variables
        self.admin_user_var = tk.StringVar(value="admin")
        self.admin_pass_var = tk.StringVar()
        
        # Common Variables
        self.int_1g_var = tk.StringVar(value="0")
        self.int_10g_var = tk.StringVar(value="48")
        self.int_40g_var = tk.StringVar(value="6")
        
        # Standalone Variables
        self.sa_hostname_var = tk.StringVar()
        self.sa_mgmt_ip_var = tk.StringVar()
        self.sa_mgmt_gw_var = tk.StringVar()
        self.sa_motd_var = tk.StringVar(value="Authorized Access Only")
        
        # vPC Variables
        self.vpc_domain_id_var = tk.StringVar(value="1")
        self.vpc_kpa_vrf_var = tk.StringVar(value="management")
        self.vpc_pl_id_var = tk.StringVar(value="1")
        
        self.vpc_p_hostname_var = tk.StringVar()
        self.vpc_p_mgmt_ip_var = tk.StringVar()
        self.vpc_p_mgmt_gw_var = tk.StringVar()
        self.vpc_p_kpa_src_var = tk.StringVar() 
        
        self.vpc_s_hostname_var = tk.StringVar()
        self.vpc_s_mgmt_ip_var = tk.StringVar()
        self.vpc_s_mgmt_gw_var = tk.StringVar()
        self.vpc_s_kpa_src_var = tk.StringVar() 
        
        self._create_widgets()
        logger.info("Application initialized with models")

    def _create_widgets(self):
        # Header (Phase 12 Branding)
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill="x")
        ttk.Label(header_frame, text="CONFIGURATION AUTHORITY SYSTEM", font=("Segoe UI", 18, "bold"), foreground="#2980b9").pack(side="left")
        ttk.Label(header_frame, text=f"Build: {self.pipeline.version}", font=("Segoe UI", 10, "italic")).pack(side="right")
        
        # Top Frame: Mode and Model
        top_frame = ttk.LabelFrame(self.root, text="System Settings", padding=10)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(top_frame, text="Mode:").pack(side="left", padx=5)
        ttk.Radiobutton(top_frame, text="Standalone", variable=self.mode_var, value="Standalone", command=self._toggle_mode).pack(side="left", padx=5)
        ttk.Radiobutton(top_frame, text="vPC Pair", variable=self.mode_var, value="vPC Pair", command=self._toggle_mode).pack(side="left", padx=5)
        
        ttk.Separator(top_frame, orient="vertical").pack(side="left", padx=20, fill="y")
        
        ttk.Label(top_frame, text="Switch Model:").pack(side="left", padx=5)
        model_cb = ttk.Combobox(top_frame, textvariable=self.model_var, values=[
            NexusModel.GENERIC, NexusModel.N93180YC_EX, NexusModel.N9336C_FX2, NexusModel.N9348GC_FXP
        ], state="readonly", width=25)
        model_cb.pack(side="left", padx=5)
        model_cb.bind("<<ComboboxSelected>>", self._on_model_change)

        # User Credentials Frame
        auth_frame = ttk.LabelFrame(self.root, text="Admin Credentials (Role: network-admin)", padding=10)
        auth_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(auth_frame, text="Username:").pack(side="left", padx=5)
        ttk.Entry(auth_frame, textvariable=self.admin_user_var, width=20).pack(side="left", padx=5)
        
        ttk.Label(auth_frame, text="Password:").pack(side="left", padx=5)
        ttk.Entry(auth_frame, textvariable=self.admin_pass_var, width=20, show="*").pack(side="left", padx=5)
        
        # Interface Configuration (Generic Only)
        self.int_frame = ttk.LabelFrame(self.root, text="Interface Counts (Generic Mode Only)", padding=10)
        self.int_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid layout for ports
        ttk.Label(self.int_frame, text="1G Ports:").grid(row=0, column=0, padx=5)
        self.entry_1g = ttk.Entry(self.int_frame, textvariable=self.int_1g_var, width=10)
        self.entry_1g.grid(row=0, column=1, padx=5)
        
        ttk.Label(self.int_frame, text="10G Ports:").grid(row=0, column=2, padx=5)
        self.entry_10g = ttk.Entry(self.int_frame, textvariable=self.int_10g_var, width=10)
        self.entry_10g.grid(row=0, column=3, padx=5)
        
        ttk.Label(self.int_frame, text="40G Ports:").grid(row=0, column=4, padx=5)
        self.entry_40g = ttk.Entry(self.int_frame, textvariable=self.int_40g_var, width=10)
        self.entry_40g.grid(row=0, column=5, padx=5)
        
        # VLAN Configuration
        vlan_frame = ttk.LabelFrame(self.root, text="VLAN Configuration", padding=10)
        vlan_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(vlan_frame, text="Format: 'VLAN_ID VLAN_NAME' (e.g., '10 Data_Vlan'). One per line.").pack(anchor="w")
        self.vlan_input = tk.Text(vlan_frame, height=5, width=80)
        self.vlan_input.pack(fill="x", pady=5)
        ttk.Button(vlan_frame, text="Load VLANs from File", command=self._load_vlans).pack(anchor="e")
        
        # Device Specific Details
        self.details_frame = ttk.Frame(self.root)
        self.details_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self._create_standalone_widgets()
        self._create_vpc_widgets()
        
        self._toggle_mode()
        self._on_model_change()
        
        # Generate Button
        ttk.Button(self.root, text="Generate Configuration", command=self._generate_config).pack(pady=10)

    def _create_standalone_widgets(self):
        self.sa_frame = ttk.LabelFrame(self.details_frame, text="Standalone Settings", padding=10)
        
        ttk.Label(self.sa_frame, text="Hostname:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(self.sa_frame, textvariable=self.sa_hostname_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.sa_frame, text="Management IP:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(self.sa_frame, textvariable=self.sa_mgmt_ip_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.sa_frame, text="Management Gateway:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(self.sa_frame, textvariable=self.sa_mgmt_gw_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(self.sa_frame, text="MOTD:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(self.sa_frame, textvariable=self.sa_motd_var, width=50).grid(row=3, column=1, padx=5, pady=5)

    def _create_vpc_widgets(self):
        self.vpc_frame = ttk.LabelFrame(self.details_frame, text="vPC Pair Settings", padding=10)
        
        ttk.Label(self.vpc_frame, text="vPC Domain ID:").grid(row=0, column=0, sticky="e", padx=5)
        ttk.Entry(self.vpc_frame, textvariable=self.vpc_domain_id_var, width=10).grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(self.vpc_frame, text="Peer-Keepalive VRF:").grid(row=0, column=2, sticky="e", padx=5)
        ttk.Entry(self.vpc_frame, textvariable=self.vpc_kpa_vrf_var, width=15).grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(self.vpc_frame, text="Peer-Link PO ID:").grid(row=0, column=4, sticky="e", padx=5)
        ttk.Entry(self.vpc_frame, textvariable=self.vpc_pl_id_var, width=10).grid(row=0, column=5, sticky="w", padx=5)
        
        # Primary Device
        p_frame = ttk.LabelFrame(self.vpc_frame, text="Primary Device", padding=5)
        p_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=10)
        
        ttk.Label(p_frame, text="Hostname:").grid(row=0, column=0, sticky="e")
        ttk.Entry(p_frame, textvariable=self.vpc_p_hostname_var).grid(row=0, column=1, sticky="w")
        
        ttk.Label(p_frame, text="Mgmt IP:").grid(row=1, column=0, sticky="e")
        ttk.Entry(p_frame, textvariable=self.vpc_p_mgmt_ip_var).grid(row=1, column=1, sticky="w")
        
        ttk.Label(p_frame, text="Mgmt Gateway:").grid(row=2, column=0, sticky="e")
        ttk.Entry(p_frame, textvariable=self.vpc_p_mgmt_gw_var).grid(row=2, column=1, sticky="w")
        
        ttk.Label(p_frame, text="KPA Src IP:").grid(row=3, column=0, sticky="e")
        ttk.Entry(p_frame, textvariable=self.vpc_p_kpa_src_var).grid(row=3, column=1, sticky="w")
        
        # Secondary Device
        s_frame = ttk.LabelFrame(self.vpc_frame, text="Secondary Device", padding=5)
        s_frame.grid(row=1, column=3, columnspan=3, sticky="nsew", padx=5, pady=10)
        
        ttk.Label(s_frame, text="Hostname:").grid(row=0, column=0, sticky="e")
        ttk.Entry(s_frame, textvariable=self.vpc_s_hostname_var).grid(row=0, column=1, sticky="w")
        
        ttk.Label(s_frame, text="Mgmt IP:").grid(row=1, column=0, sticky="e")
        ttk.Entry(s_frame, textvariable=self.vpc_s_mgmt_ip_var).grid(row=1, column=1, sticky="w")

        ttk.Label(s_frame, text="Mgmt Gateway:").grid(row=2, column=0, sticky="e")
        ttk.Entry(s_frame, textvariable=self.vpc_s_mgmt_gw_var).grid(row=2, column=1, sticky="w")
        
        ttk.Label(s_frame, text="KPA Src IP:").grid(row=3, column=0, sticky="e")
        ttk.Entry(s_frame, textvariable=self.vpc_s_kpa_src_var).grid(row=3, column=1, sticky="w")

    def _toggle_mode(self):
        mode = self.mode_var.get()
        if mode == "Standalone":
            self.vpc_frame.pack_forget()
            self.sa_frame.pack(fill="both", expand=True)
        else:
            self.sa_frame.pack_forget()
            self.vpc_frame.pack(fill="both", expand=True)

    def _on_model_change(self, event=None):
        model = self.model_var.get()
        if model == NexusModel.GENERIC:
            self.entry_1g.config(state="normal")
            self.entry_10g.config(state="normal")
            self.entry_40g.config(state="normal")
        else:
            self.entry_1g.config(state="disabled")
            self.entry_10g.config(state="disabled")
            self.entry_40g.config(state="disabled")

    def _load_vlans(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            with open(filename, 'r') as f:
                self.vlan_input.delete("1.0", tk.END)
                self.vlan_input.insert("1.0", f.read())

    def _parse_vlans_from_ui(self) -> list[VLAN]:
        vlan_list = []
        raw_text = self.vlan_input.get("1.0", tk.END).strip()
        if not raw_text:
            return vlan_list
            
        for line in raw_text.splitlines():
            parts = line.strip().split()
            if not parts:
                continue
            try:
                v_id = int(parts[0])
                v_name = parts[1] if len(parts) > 1 else f"VLAN_{v_id}"
                vlan_list.append(VLAN(id=v_id, name=v_name))
            except (ValueError, IndexError) as e:
                logger.warning(f"Skipping invalid VLAN line: {line} - {e}")
        return vlan_list

    def _generate_config(self):
        try:
            mode = self.mode_var.get()
            model = self.model_var.get()
            
            logger.info(f"Generating models for mode: {mode}, model: {model}")
            
            # Auth
            user = self.admin_user_var.get().strip()
            password = self.admin_pass_var.get().strip()
            
            # VLANs
            vlan_objects = self._parse_vlans_from_ui()
            
            # Interface Logic
            exclude_ports = []
            vpc_ports = None

            if mode == "vPC Pair":
                vpc_ports = get_vpc_ports(model)
                if vpc_ports:
                    exclude_ports.extend(vpc_ports.get('peer_link', []))
                    exclude_ports.extend(vpc_ports.get('keepalive', []))

            if model == NexusModel.GENERIC:
                interface_objects = generate_interfaces_generic(
                    int(self.int_1g_var.get() or 0),
                    int(self.int_10g_var.get() or 0),
                    int(self.int_40g_var.get() or 0),
                    exclude_ports
                )
            else:
                interface_objects = generate_interfaces_model(model, exclude_ports)

            # Build Devices
            if mode == "Standalone":
                hostname = self.sa_hostname_var.get().strip()
                if not hostname: raise ValueError("Hostname is required")
                
                device = Device(
                    hostname=hostname,
                    mgmt_ip=self.sa_mgmt_ip_var.get(),
                    mgmt_gw=self.sa_mgmt_gw_var.get(),
                    model=model,
                    vlans=vlan_objects,
                    interfaces=interface_objects,
                    motd=self.sa_motd_var.get(),
                    admin_user=user,
                    admin_password=password
                )
                
                msg = self.pipeline.execute(device)
                logger.info(msg)
                
            else: # vPC Pair
                p_host = self.vpc_p_hostname_var.get().strip()
                s_host = self.vpc_s_hostname_var.get().strip()
                if not p_host or not s_host: raise ValueError("Both Hostnames are required")
                
                domain = self.vpc_domain_id_var.get()
                kpa_vrf = self.vpc_kpa_vrf_var.get()
                pl_id = self.vpc_pl_id_var.get()

                # Primary
                p_vpc = VPCConfig(
                    domain_id=int(domain),
                    keepalive_vrf=kpa_vrf,
                    peer_link_id=int(pl_id),
                    role="primary",
                    local_keepalive_ip=self.vpc_p_kpa_src_var.get(),
                    remote_keepalive_ip=self.vpc_s_kpa_src_var.get()
                )
                
                p_device = Device(
                    hostname=p_host,
                    mgmt_ip=self.vpc_p_mgmt_ip_var.get(),
                    mgmt_gw=self.vpc_p_mgmt_gw_var.get(),
                    model=model,
                    vlans=vlan_objects,
                    interfaces=interface_objects,
                    vpc=p_vpc,
                    admin_user=user,
                    admin_password=password
                )
                
                # Secondary
                s_vpc = VPCConfig(
                    domain_id=int(domain),
                    keepalive_vrf=kpa_vrf,
                    peer_link_id=int(pl_id),
                    role="secondary",
                    local_keepalive_ip=self.vpc_s_kpa_src_var.get(),
                    remote_keepalive_ip=self.vpc_p_kpa_src_var.get()
                )
                
                s_device = Device(
                    hostname=s_host,
                    mgmt_ip=self.vpc_s_mgmt_ip_var.get(),
                    mgmt_gw=self.vpc_s_mgmt_gw_var.get(),
                    model=model,
                    vlans=vlan_objects,
                    interfaces=interface_objects,
                    vpc=s_vpc,
                    admin_user=user,
                    admin_password=password
                )

                msg_p = self.pipeline.execute(p_device)
                msg_s = self.pipeline.execute(s_device)
                logger.info(f"{msg_p} {msg_s}")
            
            messagebox.showinfo("Success", "Configuration Pipeline completed successfully!\nCheck the 'dist' folder for config, diff, and risk reports.")
            
        except ValidationError as e:
            logger.warning(f"Validation failed: {e.report['errors']}")
            error_msg = "Validation Errors Found:\n\n" + "\n".join([f"• {err}" for err in e.report['errors']])
            messagebox.showwarning("Validation Failed", error_msg)
            
        except Exception as e:
            logger.error(f"Error during model-based generation: {str(e)}")
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = NexusConfiguratorGUI(root)
    root.mainloop()
