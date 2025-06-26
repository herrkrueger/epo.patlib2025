#!/bin/bash
# Configuration Test Script for REE Patent Analysis Platform
# Enhanced from EPO PATLIB 2025 Live Demo Code

echo "🚀 REE Patent Analysis Platform - Configuration Tests"
echo "============================================================"

# Change to the correct directory
cd "$(dirname "$0")"

# Run the configuration tests
echo "Running comprehensive configuration test suite..."
echo ""

python config/test_config.py

# Capture exit code
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "🎉 All configuration tests completed successfully!"
else
    echo "⚠️ Some configuration tests failed. Review the output above."
fi

echo "============================================================"
echo "To run individual test components:"
echo "  python -c 'from config.test_config import test_yaml_file_syntax; test_yaml_file_syntax()'"
echo "  python -c 'from config.test_config import test_centralized_search_patterns; test_centralized_search_patterns()'"
echo "  python -c 'from config.test_config import test_data_access_integration; test_data_access_integration()'"
echo ""
echo "Configuration files located in: ./config/"
echo "  - api_config.yaml"
echo "  - database_config.yaml" 
echo "  - visualization_config.yaml"
echo "  - search_patterns_config.yaml"

exit $exit_code