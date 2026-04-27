# CarryMem Testing Guide

## Overview

This guide covers testing practices, tools, and workflows for the CarryMem project.

## Quick Start

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=memory_classification_engine --cov-report=html

# Run specific test file
pytest tests/test_cli_enhancements.py -v

# Run tests matching a pattern
pytest -k "test_doctor" -v
```

## Test Structure

```
tests/
├── test_cli_enhancements.py    # CLI enhancements tests (17 tests, 71.92% coverage)
├── test_v080_cli.py            # Existing CLI tests
└── ... (other test files)
```

## Testing Tools

### pytest
Primary testing framework with powerful features:
- Fixtures for test setup/teardown
- Parametrization for testing multiple scenarios
- Markers for organizing tests
- Rich assertion introspection

### pytest-cov
Coverage measurement and reporting:
```bash
# Generate HTML coverage report
pytest --cov=memory_classification_engine --cov-report=html

# View report
open htmlcov/index.html
```

### pytest-mock
Mocking support for isolating tests:
```python
def test_with_mock(monkeypatch):
    monkeypatch.setattr("module.function", lambda: "mocked")
```

## Writing Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

### Example Test Structure

```python
"""
Tests for Module Name
Brief description of what's being tested
"""

import pytest
from module import function_to_test


@pytest.fixture
def sample_data():
    """Fixture providing test data"""
    return {"key": "value"}


class TestFunctionName:
    """Tests for specific function"""
    
    def test_normal_case(self, sample_data):
        """Test normal operation"""
        result = function_to_test(sample_data)
        assert result == expected_value
    
    def test_edge_case(self):
        """Test edge case handling"""
        result = function_to_test(None)
        assert result is None
    
    def test_error_case(self):
        """Test error handling"""
        with pytest.raises(ValueError):
            function_to_test("invalid")
```

### Best Practices

1. **One assertion per test** (when possible)
   - Makes failures easier to diagnose
   - Each test has a clear purpose

2. **Use descriptive test names**
   ```python
   # Good
   def test_doctor_command_detects_missing_database()
   
   # Bad
   def test_doctor()
   ```

3. **Arrange-Act-Assert pattern**
   ```python
   def test_example():
       # Arrange: Set up test data
       data = create_test_data()
       
       # Act: Execute the code being tested
       result = process(data)
       
       # Assert: Verify the result
       assert result == expected
   ```

4. **Use fixtures for common setup**
   ```python
   @pytest.fixture
   def temp_db(tmp_path):
       """Create temporary test database"""
       db_path = tmp_path / "test.db"
       # Setup code
       yield db_path
       # Teardown code (if needed)
   ```

5. **Mock external dependencies**
   ```python
   def test_with_mocked_file(monkeypatch, tmp_path):
       config_file = tmp_path / "config.json"
       config_file.write_text('{"key": "value"}')
       monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
   ```

## Coverage Goals

### Current Status
- **Overall project**: 11.10%
- **cli_enhancements.py**: 71.92% ✅
- **Target**: 80%+ overall

### Coverage Configuration

Located in `pyproject.toml`:
```toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
fail_under = 80.0
```

### Viewing Coverage

``ash
# Terminal report
pytest --cov=memory_classification_engine --cov-report=term-missing

# HTML report (recommended)
pytest --cov=memory_classification_engine --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=memory_classification_engine --cov-report=xml
```

## Code Quality Tools

### Black (Code Formatting)
```bash
# Check formatting
black --check src/ tests/

# Auto-format
black src/ tests/
```

### isort (Import Sorting)
```bash
# Check imports
isort --check-only src/ tests/

# Auto-sort
isort src/ tests/
```

### flake8 (Linting)
```bash
# Run linter
flake8 src/ tests/ --max-line-length=100
```

### mypy (Type Checking)
```bash
# Type check
mypy src/ --ignore-missing-imports
```

## Pre-commit Hooks

Automatically run quality checks before commits:

```bash
# Install hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run on staged files
git add .
git commit -m "message"  # Hooks run automatically
```

Configuration in `.pre-commit-config.yaml`:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON/TOML validation
- Black formatting
- isort import sorting
- flake8 linting
- mypy type checking

## CI/CD Integration

### GitHub Actions Workflow

Located in `.github/workflows/ci.yml`:

**Quality Job:**
- Linting (flake8)
- Formatting check (black)
- Import sorting (isort)
- Type checking (mypy)

**Test Job:**
- Matrix testing: Python 3.9, 3.10, 3.11, 3.12
- Platforms: Ubuntu, macOS
- Coverage reporting
- Minimum coverage threshold: 15%

**Build Job:**
- Package building
- Distribution validation

### Running CI Locally

```bash
# Run quality checks
flake8 src/ tests/
black --check src/ tests/
isort --check-only src/ tests/
mypy src/ --ignore-missing-imports

# Run tests with coverage
pytest --cov=memory_classification_engine --cov-fail-under=15 -v
```

## Test Examples

### Testing CLI Commands

```python
def test_doctor_healthy_system(temp_db, capsys, monkeypatch):
    """Test doctor command with all checks passing"""
    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/carrymem")
    monkeypatch.setattr(
        "memory_classification_engine.cli_enhancements._DEFAULT_DB",
        temp_db
    )
    
    result = cmd_doctor([])
    
    captured = capsys.readouterr()
    assert "Checking" in captured.out
    assert "health" in captured.out
```

### Testing with Temporary Files

```python
def test_setup_mcp_claude(tmp_path, capsys, monkeypatch):
    """Test MCP setup for Claude Desktop"""
    config_dir = tmp_path / "Library/Application Support/Claude"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "claude_desktop_config.json"
    config_path.write_text(json.dumps({}))
    
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    
    result = cmd_setup_mcp(["--tool", "claude"])
    
    assert result == 0
    with open(config_path) as f:
        config = json.load(f)
    assert "carrymem" in config["mcpServers"]
```

### Testing Database Operations

```python
@pytest.fixture
def populated_db(temp_db):
    """Create a database with test data"""
    conn = sqlite3.connect(str(temp_db))
    cursor = conn.cursor()
    
    test_data = [
        ("I prefer dark mode", "preference", "default"),
        ("Python is my main language", "fact", "default"),
    ]
    
    for content, mem_type, namespace in test_data:
        cursor.execute(
            "INSERT INTO memories (content, type, namespace) VALUES (?, ?, ?)",
            (content, mem_type, namespace)
        )
    
    conn.commit()
    conn.close()
    return temp_db
```

## Troubleshooting

### Tests Failing Locally But Passing in CI
- Check Python version differences
- Verify all dependencies are installed
- Check for platform-specific code

### Coverage Not Updating
```bash
# Clear coverage cache
rm -rf .coverage htmlcov/

# Run tests again
pytest --cov=memory_classification_engine --cov-report=html
```

### Import Errors in Tests
```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

### Pre-commit Hooks Failing
```bash
# Update hooks
pre-commit autoupdate

# Run specific hook
pre-commit run black --all-files
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [Black documentation](https://black.readthedocs.io/)
- [pre-commit documentation](https://pre-commit.com/)

## Contributing

When adding new features:
1. Write tests first (TDD approach recommended)
2. Aim for 95%+ coverage on new code
3. Run pre-commit hooks before committing
4. Ensure all CI checks pass

For questions or issues, refer to the project's main documentation or open an issue on GitHub.
