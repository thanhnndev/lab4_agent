#!/bin/bash
# Quick script to run advanced tests

echo "========================================="
echo "🧪 TravelBuddy Advanced Test Suite"
echo "========================================="
echo ""

cd "$(dirname "$0")/.."

echo "📁 Working directory: $(pwd)"
echo ""

python tests/run_advanced_tests.py

echo ""
echo "========================================="
echo "✅ Test run complete!"
echo "========================================="
echo ""
echo "📄 View Report:"
echo "   cat tests/test_details_report.md"
echo ""
echo "📊 View Metrics:"
echo "   cat logs/test_run_*/metrics.json | python -m json.tool"
echo ""
echo "📋 View Logs:"
echo "   cat logs/test_run_*/context_retention.log"
echo ""
