# Amazon Bedrock AgentCore Tutorial

A hands-on workshop for building, deploying, and orchestrating AI agents on AWS using Amazon Bedrock AgentCore.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Workshop Modules](#workshop-modules)
- [Quick Start](#quick-start)

## Overview

This workshop guides you from zero to a production-grade multi-agent research system. You will deploy agents to AgentCore Runtime, wire them together using the A2A protocol, and extend them with external tools via MCP Gateway.

## Prerequisites

- Python 3.11+
- AWS account with admin access and Bedrock model access enabled
- AWS CLI configured (`aws configure`)
- `uv` package manager

## Workshop Modules

| # | Module | Description |
|---|--------|-------------|
| 01 | [Getting Started](./01-getting-started/README.md) | Set up AWS credentials, install the AgentCore Starter Toolkit, and verify your environment |
| 02 | [Your First Agent](./02-first-agent/README.md) | Build and deploy a simple research assistant using the Strands framework and `BedrockAgentCoreApp` |
| 03 | [Multi-Agent Coordination](./03-multi-agent-coordination/README.md) | Create an orchestrator + search specialist system using the A2A protocol for agent-to-agent communication |
| 04 | [Research Tools](./04-research-tools/README.md) | Extend agents with external APIs (PubMed), Lambda functions (citation manager), and MCP servers via AgentCore Gateway |

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url>
cd Agentcore-tutorial

# 2. Install dependencies
uv sync
source .venv/bin/activate

# 3. Verify AWS access
aws sts get-caller-identity

# 4. Start with Tutorial 01
open 01-getting-started/README.md
```

## Module Structure

```
Agentcore-tutorial/
├── 01-getting-started/          # Environment setup and AWS configuration
│   └── README.md
├── 02-first-agent/              # Simple agent with Strands + BedrockAgentCoreApp
│   ├── simple_agent.py
│   └── README.md
├── 03-multi-agent-coordination/ # Orchestrator/specialist pattern with A2A
│   ├── agents/
│   │   ├── orchestrator.py
│   │   └── search_specialist.py
│   ├── infrastructure/
│   │   └── invoke_agent.sh
│   └── README.md
└── 04-research-tools/           # MCP Gateway, Lambda tools, MCP servers
    ├── agents/
    │   └── search_specialist.py
    ├── tools/
    │   ├── lambda_citation_manager/
    │   ├── mcp_server/
    │   ├── infrastructure/
    │   └── pubmed-api.yaml
    └── README.md
```
