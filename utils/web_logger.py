import logging
import os
import json
import uuid
import time
import sys
import threading
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar
from typing import Any, Dict, Optional
from pathlib import Path

# Context variable for request ID correlation
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
session_id: str = str(uuid.uuid4())

# Context variable for user input correlation
user_input_var: ContextVar[Dict[str, Any]] = ContextVar("user_input", default={})

class ComprehensiveLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # Main application log
        self.log_file = os.path.join(self.log_dir, f"comprehensive_audit_{session_id}.log")
        
        # User action log (frontend interactions)
        self.user_action_log = os.path.join(self.log_dir, f"user_actions_{session_id}.log")
        
        # API log (all API calls and responses)
        self.api_log = os.path.join(self.log_dir, f"api_audit_{session_id}.log")
        
        # Error log (all errors)
        self.error_log = os.path.join(self.log_dir, f"errors_{session_id}.log")
        
        # User input correlation log
        self.input_correlation_log = os.path.join(self.log_dir, f"input_correlation_{session_id}.log")
        
        # Configure main logger
        self.logger = logging.getLogger("WebAuthority")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        if self.logger.handlers:
            return
        
        # Structured JSON Formatter
        formatter = StructuredFormatter()
        
        # File Handler - Main
        fh = RotatingFileHandler(self.log_file, maxBytes=10_000_000, backupCount=10, encoding="utf-8")
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        self.logger.addHandler(fh)
        
        # File Handler - User Actions
        user_fh = RotatingFileHandler(self.user_action_log, maxBytes=10_000_000, backupCount=10, encoding="utf-8")
        user_fh.setFormatter(formatter)
        user_fh.setLevel(logging.DEBUG)
        self.user_logger = logging.getLogger("UserActions")
        self.user_logger.setLevel(logging.DEBUG)
        self.user_logger.propagate = False
        self.user_logger.addHandler(user_fh)
        
        # File Handler - API
        api_fh = RotatingFileHandler(self.api_log, maxBytes=10_000_000, backupCount=10, encoding="utf-8")
        api_fh.setFormatter(formatter)
        api_fh.setLevel(logging.DEBUG)
        self.api_logger = logging.getLogger("APIAudit")
        self.api_logger.setLevel(logging.DEBUG)
        self.api_logger.propagate = False
        self.api_logger.addHandler(api_fh)
        
        # File Handler - Errors
        error_fh = RotatingFileHandler(self.error_log, maxBytes=10_000_000, backupCount=10, encoding="utf-8")
        error_fh.setFormatter(formatter)
        error_fh.setLevel(logging.ERROR)
        self.error_logger = logging.getLogger("Errors")
        self.error_logger.setLevel(logging.ERROR)
        self.error_logger.propagate = False
        self.error_logger.addHandler(error_fh)
        
        # File Handler - Input Correlation
        input_fh = RotatingFileHandler(self.input_correlation_log, maxBytes=10_000_000, backupCount=10, encoding="utf-8")
        input_fh.setFormatter(formatter)
        input_fh.setLevel(logging.DEBUG)
        self.input_logger = logging.getLogger("InputCorrelation")
        self.input_logger.setLevel(logging.DEBUG)
        self.input_logger.propagate = False
        self.input_logger.addHandler(input_fh)
        
        # Stream Handler (Console) - human readable
        console_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(console_formatter)
        ch.setLevel(logging.INFO)
        self.logger.addHandler(ch)
        
        # Log startup
        self.info("APPLICATION_STARTUP", session_id=session_id, python_version=sys.version, cwd=os.getcwd())

    def info(self, msg, **kwargs):
        self._log(logging.INFO, msg, **kwargs)

    def error(self, msg, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)

    def warning(self, msg, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)

    def debug(self, msg, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

    def log_user_action(self, action_type: str, element_id: str = None, value: str = None, 
                       element_type: str = None, page: str = None, **kwargs):
        """Log user interactions from frontend"""
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "session_id": session_id,
            "action_type": action_type,
            "element_id": element_id,
            "element_type": element_type,
            "value": value,
            "page": page,
            "request_id": request_id_var.get(""),
            **kwargs
        }
        self.user_logger.debug(json.dumps(log_entry))

    def log_api_request(self, method: str, endpoint: str, payload: Dict = None, 
                       headers: Dict = None, **kwargs):
        """Log API requests"""
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "session_id": session_id,
            "type": "API_REQUEST",
            "method": method,
            "endpoint": endpoint,
            "payload": payload,
            "headers": {k: v for k, v in (headers or {}).items() if k.lower() != 'authorization'},
            "request_id": request_id_var.get(""),
            **kwargs
        }
        self.api_logger.debug(json.dumps(log_entry))

    def log_api_response(self, method: str, endpoint: str, status_code: int, 
                        response: Dict = None, duration_ms: float = None, **kwargs):
        """Log API responses"""
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "session_id": session_id,
            "type": "API_RESPONSE",
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "response": response,
            "duration_ms": duration_ms,
            "request_id": request_id_var.get(""),
            **kwargs
        }
        self.api_logger.debug(json.dumps(log_entry))

    def log_error(self, msg, **kwargs):
        """Log to error file"""
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "session_id": session_id,
            "message": msg,
            "request_id": request_id_var.get(""),
            "user_input": user_input_var.get({}),
            **kwargs
        }
        self.error_logger.error(json.dumps(log_entry))

    def set_user_input(self, input_data: Dict[str, Any]):
        """Set user input context for correlation"""
        user_input_var.set(input_data)
        
        # Log the input correlation
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "session_id": session_id,
            "type": "USER_INPUT_SET",
            "request_id": request_id_var.get(""),
            "input_data": input_data
        }
        self.input_logger.debug(json.dumps(log_entry))
    
    def log_user_input_correlation(self, action: str, input_data: Dict[str, Any], 
                                  system_response: Dict[str, Any] = None, **kwargs):
        """Log correlation between user input and system response"""
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "session_id": session_id,
            "type": "INPUT_CORRELATION",
            "action": action,
            "request_id": request_id_var.get(""),
            "user_input": input_data,
            "system_response": system_response,
            **kwargs
        }
        self.input_logger.debug(json.dumps(log_entry))
    
    def log_switch_configuration(self, hostname: str, model: str, role: str, 
                                 config_data: Dict[str, Any] = None, **kwargs):
        """Log switch configuration with user input correlation"""
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "session_id": session_id,
            "type": "SWITCH_CONFIGURATION",
            "request_id": request_id_var.get(""),
            "hostname": hostname,
            "model": model,
            "role": role,
            "config_data": config_data,
            "user_input": user_input_var.get({}),
            **kwargs
        }
        self.input_logger.debug(json.dumps(log_entry))
    
    def log_vpc_configuration(self, domain: int, primary: str, secondary: str, 
                             config_data: Dict[str, Any] = None, **kwargs):
        """Log vPC configuration with user input correlation"""
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "session_id": session_id,
            "type": "VPC_CONFIGURATION",
            "request_id": request_id_var.get(""),
            "domain": domain,
            "primary": primary,
            "secondary": secondary,
            "config_data": config_data,
            "user_input": user_input_var.get({}),
            **kwargs
        }
        self.input_logger.debug(json.dumps(log_entry))
    
    def log_deployment_generation(self, switch_count: int, vpc_pair_count: int, 
                                  uplink_count: int, duration_ms: float = None, **kwargs):
        """Log deployment generation with user input correlation"""
        log_entry = {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "session_id": session_id,
            "type": "DEPLOYMENT_GENERATION",
            "request_id": request_id_var.get(""),
            "switch_count": switch_count,
            "vpc_pair_count": vpc_pair_count,
            "uplink_count": uplink_count,
            "duration_ms": duration_ms,
            "user_input": user_input_var.get({}),
            **kwargs
        }
        self.input_logger.debug(json.dumps(log_entry))

    def _log(self, level, msg, **kwargs):
        request_id = request_id_var.get("")
        log_entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "level": logging.getLevelName(level),
            "message": msg,
            "session_id": session_id,
            "request_id": request_id,
            **kwargs
        }
        self.logger.log(level, json.dumps(log_entry))

    def shutdown(self):
        """Close all log handlers on shutdown"""
        self.info("APPLICATION_SHUTDOWN", session_id=session_id)
        handlers = self.logger.handlers[:]
        self.user_logger.handlers[:]
        self.api_logger.handlers[:]
        self.error_logger.handlers[:]
        self.input_logger.handlers[:]
        for handler in handlers:
            handler.close()
        for handler in self.user_logger.handlers:
            handler.close()
        for handler in self.api_logger.handlers:
            handler.close()
        for handler in self.error_logger.handlers:
            handler.close()
        for handler in self.input_logger.handlers:
            handler.close()

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", ""),
            "session_id": session_id,
        }
        if hasattr(record, "extra_data"):
            log_entry.update(record.extra_data)
        return json.dumps(log_entry)

# Global Instance
logger = ComprehensiveLogger()
