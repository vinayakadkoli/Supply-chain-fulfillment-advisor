# Supply Chain Fulfillment Advisor

An AI agent that analyzes sales order fulfillment feasibility by checking inventory levels, calculating fulfillment gaps, scanning open purchase orders, and recommending delivery actions.

## Overview

Uses A2A Protocol, LangGraph, LiteLLM, and SAP Cloud SDK.

## Structure

- `app/main.py` - A2A server entry
- `app/agent_executor.py` - Request handling
- `app/agent.py` - Agent logic
