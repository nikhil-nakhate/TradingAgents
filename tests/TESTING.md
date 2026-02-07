# Testing Guide

## Quick Start

1. **Install test dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run all tests:**
   ```bash
   pytest
   ```

3. **Run specific test category:**
   ```bash
   pytest tests/unit/          # Unit tests only
   pytest tests/integration/   # Integration tests only
   ```

## Test Organization

### Unit Tests (`tests/unit/`)
Fast, isolated tests for individual components:
- `test_cli_utils.py` - CLI input validation and selection functions
- `test_propagation.py` - State initialization and graph arguments
- `test_message_buffer.py` - Message and status tracking
- `test_config.py` - Configuration validation and screening config
- `test_discovery.py` - Discovery feature unit tests
- `test_agent_states.py` - State structure validation

### Integration Tests (`tests/integration/`)
Tests for component interactions:
- `test_trading_graph.py` - Trading graph initialization and workflow
- `test_discovery_workflow.py` - Full discovery pipeline
- `test_cli_integration.py` - CLI end-to-end workflow

## Common Test Patterns

### Testing with Mocks
```python
@patch("module.function")
def test_example(mock_function):
    mock_function.return_value = "expected"
    result = function_under_test()
    assert result == "expected"
```

### Using Fixtures
```python
def test_with_fixtures(sample_config, mock_llm, sample_ticker):
    # Use provided fixtures
    result = function(sample_config, mock_llm, sample_ticker)
    assert result is not None
```

### Testing Error Cases
```python
def test_error_handling():
    with pytest.raises(ValueError):
        function_with_invalid_input()
```

## Available Fixtures

From `conftest.py`:
- `sample_config` - Sample configuration dictionary
- `temp_results_dir` - Temporary directory for test outputs
- `mock_llm` - Mock LLM instance
- `mock_openai_llm` - Mock OpenAI LLM
- `mock_anthropic_llm` - Mock Anthropic LLM
- `mock_google_llm` - Mock Google LLM
- `sample_agent_state` - Sample agent state dictionary
- `sample_ticker` - Sample ticker symbol ("AAPL")
- `sample_date` - Sample date string
- `sample_discovery_criteria` - Sample discovery criteria
- `sample_ticker_list` - Sample list of tickers
- `sample_analysis_result` - Sample analysis result
- `mock_stock_data` - Mock stock data
- `mock_message_buffer` - MessageBuffer instance
- `mock_propagator` - Propagator instance

## Mock Data

From `fixtures/mock_data.py`:
- `MOCK_STOCK_DATA` - Sample stock price/indicator data
- `MOCK_DISCOVERY_CRITERIA` - Sample discovery criteria
- `MOCK_TICKER_LISTS` - Sample ticker lists by sector
- `MOCK_ANALYSIS_RESULTS` - Sample analysis results
- `MOCK_AGENT_STATE` - Sample complete agent state
- `MOCK_LLM_RESPONSES` - Sample LLM response strings
- `get_test_date()` - Helper to generate test dates

## Debugging Tests

### Run with verbose output:
```bash
pytest -v
```

### Run with print statements:
```bash
pytest -s
```

### Run specific test:
```bash
pytest tests/unit/test_propagation.py::TestPropagator::test_create_initial_state_basic
```

### Stop on first failure:
```bash
pytest -x
```

### Show local variables on failure:
```bash
pytest -l
```

## Coverage

Generate coverage report:
```bash
pytest --cov=tradingagents --cov=cli --cov-report=html
```

View HTML report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Best Practices

1. **Mock External Dependencies**: Always mock LLM calls and API requests
2. **Use Fixtures**: Leverage shared fixtures for common test data
3. **Test Edge Cases**: Include tests for error conditions
4. **Keep Tests Fast**: Avoid real API calls or slow operations
5. **Independent Tests**: Tests should not depend on each other
6. **Descriptive Names**: Use clear test function names

## Troubleshooting

### Import Errors
- Ensure you're running from project root
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Mock Not Working
- Verify you're patching the correct import path
- Use `@patch("module.where.used.function")` not `@patch("module.where.defined.function")`

### Fixture Not Found
- Ensure fixture is defined in `conftest.py`
- Check fixture name matches exactly

### Test Hangs
- Check for infinite loops in mocked functions
- Verify mocks return expected values
