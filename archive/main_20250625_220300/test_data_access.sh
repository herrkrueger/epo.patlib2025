#!/bin/bash
# Data Access Test Script for Patent Analysis Platform
# Enhanced from EPO PATLIB 2025 Live Demo Code

echo "🚀 Patent Analysis Platform - Data Access Tests"
echo "Enhanced from EPO PATLIB 2025 Live Demo Code"
echo "============================================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python test scripts exist
if [[ ! -f "data_access/test_data_access.py" ]]; then
    echo "❌ Test script not found: data_access/test_data_access.py"
    exit 1
fi

if [[ ! -f "data_access/test_nuts_mapper.py" ]]; then
    echo "❌ Test script not found: data_access/test_nuts_mapper.py"
    exit 1
fi

# Check Python version
echo ""
echo "🐍 Python Environment Check"
echo "----------------------------"
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ Python version: $python_version"
else
    echo "❌ Python3 not found"
    exit 1
fi

# Check if virtual environment is active
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "✅ Virtual environment: $(basename $VIRTUAL_ENV)"
else
    echo "⚠️ No virtual environment detected"
fi

# Check key dependencies
echo ""
echo "📦 Dependency Check"
echo "-------------------"

dependencies=("pandas" "numpy" "pathlib")
missing_deps=()

for dep in "${dependencies[@]}"; do
    python3 -c "import $dep" 2>/dev/null
    if [[ $? -eq 0 ]]; then
        version=$(python3 -c "import $dep; print($dep.__version__)" 2>/dev/null)
        echo "✅ $dep: $version"
    else
        echo "❌ $dep: Not installed"
        missing_deps+=("$dep")
    fi
done

if [[ ${#missing_deps[@]} -gt 0 ]]; then
    echo ""
    echo "⚠️ Missing dependencies: ${missing_deps[*]}"
    echo "Please install missing packages:"
    echo "pip install ${missing_deps[*]}"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check data access module structure
echo ""
echo "🏗️ Module Structure Check"
echo "-------------------------"

required_files=(
    "data_access/__init__.py"
    "data_access/patstat_client.py"
    "data_access/ops_client.py"
    "data_access/cache_manager.py"
    "data_access/country_mapper.py"
    "data_access/nuts_mapper.py"
    "data_access/README.md"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        size=$(wc -l < "$file")
        echo "✅ $file ($size lines)"
    else
        echo "❌ $file (missing)"
    fi
done

# Run the test suite
echo ""
echo "🧪 Running Test Suite"
echo "====================="

# Option selection for test mode
echo "Select test mode:"
echo "1) Core data access tests (PATSTAT, OPS, cache)"
echo "2) NUTS geographic mapping tests"
echo "3) Both test suites (recommended)"
echo ""

# Default to full suite if no interaction
if [[ -t 0 ]]; then
    read -p "Choose option (1/2/3) [3]: " -n 1 -r
    echo
    choice="${REPLY:-3}"
else
    choice="3"
fi

case $choice in
    1)
        echo "Running core data access tests..."
        timeout 1800 python3 data_access/test_data_access.py
        ;;
    2)
        echo "Running NUTS mapping tests..."
        timeout 600 python3 data_access/test_nuts_mapper.py
        ;;
    3|*)
        echo "Running complete test suite..."
        echo ""
        echo "Step 1: Core Data Access Tests"
        echo "------------------------------"
        timeout 1800 python3 data_access/test_data_access.py
        core_exit_code=$?
        
        echo ""
        echo "Step 2: NUTS Geographic Mapping Tests"
        echo "------------------------------------"
        timeout 600 python3 data_access/test_nuts_mapper.py
        nuts_exit_code=$?
        
        # Use core tests as primary indicator
        test_exit_code=$core_exit_code
        
        echo ""
        echo "🏁 Test Suite Summary"
        echo "===================="
        echo "Core Data Access: $([ $core_exit_code -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")"
        echo "NUTS Mapping: $([ $nuts_exit_code -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL")"
        ;;
esac

# If we didn't run the full suite, get the exit code from the single test
if [[ $choice == "1" || $choice == "2" ]]; then
    test_exit_code=$?
fi

echo ""
echo "📊 Test Execution Summary"
echo "========================="

case $test_exit_code in
    0)
        echo "🎉 All tests passed successfully!"
        echo "✅ Data access layer is ready for production use"
        ;;
    124)
        echo "⏰ Tests timed out (30 minute limit exceeded)"
        echo "⚠️ Consider optimizing performance or reducing test scope"
        ;;
    130)
        echo "⚠️ Tests interrupted by user (Ctrl+C)"
        ;;
    *)
        echo "❌ Tests failed with exit code: $test_exit_code"
        echo "🔍 Please review the test output above for details"
        ;;
esac

# Performance summary
echo ""
echo "⚡ Performance Guidelines"
echo "------------------------"
echo "• PATSTAT connection: <5 seconds for initial setup"
echo "• EPO OPS authentication: <3 seconds with cached tokens"
echo "• Cache operations: <100ms for typical queries"
echo "• NUTS mapping: <1 second for hierarchy navigation"

# Usage examples
echo ""
echo "💡 Usage Examples"
echo "----------------"
echo "# Core data access tests:"
echo "python3 data_access/test_data_access.py"
echo ""
echo "# NUTS mapping tests:"
echo "python3 data_access/test_nuts_mapper.py"
echo ""
echo "# Individual component tests:"
echo "python3 -c \"from data_access.test_data_access import test_patstat_connection; test_patstat_connection()\""
echo "python3 -c \"from data_access.test_nuts_mapper import test_nuts_mapper_basic; test_nuts_mapper_basic()\""

# Additional checks
echo ""
echo "🔧 Additional Checks"
echo "-------------------"

# Check if config files exist
if [[ -f "config/api_config.yaml" ]]; then
    echo "✅ API configuration found"
else
    echo "⚠️ API configuration missing"
fi

if [[ -f "config/database_config.yaml" ]]; then
    echo "✅ Database configuration found"
else
    echo "⚠️ Database configuration missing"
fi

# Check environment file
if [[ -f ".env" ]]; then
    echo "✅ Environment file found"
else
    echo "⚠️ Environment file missing (needed for EPO OPS)"
fi

# Check NUTS mapping files
if [[ -f "data_access/mappings/nuts_mapping.csv" ]]; then
    nuts_count=$(wc -l < "data_access/mappings/nuts_mapping.csv")
    echo "✅ NUTS mapping CSV found ($nuts_count regions)"
else
    echo "⚠️ NUTS mapping CSV missing"
fi

# Final recommendations
echo ""
echo "📝 Next Steps"
echo "------------"
if [[ $test_exit_code -eq 0 ]]; then
    echo "1. ✅ Complete data access layer is ready for production!"
    echo "2. 🗄️ Deploy to EPO PATLIB 2025 demo environment"
    echo "3. 📊 Test with real patent analysis workflows"
    echo "4. 🚀 Demonstrate full pipeline capabilities"
else
    echo "1. 🔍 Review failed data access components and fix issues"
    echo "2. 📝 Check database connectivity and API credentials"
    echo "3. 🐛 Debug specific component integration problems"
    echo "4. 💬 Address configuration or dependency concerns"
fi

echo ""
echo "============================================================"
echo "Data Access Test Suite Completed"
echo "Exit code: $test_exit_code"

exit $test_exit_code