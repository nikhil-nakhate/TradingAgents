"""
Unit tests for configuration handling.
"""

import pytest
import copy
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.discovery.lightweight_analyzer import create_screening_config


class TestDefaultConfig:
    """Test cases for DEFAULT_CONFIG."""

    def test_default_config_has_required_keys(self):
        """Test DEFAULT_CONFIG has all required keys."""
        required_keys = [
            "project_dir",
            "results_dir",
            "llm_provider",
            "deep_think_llm",
            "quick_think_llm",
            "backend_url",
            "max_debate_rounds",
            "max_risk_discuss_rounds",
            "max_recur_limit",
            "data_vendors",
        ]
        
        for key in required_keys:
            assert key in DEFAULT_CONFIG, f"Missing required key: {key}"

    def test_default_config_data_vendors_structure(self):
        """Test data_vendors structure."""
        assert "data_vendors" in DEFAULT_CONFIG
        data_vendors = DEFAULT_CONFIG["data_vendors"]
        
        required_categories = [
            "core_stock_apis",
            "technical_indicators",
            "fundamental_data",
            "news_data",
        ]
        
        for category in required_categories:
            assert category in data_vendors, f"Missing data vendor category: {category}"

    def test_config_copying_does_not_mutate_original(self):
        """Test that copying config doesn't mutate original."""
        original = DEFAULT_CONFIG.copy()
        copied = DEFAULT_CONFIG.copy()
        
        copied["max_debate_rounds"] = 999
        copied["data_vendors"]["core_stock_apis"] = "test"
        
        assert original["max_debate_rounds"] != 999
        assert original["data_vendors"]["core_stock_apis"] != "test"

    def test_config_deep_copy(self):
        """Test deep copying config."""
        import copy
        
        original = DEFAULT_CONFIG.copy()
        deep_copied = copy.deepcopy(DEFAULT_CONFIG)
        
        deep_copied["data_vendors"]["core_stock_apis"] = "test"
        
        assert original["data_vendors"]["core_stock_apis"] != "test"

    def test_config_llm_provider_default(self):
        """Test default LLM provider."""
        assert DEFAULT_CONFIG["llm_provider"] == "openai"

    def test_config_debate_rounds_default(self):
        """Test default debate rounds."""
        assert DEFAULT_CONFIG["max_debate_rounds"] == 1
        assert DEFAULT_CONFIG["max_risk_discuss_rounds"] == 1

    def test_config_recur_limit_default(self):
        """Test default recursion limit."""
        assert DEFAULT_CONFIG["max_recur_limit"] == 100


class TestScreeningConfig:
    """Test cases for create_screening_config."""

    def test_create_screening_config_basic(self, sample_config):
        """Test create_screening_config creates optimized config."""
        screening_config = create_screening_config(sample_config)
        
        assert screening_config["deep_think_llm"] == sample_config["quick_think_llm"]
        assert screening_config["max_debate_rounds"] == 0
        assert screening_config["max_risk_discuss_rounds"] == 0
        assert screening_config["use_memory"] == False
        assert screening_config["use_reflection"] == False

    def test_create_screening_config_data_vendors(self, sample_config):
        """Test screening config uses fast data vendors."""
        screening_config = create_screening_config(sample_config)
        
        assert screening_config["data_vendors"]["core_stock_apis"] == "yfinance"
        assert screening_config["data_vendors"]["technical_indicators"] == "yfinance"
        assert screening_config["data_vendors"]["fundamental_data"] == "yfinance"
        assert screening_config["data_vendors"]["news_data"] == "openai"

    def test_create_screening_config_timeouts(self, sample_config):
        """Test screening config has appropriate timeouts."""
        screening_config = create_screening_config(sample_config)
        
        assert screening_config["api_timeout"] == 10
        assert screening_config["max_retries"] == 2

    def test_create_screening_config_does_not_mutate_original(self, sample_config):
        """Test create_screening_config doesn't mutate original."""
        original_debate_rounds = sample_config["max_debate_rounds"]
        screening_config = create_screening_config(sample_config)
        
        assert sample_config["max_debate_rounds"] == original_debate_rounds
        assert screening_config["max_debate_rounds"] == 0


class TestConfigValidation:
    """Test cases for config validation."""

    @pytest.mark.parametrize("provider", ["openai", "anthropic", "google", "llamacpp", "ollama", "openrouter"])
    def test_valid_llm_providers(self, provider):
        """Test valid LLM providers."""
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = provider
        
        # Should not raise error
        assert config["llm_provider"] == provider

    def test_config_data_vendors_options(self):
        """Test data vendor options are valid."""
        config = DEFAULT_CONFIG.copy()
        
        # Test valid vendor options
        valid_vendors = {
            "core_stock_apis": ["yfinance", "alpha_vantage", "local"],
            "technical_indicators": ["yfinance", "alpha_vantage", "local"],
            "fundamental_data": ["openai", "alpha_vantage", "local"],
            "news_data": ["openai", "alpha_vantage", "google", "local"],
        }
        
        for category, vendors in valid_vendors.items():
            for vendor in vendors:
                config["data_vendors"][category] = vendor
                assert config["data_vendors"][category] == vendor

    def test_config_project_dir_is_absolute(self):
        """Test project_dir is an absolute path."""
        import os
        project_dir = DEFAULT_CONFIG["project_dir"]
        assert os.path.isabs(project_dir)

    def test_config_results_dir(self):
        """Test results_dir configuration."""
        results_dir = DEFAULT_CONFIG["results_dir"]
        assert isinstance(results_dir, str)
        assert len(results_dir) > 0
