# Lab 4 Agent - Base Project (Ollama + LangGraph)

Base scaffold for the TravelBuddy assignment with:
- `requirements.txt` for `pip install`
- `README.md`
- custom mock data
- backend LLM based on Ollama

## Project Structure

- `agent.py`: LangGraph workflow with tool-calling loop
- `tools.py`: custom tools (`search_flights`, `search_hotels`, `calculate_budget`)
- `data/mock_data.py`: custom mock flights/hotels database
- `system_prompt.txt`: base system prompt
- `.env.example`: environment variables for Ollama

## 1) Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2) Start Ollama

Install and run Ollama, then pull a model:

```bash
ollama pull llama3.1:8b
```

Create env file:

```bash
cp .env.example .env
```

## 3) Run

```bash
python agent.py
```

## Notes (Context7 docs used)

This base follows Context7 documentation patterns:
- Ollama Python (`/ollama/ollama-python`): `chat`/`Client`/`AsyncClient` usage, model invocation style.
- LangGraph (`/langchain-ai/langgraph`): `StateGraph`, `ToolNode`, `tools_condition`, `START/END`, `compile()` and `invoke()`.
