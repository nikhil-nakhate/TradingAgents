# TradingAgents Test Suite

Comprehensive test suite for the TradingAgents multi-agent trading framework.

## Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── unit/                    # Unit tests
│   ├── test_cli_utils.py    # CLI utility functions
│   ├── test_propagation.py  # State initialization and propagation
│   ├── test_message_buffer.py # Message buffer functionality
│   ├── test_config.py       # Configuration handling
│   ├── test_discovery.py    # Discovery feature unit tests
│   └── test_agent_states.py # Agent state validation
├── integration/             # Integration tests
│   ├── test_trading_graph.py # Trading graph workflow
│   ├── test_discovery_workflow.py # Full discovery pipeline
│   └── test_cli_integration.py # CLI end-to-end tests
└── fixtures/                # Mock data and test fixtures
    └── mock_data.py         # Mock data definitions
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run unit tests only
```bash
pytest tests/unit/
```

### Run integration tests only
```bash
pytest tests/integration/
```

### Run specific test file
```bash
pytest tests/unit/test_propagation.py
```

### Run specific test
```bash
pytest tests/unit/test_propagation.py::TestPropagator::test_create_initial_state_basic
```

### Run with coverage
```bash
pytest --cov=tradingagents --cov=cli --cov-report=html
```

### Run with verbose output
```bash
pytest -v
```

## Test Coverage

### Unit Tests
- **CLI Utilities**: Input validation, date formatting, analyst selection
- **State Propagation**: Initial state creation, state structure validation
- **Message Buffer**: Message storage, status updates, report aggregation
- **Configuration**: Config validation, screening config creation
- **Discovery**: Intent interpretation, ticker discovery, filtering
- **Agent States**: TypedDict structure validation

### Integration Tests
- **Trading Graph**: Graph initialization, LLM provider support, state flow
- **Discovery Workflow**: Full pipeline from intent to ticker selection
- **CLI Integration**: End-to-end CLI workflow (mocked)

## Mocking Strategy

All tests use mocks to avoid:
- API costs (LLM calls are mocked)
- External dependencies (yfinance, Alpha Vantage, etc.)
- User input (questionary prompts are mocked)
- File system operations (temporary directories used)

## Writing New Tests

1. **Unit Tests**: Test individual functions/methods in isolation
2. **Integration Tests**: Test component interactions
3. **Use Fixtures**: Leverage shared fixtures from `conftest.py`
4. **Mock External Calls**: Always mock LLM and API calls
5. **Test Edge Cases**: Include error handling and edge cases

## Example Test

```python
def test_example_functionality(sample_config, mock_llm):
    """Test example functionality."""
    # Arrange
    config = sample_config
    
    # Act
    result = function_under_test(config, mock_llm)
    
    # Assert
    assert result is not None
    assert isinstance(result, dict)
```

## Notes

- Tests are designed to run fast (no real API calls)
- All LLM interactions are mocked
- External data sources are mocked
- Tests are independent and can run in any order
