"""Import Wizard Unit Tests

Tests the config builder questionnaire engine and wizard flow logic.
"""

import pytest
from core.import_wizard import QUESTIONS


class TestImportWizard:
    """Test import wizard questionnaire structure and logic."""
    
    def test_questions_structure(self):
        """Test that QUESTIONS is a list of question dictionaries."""
        assert isinstance(QUESTIONS, list), "QUESTIONS must be a list"
        assert len(QUESTIONS) > 0, "QUESTIONS must have at least one question"
        
        for question in QUESTIONS:
            assert isinstance(question, dict), "Each question must be a dictionary"
            assert "id" in question, "Question must have 'id' field"
            assert "title" in question, "Question must have 'title' field"
            assert "type" in question, "Question must have 'type' field"
    
    def test_start_mode_question_exists(self):
        """Test that start_mode question exists with correct options."""
        start_mode = next((q for q in QUESTIONS if q["id"] == "start_mode"), None)
        assert start_mode is not None, "start_mode question must exist"
        
        assert start_mode["type"] == "choice", "start_mode must be choice type"
        assert "options" in start_mode, "start_mode must have options"
        assert len(start_mode["options"]) == 2, "start_mode must have 2 options (paste, fresh)"
        
        option_values = [opt["value"] for opt in start_mode["options"]]
        assert "paste" in option_values, "Must have 'paste' option"
        assert "fresh" in option_values, "Must have 'fresh' option"
    
    def test_device_role_question_exists(self):
        """Test that device_role question exists with correct options."""
        device_role = next((q for q in QUESTIONS if q["id"] == "device_role"), None)
        assert device_role is not None, "device_role question must exist"
        
        assert device_role["type"] == "choice", "device_role must be choice type"
        assert "options" in device_role, "device_role must have options"
        
        option_values = [opt["value"] for opt in device_role["options"]]
        expected_roles = ["access", "leaf", "spine", "mgmt"]
        for role in expected_roles:
            assert role in option_values, f"Must have '{role}' option"
    
    def test_redundancy_question_exists(self):
        """Test that redundancy question exists with correct options."""
        redundancy = next((q for q in QUESTIONS if q["id"] == "redundancy"), None)
        assert redundancy is not None, "redundancy question must exist"
        
        assert redundancy["type"] == "choice", "redundancy must be choice type"
        
        option_values = [opt["value"] for opt in redundancy["options"]]
        assert "standalone" in option_values, "Must have 'standalone' option"
        assert "vpc" in option_values, "Must have 'vpc' option"
    
    def test_redundancy_hide_if_logic(self):
        """Test that redundancy question has hide_if for mgmt role."""
        redundancy = next((q for q in QUESTIONS if q["id"] == "redundancy"), None)
        assert "hide_if" in redundancy, "redundancy must have hide_if"
        assert redundancy["hide_if"]["device_role"] == "mgmt", "Should hide for mgmt role"
    
    def test_environment_question_exists(self):
        """Test that environment question exists."""
        environment = next((q for q in QUESTIONS if q["id"] == "environment"), None)
        assert environment is not None, "environment question must exist"
        
        assert environment["type"] == "choice", "environment must be choice type"
        
        option_values = [opt["value"] for opt in environment["options"]]
        assert "lab" in option_values, "Must have 'lab' option"
        assert "production" in option_values, "Must have 'production' option"
    
    def test_fabric_question_exists(self):
        """Test that fabric question exists for VXLAN overlay."""
        fabric = next((q for q in QUESTIONS if q["id"] == "fabric"), None)
        assert fabric is not None, "fabric question must exist"
        
        assert fabric["type"] == "choice", "fabric must be choice type"
        assert "show_if" in fabric, "fabric must have show_if for leaf role"
    
    def test_site_name_question_exists(self):
        """Test that site_name question exists."""
        site_name = next((q for q in QUESTIONS if q["id"] == "site_name"), None)
        assert site_name is not None, "site_name question must exist"
        
        assert site_name["type"] == "text", "site_name must be text type"
        assert site_name["required"] is True, "site_name must be required"
        assert "placeholder" in site_name, "site_name must have placeholder"
    
    def test_hostname_question_exists(self):
        """Test that hostname question exists."""
        hostname = next((q for q in QUESTIONS if q["id"] == "hostname"), None)
        assert hostname is not None, "hostname question must exist"
        
        assert hostname["type"] == "text", "hostname must be text type"
        assert hostname["required"] is True, "hostname must be required"
    
    def test_mgmt_ip_question_exists(self):
        """Test that mgmt_ip question exists."""
        mgmt_ip = next((q for q in QUESTIONS if q["id"] == "mgmt_ip"), None)
        assert mgmt_ip is not None, "mgmt_ip question must exist"
        
        assert mgmt_ip["type"] == "text", "mgmt_ip must be text type"
        assert mgmt_ip["required"] is True, "mgmt_ip must be required"
        assert "placeholder" in mgmt_ip, "mgmt_ip must have placeholder"
    
    def test_running_config_question_exists(self):
        """Test that running_config question exists for paste mode."""
        running_config = next((q for q in QUESTIONS if q["id"] == "running_config"), None)
        assert running_config is not None, "running_config question must exist"
        
        assert running_config["type"] == "textarea", "running_config must be textarea type"
        assert "show_if" in running_config, "running_config must have show_if"
        assert running_config["show_if"]["start_mode"] == "paste", "Should show for paste mode"
    
    def test_question_has_help_text(self):
        """Test that questions have help text for user guidance."""
        for question in QUESTIONS:
            # Help text is optional but recommended
            if "help" in question:
                assert isinstance(question["help"], str), "Help text must be a string"
    
    def test_question_required_field_validation(self):
        """Test that required field is properly set."""
        required_questions = [q for q in QUESTIONS if q.get("required")]
        assert len(required_questions) > 0, "Must have at least one required question"
        
        for question in required_questions:
            assert isinstance(question["required"], bool), "required must be boolean"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
