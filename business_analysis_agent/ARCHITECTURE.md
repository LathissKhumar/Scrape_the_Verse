# Architecture & Component Documentation: Business Analysis Agent

## Overview

The **Business Analysis Agent** is a multi-agent, LangGraph-driven business intelligence system. It takes user input about a target company (e.g., name, website, industry, location, services), structures initial evidence, and executes an orchestrated multi-agent pipeline powered by Ollama (`qwen3:4b`). The system evaluates digital presence, synthesizes business problems, maps them to agency service opportunities, and calculates an overall weighted opportunity score (0-100).

---

## Folder Structure

```
business_analysis_agent/
├── main.py                         # Application CLI entry point & output generator
├── requirements.txt                # Python dependencies (langgraph, langchain-ollama, pydantic, pytest)
├── .env / .env.example             # Configuration for Ollama host & model
├── README.md                       # Project quickstart and general guide
├── ARCHITECTURE.md                 # Technical architecture & component documentation
│
├── business_analysis/              # Core business analysis module
│   ├── __init__.py                 # Module marker
│   ├── graph.py                    # LangGraph StateGraph workflow definition & execution nodes
│   ├── state.py                    # State dictionary definition (BusinessAnalysisState) & evidence builder
│   ├── llm.py                      # Ollama LLM provider & structured output helpers
│   │
│   ├── agents/                     # Specialized agent nodes for individual analysis tasks
│   │   ├── __init__.py
│   │   ├── business_profile.py     # Classifies business model, type, offerings, scale
│   │   ├── market_analysis.py       # Analyzes industry conditions, digital adoption, search behavior
│   │   ├── customer_analysis.py     # Maps customer segments, user journey stages, conversion actions
│   │   ├── competitor_analysis.py   # Analyzes competitor positioning, digital presence, and gaps
│   │   ├── service_analysis.py      # Evaluates service visibility, discoverability, friction
│   │   ├── business_problem.py      # Synthesizes business problems based on multi-domain analysis
│   │   ├── opportunity.py           # Maps business problems to digital agency service offerings
│   │   └── business_scoring.py      # Computes weighted score breakdown and score explanation
│   │
│   └── schemas/
│       ├── __init__.py
│       └── models.py               # Pydantic models & Enums defining state objects & API contracts
│
└── tests/
    ├── __init__.py
    └── test_business_analysis.py   # Pytest suite with mock LLM calls
```

---

## Key Components & Descriptions

### 1. Main Entry Point & Output Management

#### `main.py`
- **Purpose**: Serves as the primary CLI entry point for running the agent.
- **Key Functions**:
  - `collect_user_input()`: Interactively prompts the user for business information (Company name, Website, Industry, Location, Description, Services, Target customers).
  - `main()`: Instantiates initial state, compiles and executes the LangGraph pipeline, and renders results.
  - `display_result()`: Prints structured summary results (scores, priority, recommended services, business problems, key opportunities) directly to the console.
  - `save_outputs()`: Exports analysis output to `outputs/<company>_analysis.json` and `outputs/<company>_report.md`.
  - `generate_markdown_report()`: Formats complete analysis state into a human-readable Markdown report.

---

### 2. Workflow Orchestration & State Management

#### `business_analysis/graph.py`
- **Purpose**: Defines and compiles the `StateGraph` workflow using `langgraph`.
- **Workflow Pipeline Execution**:
  1. `collect_initial_evidence`: Initializes state evidence array.
  2. `business_profile`: Runs `business_profile_agent`.
  3. `parallel_analysis`: Concurrently executes Market, Customer, Competitor, and Service analysis nodes in parallel using Python's `ThreadPoolExecutor(max_workers=4)` for fast execution.
  4. `business_problem`: Runs `business_problem_agent` to synthesize root problems.
  5. `opportunity`: Runs `opportunity_agent` to map problems to agency services.
  6. `business_scoring`: Calculates component scores and priority.
  7. `generate_final_report`: Compiles `FinalBusinessAnalysis` object.

#### `business_analysis/state.py`
- **Purpose**: Defines `BusinessAnalysisState` (a `TypedDict`) passed across graph nodes.
- **Key Features**:
  - `create_initial_state()`: Converts `BusinessInput` into initial `Evidence` items with confidence scores (1.0 for mandatory input, 0.9 for optional fields).
  - Maintains domain data structures: `business_profile`, `market_analysis`, `customer_analysis`, `competitor_analysis`, `service_analysis`, `business_problems`, `opportunities`, `business_score`, `final_report`, `errors`.

#### `business_analysis/llm.py`
- **Purpose**: Centralized wrapper for Ollama integration using `langchain-ollama`.
- **Key Functions & Speed Optimizations**:
  - `get_llm()`: Initializes singleton `ChatOllama` instance with configurable `OLLAMA_BASE_URL` and `OLLAMA_MODEL` (default: `qwen3:4b`).
  - **Performance Parameters**:
    - `keep_alive="1h"`: Keeps the model loaded in RAM between runs to eliminate cold-start reload overhead.
    - `num_ctx=4096`: Limits context window allocation to prevent memory pressure on system RAM.
    - `num_predict=1024`: Limits output token generation to prevent runaway response loops.
    - `timeout=120`: Sets timeout limits to handle slow network/inference gracefully.
  - `get_structured_llm(output_model)`: Wraps LLM with Pydantic structured output enforcement.
  - `invoke_llm()` & `ainvoke_llm()`: Synchronous and asynchronous execution helpers.

---

### 3. Data Schemas & Models

#### `business_analysis/schemas/models.py`
- **Purpose**: Holds all Pydantic models and Enums for strict typing and structured LLM outputs.
- **Key Models & Enums**:
  - `SourceType`, `Evidence`: Track origin, confidence (0.0-1.0), and claims.
  - `BusinessType`, `BusinessModel`, `CompanyScale`, `BusinessProfile`: Store business metadata.
  - `MarketCondition`, `DigitalAdoptionLevel`, `MarketAnalysis`: Store market dynamics.
  - `CustomerSegment`, `JourneyStage`, `CustomerJourneyStep`, `ConversionAction`, `CustomerAnalysis`: Model customer behavior and touchpoints.
  - `Competitor`, `CompetitorAnalysis`: Track competitive landscape and gaps.
  - `ServiceImportance`, `ServiceVisibility`, `Service`, `ServiceAnalysis`: Audit digital representation of offerings.
  - `ProblemSeverity`, `BusinessProblem`: Define identified problems, impacts, and confidence.
  - `AgencyService`, `Opportunity`: Enumerate agency services (`NEW_WEBSITE`, `SEO`, `LOCAL_SEO`, `CONTENT`, `CONVERSION_OPTIMIZATION`, etc.) and mapped opportunities.
  - `ScoreCategory`, `BusinessScore`: Structured scoring model.
  - `FinalBusinessAnalysis`, `BusinessInput`: Top-level input and output schemas.

---

### 4. Specialized Analysis Agents (`business_analysis/agents/`)

Each agent consumes the current state and returns an updated dictionary slice:

1. **`business_profile.py` (`business_profile_agent`)**
   - Classifies company scale, business type (e.g., local service, SaaS, B2B service), business model (B2B, B2C, hybrid), offerings, positioning, and target market.

2. **`market_analysis.py` (`market_analysis_agent`)**
   - Evaluates industry condition (growing, stable, declining), customer acquisition environment, digital adoption level, search behavior, and digital growth opportunities.

3. **`customer_analysis.py` (`customer_analysis_agent`)**
   - Identifies customer segments, maps customer journey stages (Discovery, Evaluation, Trust, Decision, Conversion), customer needs, and conversion actions.

4. **`competitor_analysis.py` (`competitor_analysis_agent`)**
   - Evaluates key competitors, their positioning, digital presence, website quality, SEO status, and identified market gaps.

5. **`service_analysis.py` (`service_analysis_agent`)**
   - Audits individual business services for online visibility, discoverability, CTA presence, customer friction points, and content gaps.

6. **`business_problem.py` (`business_problem_agent`)**
   - Synthesizes findings from all prior analyses to extract actionable business problems with impact ratings (1-10), confidence scores, and severity levels (`critical`, `high`, `medium`, `low`).

7. **`opportunity.py` (`opportunity_agent`)**
   - Uses deterministic keyword mapping (`PROBLEM_TO_SERVICE_MAP`) combined with LLM context reasoning to convert business problems into actionable agency opportunities with assigned priorities (1-10) and estimated impact statements.

8. **`business_scoring.py` (`business_scoring_agent`)**
   - Calculates a deterministic weighted overall score (0-100) based on 5 core metrics:
     - **Business Fit (20%)**: Based on company scale, business type, market condition, competitor density.
     - **Digital Need (25%)**: Based on current service visibility, market digital adoption, key gaps, competitor digital strength.
     - **Opportunity Value (25%)**: Based on average priority of opportunities and count of critical problems.
     - **Evidence Confidence (15%)**: Based on confidence scores across collected evidence and synthesized problems.
     - **Serviceability (15%)**: Based on ease of delivering agency solutions for the business profile.
   - Assigns priority category (`VERY_HIGH` >= 80, `HIGH` >= 60, `MEDIUM` >= 40, `LOW` < 40).
   - Generates LLM explanation for score rationale.

---

### 5. Test Suite

#### `tests/test_business_analysis.py`
- **Purpose**: Automated pytest test suite.
- **Features**: Mocks LLM responses (`unittest.mock`) to verify graph flow, state mutations, schema validation, and scoring logic deterministically without calling Ollama.
