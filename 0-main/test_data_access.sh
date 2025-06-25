#!/bin/bash
# Data Access Test Script for Patent Analysis Platform
# Enhanced from EPO PATLIB 2025 Live Demo Code

echo "🚀 Patent Analysis Platform - Data Access Tests"
echo "============================================================"

# Change to the correct directory
cd "$(dirname "$0")"

# Run the data access tests
echo "Running comprehensive data access test suite..."
echo ""

python data_access/test_data_access.py

# Capture exit code
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "🎉 All data access tests completed successfully!"
else
    echo "⚠️ Some data access tests failed. Review the output above."
fi

echo "============================================================"
echo "To run individual test components:"
echo "  python -c 'from data_access.test_data_access import test_patstat_connection; test_patstat_connection()'"
echo "  python -c 'from data_access.test_data_access import test_ops_client; test_ops_client()'"
echo "  python -c 'from data_access.test_data_access import test_cache_functionality; test_cache_functionality()'"
echo ""
echo "Data access modules located in: ./data_access/"
echo "  - patstat_client.py"
echo "  - ops_client.py" 
echo "  - cache_manager.py"

exit $exit_code