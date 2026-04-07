# 🤖 TravelBuddy - AI Travel Agent (Lab 4)

**TravelBuddy** is an intelligent travel assistant built with LangGraph and Ollama that helps users plan trips by automatically searching flights, checking budgets, and finding suitable hotels.

---

## 📋 Quick Links

| Document | Description |
|----------|-------------|
| [`test_results.md`](test_results.md) | Basic test results (5 tests) with 12 screenshots |
| [`tests/test_details_report.md`](tests/test_details_report.md) | Advanced test details (21 prompts) with full logs |
| [`IMPLEMENTATION_CHECK.md`](IMPLEMENTATION_CHECK.md) | Requirements verification checklist |
| [`tests/README.md`](tests/README.md) | Advanced test suite documentation |

---

## 🏗️ Project Structure

```
lab4_agent/
├── 📄 agent.py                     # Main LangGraph agent workflow
├── 📄 system_prompt.txt            # Agent persona, rules, constraints
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env                         # Environment variables (Ollama config)
│
├── 📁 tools/                       # Custom tools module
│   ├── __init__.py                 # Export all tools
│   ├── flights.py                  # search_flights tool
│   ├── hotels.py                   # search_hotels tool
│   ├── budget.py                   # calculate_budget tool
│   └── locations.py                # check_valid_locations tool (NEW)
│
├── 📁 data/                        # Mock data
│   └── mock_data.py                # Flights & hotels database
│
├── 📁 tests/                       # Advanced test suite
│   ├── advanced_test_cases.py      # 5 test cases, 21 prompts
│   ├── run_advanced_tests.py       # Test runner with logging
│   ├── run_tests.sh                # Quick run script
│   ├── test_details_report.md      # Detailed test report
│   └── README.md                   # Test documentation
│
├── 📁 logs/                        # Test execution logs
│   └── test_run_[timestamp]/
│       ├── test_*.log              # Per-test logs
│       ├── full_session.log        # Full conversation log
│       └── metrics.json            # Performance metrics
│
├── 📁 extras/                      # Additional resources
│   └── simple-test/                # Screenshots (12 images)
│       ├── test-01-1.png
│       ├── test-02-1.png ... test-02-4.png
│       ├── test-03-1.png ... test-03-3.png
│       ├── test-04-1.png ... test-04-2.png
│       └── test-05-1.png ... test-05-2.png
│
├── 📄 test_results.md              # Basic test results with screenshots
└── 📄 IMPLEMENTATION_CHECK.md      # Requirements verification
```

---

## 🚀 Setup

### 1) Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Start Ollama

```bash
# Install Ollama: https://ollama.ai
ollama pull dengcao/Qwen3-30B-A3B-Instruct-2507
# Or use: llama3.1:8b
```

### 3) Configure Environment

```bash
cp .env.example .env
# Edit .env with your Ollama host and model
```

### 4) Run Agent

```bash
python agent.py
```

---

## 🧪 Testing

### Basic Tests (5 scenarios)

Run the agent manually and test these scenarios:

| Test | Description | Expected |
|------|-------------|----------|
| 1 | Direct Answer | No tools, friendly greeting |
| 2 | Single Tool Call | `search_flights` called |
| 3 | Multi-Step Chaining | Flight + Hotel + Budget |
| 4 | Missing Info | Ask clarifying questions |
| 5 | Guardrail | Refuse non-travel requests |

**Results:** [`test_results.md`](test_results.md) (with 12 screenshots)

---

### Advanced Tests (21 prompts)

Run the automated test suite:

```bash
# Option 1: Python
python tests/run_advanced_tests.py

# Option 2: Shell script
bash tests/run_tests.sh
```

**Test Cases:**
1. **Context Retention** (5 prompts) - Multi-turn conversation
2. **Error Handling** (3 prompts) - Retry & recovery
3. **Edge Cases** (4 prompts) - Extreme budgets, invalid destinations
4. **Guardrail Stress** (5 prompts) - Constraint breaking attempts
5. **Multi-Step Complex** (4 prompts) - Complex travel planning

**Results:** [`tests/test_details_report.md`](tests/test_details_report.md)

**Latest Run:**
- ✅ **20/21 passed (95.2%)**
- ⏱️ **Avg response: 14.62s**
- 📂 **Logs:** `logs/test_run_[timestamp]/`

---

## 🛠️ Tools

### Available Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `check_valid_locations()` | None | Returns valid cities and routes |
| `search_flights(origin, destination)` | origin, destination | Search flights between cities |
| `search_hotels(city, max_price)` | city, max_price_per_night | Search hotels with price filter |
| `calculate_budget(total, expenses)` | total_budget, expenses | Calculate remaining budget |

### Tool Flow

```
User Input
    ↓
check_valid_locations() ← Always first
    ↓
search_flights() / search_hotels()
    ↓
calculate_budget()
    ↓
Final Response
```

---

## 📊 Test Results Summary

### Basic Tests

| Test | Status | Response Time | Tools Called |
|------|--------|---------------|--------------|
| Test 1: Direct Answer | ✅ PASS | 18.34s | 0 |
| Test 2: Single Tool | ✅ PASS | 20.45s | 3 |
| Test 3: Multi-Step | ✅ PASS | 17.06s | 3 |
| Test 4: Missing Info | ✅ PASS | 1.11s | 0 |
| Test 5: Guardrail | ✅ PASS | 1.39s | 0 |

**Total:** 5/5 passed ✅

---

### Advanced Tests

| Test Case | Prompts | Pass | Fail | Pass Rate |
|-----------|---------|------|------|-----------|
| Context Retention | 5 | 4 | 1 | 80% |
| Error Handling | 3 | 3 | 0 | 100% |
| Edge Cases | 4 | 4 | 0 | 100% |
| Guardrail Stress | 5 | 5 | 0 | 100% |
| Multi-Step Complex | 4 | 4 | 0 | 100% |

**Total:** 20/21 passed (95.2%) ✅

---

## 🔧 Key Enhancements

### 1. Message Truncation
Prevents context overflow by keeping only last 20 messages.

```python
MAX_MESSAGES = 20
if len(messages) > MAX_MESSAGES:
    messages = messages[-MAX_MESSAGES:]
```

### 2. Tool Error Handling
Parse errors and suggest fixes for automatic retry.

```python
def tool_node_with_retry(state: AgentState) -> dict:
    try:
        result = tools_dict[tc["name"]].invoke(tc["args"])
    except Exception as e:
        error_msg = parse_tool_error(tc["name"], tc["args"], str(e))
```

### 3. Location Validation
New `check_valid_locations()` tool to avoid city name mismatch bugs.

```python
# Always validate before search
check_valid_locations() → search_flights() → search_hotels()
```

### 4. System Prompt Reinforcement
Added sections for constraint reinforcement in long conversations:
- `<critical_reminder>` - Repeats constraints at end
- `<examples>` - Wrong/Right behavior examples
- `<context_handling>` - Long conversation guidelines
- `<self_check>` - Pre-response checklist

---

## 📝 Mock Data

### Flight Routes (5 routes)
- Ha Noi ↔ Da Nang
- Ha Noi ↔ Phu Quoc
- Ha Noi ↔ Ho Chi Minh
- Ho Chi Minh ↔ Da Nang
- Ho Chi Minh ↔ Phu Quoc

### Hotels (4 cities, 20+ hotels)
- **Ha Noi:** 7 hotels (150k - 4.5M/night)
- **Da Nang:** 5 hotels (250k - 1.8M/night)
- **Phu Quoc:** 4 hotels (200k - 3.5M/night)
- **Ho Chi Minh:** 4 hotels (550k - 2.8M/night)

---

## 📚 Documentation References

This project follows patterns from:
- **Ollama Python:** Model invocation and chat completion
- **LangGraph:** StateGraph, ToolNode, tools_condition, START/END edges
- **Context7:** Best practices for tool-calling agents

---

## 🎯 Rubric Self-Assessment

| Criteria | Score | Evidence |
|----------|-------|----------|
| LangGraph Setup (Nodes, Edges, Graph) | 25/25 | Graph runs stable, correct edges |
| Tool Implementations + Error Handling | 25/25 | 4 tools working, error handling robust |
| System Prompt (Test 4 + Test 5) | 20/20 | Both tests passed |
| Multi-Step Tool Chaining (Test 3) | 20/20 | Full chain: validate → flights → hotels → budget |
| Code Quality (type hints, logging) | 10/10 | Type hints complete, DEV_MODE debug |

**Total: 100/100** ✅

---

## 🐛 Known Issues & Observations

### Issues Found
1. **Context Retention Test:** Agent sometimes calls tools earlier than expected (proactive behavior)
2. **City Name Normalization:** User input "Đà Nẵng" vs mock data "Da Nang" - solved with `check_valid_locations`

### Future Improvements
1. Add city name mapping function for better normalization
2. Test with >50 messages in single session
3. Implement advanced budget categorization
4. Add support for activities and restaurants suggestions
