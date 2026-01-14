# 🤖 Multi-Agent Orchestrator

**YAML-driven multi-agent workflow engine** — Define agent collaboration in configuration, execute automatically.

## 🚀 Quick Start

### Installation

```bash
cd multi_agent_orchestrator
pip install -e .
```

### Set API Key

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Run a Workflow

```bash
# Run with real LLM
orchestrate run examples/sequential_research.yaml

# Run with mock LLM (no API key required)
orchestrate run examples/sequential_research.yaml --mock
```

## 📋 YAML Configuration

Define your multi-agent workflow in a simple YAML file:

```yaml
agents:
  - id: researcher
    role: Research Assistant
    goal: Find key insights about electric vehicles

  - id: writer
    role: Content Writer
    goal: Write a summary using the research

workflow:
  type: sequential
  steps:
    - agent: researcher
    - agent: writer
```

## 🔄 Workflow Types

### Sequential Workflow

Agents execute in order, each receiving context from previous agents.

```yaml
workflow:
  type: sequential
  steps:
    - agent: agent1
    - agent: agent2
    - agent: agent3
```

### Parallel Workflow

Agents execute concurrently, with optional aggregation.

```yaml
workflow:
  type: parallel
  branches:
    - backend
    - frontend
  then:
    agent: reviewer
```

## 🛠️ CLI Commands

| Command                       | Description                |
| ----------------------------- | -------------------------- |
| `orchestrate run <file>`      | Execute a workflow         |
| `orchestrate validate <file>` | Validate configuration     |
| `orchestrate show <file>`     | Display workflow structure |

### Options

- `--mock` — Use mock LLM for testing (no API key needed)

## 📁 Project Structure

```
multi_agent_orchestrator/
├── orchestrator/
│   ├── cli.py              # Command-line interface
│   ├── config/             # YAML parsing & validation
│   ├── agents/             # Agent & LLM clients
│   ├── engine/             # Orchestration logic
│   └── tools/              # Tool system
└── examples/               # Example workflows
```

## 💡 Examples

See the `examples/` directory for sample workflows:

- `sequential_research.yaml` — Researcher → Writer pipeline
- `parallel_review.yaml` — Backend + Frontend → Tech Lead review
- `tool_enabled.yaml` — Agent with Python tool access

## 🎯 Core Principle

> **Configuration defines collaboration. Execution is automatic.**

Focus on _what_ agents do and _how_ they interact — not how to wire them together.
