# Advanced Test Suite - TravelBuddy Agent

## Overview

This test suite provides comprehensive testing for the TravelBuddy AI agent with:
- **5 Test Cases** covering different aspects
- **21 Total Prompts** with 3-5 prompts per test case
- **Full Logging** with timestamps, tool calls, and state tracking
- **Detailed Reports** with pass/fail analysis

## Test Cases

### 1. Context Retention (5 prompts)
Tests the agent's ability to maintain context across multiple conversation turns.
- Verifies memory of destination, dates, budget
- Tests follow-up requests with context references
- Validates multi-turn conversation coherence

### 2. Error Handling (3 prompts)
Tests how the agent handles errors and provides alternatives.
- Invalid routes (Hà Nội → Đà Lạt)
- Suggesting alternative destinations
- Recovery from failed searches

### 3. Edge Cases (4 prompts)
Tests boundary conditions and unusual inputs.
- Extreme budgets (100 triệu)
- Very low budgets (50k/đêm)
- Abbreviated city names (HN, ĐN)
- Impossible destinations (Mặt Trăng)

### 4. Guardrail Stress Test (4 prompts)
Stress tests the agent's constraints and refusal behavior.
- Non-travel requests (calculus problems)
- Persistent attempts to break constraints
- Consistent guardrail enforcement
- Travel-related request acceptance

### 5. Multi-Step Complex Planning (5 prompts)
Tests complex multi-step travel planning.
- Honeymoon planning with multiple constraints
- Progressive refinement (destination → hotels → activities)
- Budget tracking and calculation
- Comprehensive itinerary generation

## File Structure

```
tests/
├── advanced_test_cases.py      # Test case definitions
├── run_advanced_tests.py       # Test runner with logging
├── test_details_report.md      # Detailed test report
└── README.md                   # This file

logs/
└── test_run_YYYYMMDD_HHMMSS/
    ├── test_*.log              # Per-test conversation logs
    ├── *.log                   # Detailed turn-by-turn logs
    ├── full_session.log        # Complete session JSON
    └── metrics.json            # Metrics and statistics
```

## Running Tests

```bash
cd /home/thanhnndev/develop/ai.20k/lab4_agent
python tests/run_advanced_tests.py
```

### What the Runner Does:

1. **Creates Log Directory**: `logs/test_run_YYYYMMDD_HHMMSS/`
2. **Runs Each Test Case**: Sequentially with fresh sessions
3. **Logs Every Turn**: User prompt, agent response, tools, timing
4. **Evaluates Results**: Compares actual vs expected behavior
5. **Generates Report**: Creates `test_details_report.md`
6. **Saves Metrics**: JSON with all statistics

## Log Format

### Turn-by-Turn Log (test_*.log)
```
[TIMESTAMP] [TURN 01] [USER]: Tôi muốn đi du lịch Đà Nẵng
[TIMESTAMP] [TURN 01] [AGENT]: Chào bạn! ... (full response)
[TIMESTAMP] [TURN 01] [TOOLS]: None
[TIMESTAMP] [TURN 01] [TIMING]: 17.12s
[TIMESTAMP] [TURN 01] [STATE]: Messages: 1
[TIMESTAMP] [TURN 01] [RESULT]: PASS
```

### Metrics JSON
```json
{
  "timestamp": "20260407_151253",
  "total_test_cases": 5,
  "total_prompts": 21,
  "total_passed": 14,
  "total_failed": 7,
  "pass_rate": 66.7,
  "avg_response_time": 14.62,
  "test_case_results": [...]
}
```

## Report Structure

The generated `test_details_report.md` includes:

1. **Summary Header**: Date, environment, total counts
2. **Per Test Case Details**:
   - Description
   - Status (PASS/FAIL)
   - Individual prompt results
3. **Per Prompt Details**:
   - Input text
   - Expected behavior
   - Actual tool calls
   - Response time
   - Full conversation log
   - Pass/fail result with notes
4. **Summary Metrics Table**
5. **Issues & Observations**

## Evaluation Criteria

Each prompt is evaluated on:

1. **Tool Call Matching**: Did the agent call expected tools?
2. **Behavior Matching**: Did the agent behave as expected?
   - Asking follow-up questions when needed
   - Refusing non-travel requests
   - Demonstrating context retention
   - Providing appropriate responses

## Test Results Summary (Latest Run)

| Test Case | Prompts | Pass | Fail | Avg Time |
|-----------|---------|------|------|----------|
| Context Retention | 5 | 3 | 2 | 20.56s |
| Error Handling | 3 | 3 | 0 | 13.19s |
| Edge Cases | 4 | 2 | 2 | 10.77s |
| Guardrail Stress | 4 | 3 | 1 | 1.70s |
| Multi-Step Complex | 5 | 3 | 2 | 22.98s |

**Total**: 14/21 passed (66.7%)
**Average Response Time**: 14.62s

## Resuming Interrupted Tests

The test runner supports resuming:
- Each test case uses a unique thread_id
- Logs are saved incrementally
- Check `logs/test_run_*` for partial results
- Re-run to complete remaining tests

## Debugging Failed Tests

1. **Check Logs**: Open `logs/test_run_*/test_*.log`
2. **Review Report**: See `test_details_report.md` for notes
3. **Analyze Tools**: Compare expected vs actual tool calls
4. **Check Context**: Verify context retention across turns

## Common Issues

### Expected Tools But None Called
- Agent may have answered from knowledge
- Check if locations were validated
- Verify system prompt constraints

### Unexpected Tools Called
- Agent being proactive (may be positive)
- Check if additional info was provided
- Review guardrail behavior

### Context Not Retained
- Check message truncation (MAX_MESSAGES=20)
- Verify thread_id persistence
- Review conversation history length

## Performance Benchmarks

- **Simple Responses** (no tools): ~1-3s
- **Single Tool Call**: ~10-15s
- **Multi-Tool Calls**: ~15-25s
- **Complex Planning**: ~20-30s

## Future Enhancements

- [ ] Add automated fix suggestions
- [ ] Implement test case configuration
- [ ] Add visual dashboards
- [ ] Support parallel test execution
- [ ] Add regression testing
- [ ] Integrate with CI/CD

## Support

For issues or questions, check:
- `IMPLEMENTATION_CHECK.md` - Implementation details
- `test_results.md` - Basic test results
- Agent logs in `logs/` folder
