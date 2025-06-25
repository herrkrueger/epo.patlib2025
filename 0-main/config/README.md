# Configuration Testing Guide

## Patent Analysis Platform - Configuration Test Suite

This directory contains comprehensive tests for validating the configuration architecture of the Patent Analysis Platform (originally developed for REE analysis).

## Quick Test Execution

### Option 1: Bash Script (Recommended)
```bash
./test_config.sh
```

### Option 2: Python Direct
```bash
python config/test_config.py
```

### Option 3: Python Module Import
```python
from config import run_configuration_tests
success = run_configuration_tests()
```

### Option 4: Individual Test Components
```python
from config.test_config import test_yaml_file_syntax, test_centralized_search_patterns
test_yaml_file_syntax()
test_centralized_search_patterns()
```

## What Gets Tested

### ✅ Test Coverage

1. **YAML File Syntax** - Validates all 4 configuration files
2. **Configuration Manager** - Tests loading and access functions
3. **Configuration Validation** - Validates completeness and environment variables
4. **Centralized Search Patterns** - Verifies search parameters consolidation
5. **Configuration Reorganization** - Confirms proper separation of concerns
6. **Environment Handling** - Tests .env file loading and credentials
7. **Data Access Integration** - Validates module integration with centralized config

### 📊 Expected Results

- **Success Rate**: ~85.7% (6/7 tests pass)
- **Known Issue**: API validation shows warnings due to .env variables not being set during validation phase (this is expected behavior)

### 🎯 Test Output Interpretation

**✅ PASS Indicators:**
- YAML files load successfully
- Configuration manager functions properly
- Search patterns centralized correctly
- Environment variables load from .env file
- Data access modules integrate with centralized config

**⚠️ Expected Warnings:**
- "EPO OPS consumer key not configured" during validation phase (loads correctly during actual use)
- PATSTAT client cleanup exceptions (normal SQLAlchemy cleanup behavior)

## Configuration Files

Located in `/config/`:

- `api_config.yaml` - API settings (authentication, endpoints, rate limiting)
- `database_config.yaml` - Database connections and table mappings
- `visualization_config.yaml` - Visualization themes and chart configurations  
- `search_patterns_config.yaml` - Technology-specific search patterns, keywords, and business logic (REE focus)

## Architecture Validation

The tests validate the proper architectural separation:

### API Config (Technical Settings)
- EPO OPS authentication & endpoints
- PATSTAT connection parameters
- Rate limiting & request configuration

### Search Patterns Config (Business Logic)
- Technology-specific keywords & classification codes
- Technology taxonomy & descriptions
- Market data integration patterns
- Query templates & search strategies

## Environment Requirements

- Python 3.12+
- YAML support (`pyyaml`)
- Access to `/home/jovyan/patlib/.env` for credential testing
- TIP environment with `epo.tipdata.patstat` module (for PATSTAT tests)

## Troubleshooting

### Missing .env File
If .env file is not found, environment variable tests will report warnings but other tests will pass.

### Import Errors
Ensure you're running from the correct directory:
```bash
cd /home/jovyan/patlib/0-main
./test_config.sh
```

### PATSTAT Connection Issues
PATSTAT tests require TIP environment. In external environments, these tests may show warnings but shouldn't cause failures.

## Test Development

To add new tests, modify `test_config.py`:

1. Create new test function following pattern `test_new_feature()`
2. Add to main execution in `main()` function
3. Update this README with test description

Example:
```python
def test_new_feature():
    """Test X: Description of what gets tested."""
    try:
        # Test implementation
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
```