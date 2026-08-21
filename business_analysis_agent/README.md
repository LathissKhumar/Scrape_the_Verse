# Business Analysis Agent

A LangGraph-based business analysis agent that performs comprehensive business intelligence analysis through a structured workflow.

## Technical Documentation

For an in-depth breakdown of system architecture, data models, scoring algorithms, and individual agent responsibilities, see [ARCHITECTURE.md](file:///c:/Users/msuke/Documents/Scrape_the_Verse/business_analysis_agent/ARCHITECTURE.md).

## Project Structure

```
business-analysis-agent/
├── main.py                 # Single entry point & output generator
├── requirements.txt        # Dependencies (LangGraph, LangChain Ollama, Pydantic, pytest)
├── .env / .env.example     # Ollama environment configuration
├── README.md               # Quickstart guide
├── ARCHITECTURE.md         # Comprehensive architectural documentation
│
└── business_analysis/
    ├── __init__.py
    ├── graph.py            # LangGraph workflow pipeline definition
    ├── state.py            # TypedDict state management & evidence builder
    ├── llm.py              # ChatOllama provider & structured LLM helpers
    │
    ├── agents/             # Specialized AI sub-agents
    │   ├── __init__.py
    │   ├── business_profile.py     # Business type, model, scale classifier
    │   ├── market_analysis.py       # Industry dynamics & digital adoption analyst
    │   ├── customer_analysis.py     # Customer segments & journey mapper
    │   ├── competitor_analysis.py   # Competitor digital presence & gap analyst
    │   ├── service_analysis.py      # Offering visibility & friction auditor
    │   ├── business_problem.py      # Root problem synthesizer
    │   ├── opportunity.py           # Agency service opportunity mapper
    │   └── business_scoring.py      # 5-factor scoring engine & explainer
    │
    └── schemas/
        ├── __init__.py
        └── models.py       # Pydantic data models & Enums
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

Ensure Ollama is running with the specified model:
```bash
ollama pull qwen3:4b
```

## Usage

Run the agent:

```bash
python main.py
```

The program will interactively ask for business information:
- Company name (required)
- Website URL (optional)
- Industry (required)
- Location (required)
- Business description (optional)
- Products/services (optional)
- Target customers (optional)
- Additional information (optional)

## Output

After analysis completes, the agent saves:
- `outputs/<company>_analysis.json` - Structured analysis data
- `outputs/<company>_report.md` - Human-readable report

## Workflow

The LangGraph workflow executes:
1. **collect_initial_evidence** - Gather and structure input evidence
2. **business_profile** - Classify business type, model, positioning
3. **Parallel Analysis** - Market, Customer, Competitor, Service analysis
4. **business_problem** - Synthesize problems from all analyses
5. **opportunity** - Map problems to agency service opportunities
6. **business_scoring** - Calculate weighted opportunity score
7. **generate_final_report** - Compile final business intelligence report

## Testing

```bash
python -m pytest
```

Tests mock the LLM and do not require Ollama.