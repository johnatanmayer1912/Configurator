from models.device_model import Device
from core.renderer import ConfigRenderer
from core.validator import DeviceValidator, ValidationError
from utils.web_logger import logger

class ConfigEngine:
    def __init__(self):
        self.renderer = ConfigRenderer()
        self.validator = DeviceValidator()

    def build_config(self, device: Device, metadata: dict = None) -> str:
        """
        Validates the device model and builds the configuration string.
        Raises ValidationError if checks fail.
        """
        logger.info(f"CONFIG_ENGINE_BUILD_START",
                   hostname=device.hostname,
                   has_port_channels=device.port_channels is not None,
                   port_channels_count=len(device.port_channels) if device.port_channels else 0,
                   has_interfaces=device.interfaces is not None,
                   interfaces_count=len(device.interfaces) if device.interfaces else 0,
                   has_uplink_config=device.uplink_config is not None,
                   uplink_config_count=len(device.uplink_config) if device.uplink_config else 0,
                   has_downlink_config=device.downlink_config is not None,
                   downlink_config_count=len(device.downlink_config) if device.downlink_config else 0,
                   has_vpc=device.vpc is not None)
        
        # Phase 1: Validation
        report = self.validator.validate(device)
        logger.info(f"CONFIG_ENGINE_VALIDATION_RESULT",
                   hostname=device.hostname,
                   validation_status=report["status"],
                   validation_errors_count=len(report.get("errors", [])))
        
        if report["status"] == "fail":
            logger.error(f"CONFIG_ENGINE_VALIDATION_FAILED",
                        hostname=device.hostname,
                        errors=report.get("errors", []))
            raise ValidationError(report)
            
        # Phase 2: Rendering with Authority Metadata
        logger.info(f"CONFIG_ENGINE_RENDERING_START",
                   hostname=device.hostname,
                   metadata_keys=list(metadata.keys()) if metadata else [])
        
        config_text = self.renderer.render_device_config(device, metadata=metadata)
        
        logger.info(f"CONFIG_ENGINE_RENDERING_COMPLETE",
                   hostname=device.hostname,
                   config_length=len(config_text) if config_text else 0,
                   config_preview=config_text[:500] if config_text and len(config_text) > 0 else "EMPTY")
        
        return config_text

    def save_config(self, filename: str, content: str):
        """
        Saves the generated configuration to a file.
        """
        with open(filename, "w") as f:
            f.write(content)
