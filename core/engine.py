from models.device_model import Device
from core.renderer import ConfigRenderer
from core.validator import DeviceValidator, ValidationError

class ConfigEngine:
    def __init__(self):
        self.renderer = ConfigRenderer()
        self.validator = DeviceValidator()

    def build_config(self, device: Device, metadata: dict = None) -> str:
        """
        Validates the device model and builds the configuration string.
        Raises ValidationError if checks fail.
        """
        # Phase 1: Validation
        report = self.validator.validate(device)
        if report["status"] == "fail":
            raise ValidationError(report)
            
        # Phase 2: Rendering with Authority Metadata
        return self.renderer.render_device_config(device, metadata=metadata)

    def save_config(self, filename: str, content: str):
        """
        Saves the generated configuration to a file.
        """
        with open(filename, "w") as f:
            f.write(content)
