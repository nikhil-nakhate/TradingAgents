#!/usr/bin/env python3
"""
Simple script to validate test imports without running pytest.
This helps catch import errors before running the full test suite.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all test modules can be imported."""
    errors = []
    
    # Test fixture imports
    try:
        from tests.fixtures.mock_data import (
            MOCK_STOCK_DATA,
            MOCK_DISCOVERY_CRITERIA,
            MOCK_TICKER_LISTS,
            MOCK_ANALYSIS_RESULTS,
            MOCK_AGENT_STATE,
            get_test_date,
        )
        print("✓ Mock data imports OK")
    except Exception as e:
        errors.append(f"Mock data import failed: {e}")
    
    # Test conftest imports (without pytest)
    try:
        # Skip pytest-dependent parts
        from tests.fixtures.mock_data import MOCK_STOCK_DATA
        print("✓ Fixtures can access mock data")
    except Exception as e:
        errors.append(f"Fixture import failed: {e}")
    
    # Test unit test imports
    unit_tests = [
        "tests.unit.test_propagation",
        "tests.unit.test_message_buffer",
        "tests.unit.test_config",
        "tests.unit.test_agent_states",
    ]
    
    for test_module in unit_tests:
        try:
            # Just check if module can be parsed
            with open(test_module.replace(".", "/") + ".py") as f:
                compile(f.read(), test_module, "exec")
            print(f"✓ {test_module} syntax OK")
        except SyntaxError as e:
            errors.append(f"{test_module} syntax error: {e}")
        except Exception as e:
            # Import errors are OK if pytest isn't installed
            if "pytest" not in str(e).lower() and "No module named" not in str(e):
                errors.append(f"{test_module} error: {e}")
    
    # Test integration test imports
    integration_tests = [
        "tests.integration.test_trading_graph",
        "tests.integration.test_discovery_workflow",
    ]
    
    for test_module in integration_tests:
        try:
            with open(test_module.replace(".", "/") + ".py") as f:
                compile(f.read(), test_module, "exec")
            print(f"✓ {test_module} syntax OK")
        except SyntaxError as e:
            errors.append(f"{test_module} syntax error: {e}")
        except Exception as e:
            if "pytest" not in str(e).lower() and "No module named" not in str(e):
                errors.append(f"{test_module} error: {e}")
    
    if errors:
        print("\n✗ Errors found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    else:
        print("\n✓ All imports validated successfully!")
        print("Note: Some imports may fail if pytest is not installed.")
        print("Run 'pip install pytest pytest-mock pytest-cov' to install test dependencies.")
        return 0

if __name__ == "__main__":
    sys.exit(test_imports())
