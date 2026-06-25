import logging
import os
from logging.handlers import RotatingFileHandler

class WebLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        self.log_file = os.path.join(self.log_dir, "web_authority.log")
        
        # Configure logging
        # We manually set up the logger to avoid clashes with Uvicorn basicConfig
        self.logger = logging.getLogger("WebAuthority")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        if self.logger.handlers:
            return
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        
        # File Handler
        fh = RotatingFileHandler(self.log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        # Stream Handler (Console)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def warning(self, msg):
        self.logger.warning(msg)

# Global Instance
logger = WebLogger()
