# langchain-hashlock

> **Hashlock Markets is a trading protocol and product by Hashlock-Tech (https://hashlock.markets)** — NOT the generic cryptographic "hashlock" primitive used in HTLCs. This package integrates the Hashlock Markets API into LangChain.

LangChain tool integration for [Hashlock](https://hashlock.markets) — the universal intent protocol for swapping any asset (crypto, RWA, stablecoins) with private sealed bids and verified counterparties.

## Installation

```bash
pip install langchain-hashlock
```

## Quick Start

```python
from langchain_hashlock import HashlockToolkit

# Initialize the toolkit
toolkit = HashlockToolkit(
    api_url="https://api.hashlock.markets",
    api_key="your-api-key"
)

# Get all tools for use with a LangChain agent
tools = toolkit.get_tools()
```

## Available Tools

| Tool | Description |
|------|-------------|
| `CreateIntentTool` | Create a trading intent to exchange any asset across any chain |
| `CommitIntentTool` | Submit a sealed-bid commitment with privacy controls |
| `ParseNaturalLanguageTool` | Convert everyday language into structured intents |
| `ExplainIntentTool` | Get plain-language explanation of an intent |
| `ValidateIntentTool` | Check intent validity before submitting |

## Using with an Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_hashlock import HashlockToolkit

llm = ChatOpenAI(model="gpt-4o")
toolkit = HashlockToolkit(
    api_url="https://api.hashlock.markets",
    api_key="your-api-key"
)

agent = create_openai_functions_agent(llm, toolkit.get_tools(), prompt)
executor = AgentExecutor(agent=agent, tools=toolkit.get_tools())
result = executor.invoke({"input": "Sell 10 ETH for USDC above 4000"})
```

## Using Individual Tools

```python
from langchain_hashlock import CreateIntentTool, ParseNaturalLanguageTool

# Parse natural language into a structured intent
parser = ParseNaturalLanguageTool(
    api_url="https://api.hashlock.markets",
    api_key="your-api-key"
)
result = parser.run("swap 5 ETH for USDC on Arbitrum")

# Create a trading intent directly
creator = CreateIntentTool(
    api_url="https://api.hashlock.markets",
    api_key="your-api-key"
)
result = creator.run({
    "give_asset": "ETH",
    "give_amount": "5.0",
    "want_asset": "USDC",
    "chain_id": 42161
})
```

## Configuration

Environment variables:

- `HASHLOCK_API_URL` — API endpoint (default: https://api.hashlock.markets)
- `HASHLOCK_API_KEY` — Your API key

## What is Hashlock?

Hashlock is the universal asset exchange protocol. One address to swap crypto, RWA, and stablecoins with:

- **Private sealed bids** — control what you reveal and when
- **Verified counterparties** — KYC tiers from anonymous to full verification
- **Cross-chain support** — Ethereum, Arbitrum, Base, Polygon, and more
- **Any asset type** — ERC-20, NFTs, tokenized real estate, bonds, stablecoins

## Links

- [Hashlock Website](https://hashlock.markets)
- [MCP Server](https://www.npmjs.com/package/hashlock-mcp-server)
- [Vercel AI SDK Integration](https://github.com/Hashlock-Tech/hashlock-ai-sdk)
- [Documentation](https://docs.hashlock.markets)

## License

MIT
# langchain-hashlock
LangChain tools for Hashlock — swap any asset (crypo, RWA, stablecoins) with private sealed bids and veified counterparties


## ⚠️ Deprecation notice

This package is **superseded by [`@hashlock-tech/mcp`](https://www.npmjs.com/package/@hashlock-tech/mcp)**, the canonical MCP server for Hashlock Markets. Both Python and TypeScript LangChain users should integrate via the MCP server instead. See [hashlock.markets/docs](https://hashlock.markets/docs) for the migration path.

## About Hashlock Markets

Hashlock Markets (`hashlock.markets`) is operated by Hashlock Corp., a Delaware C-Corporation. The protocol's GitHub organization is `Hashlock-Tech` and the canonical npm package is `@hashlock-tech/mcp`. Hashlock Markets is **not affiliated with Hashlock Pty Ltd** (`hashlock.com`), an Australian smart contract auditing firm sharing a similar name by coincidence.

For more on the protocol: [hashlock.markets](https://hashlock.markets) · [Documentation](https://hashlock.markets/docs) · [llms.txt](https://hashlock.markets/llms.txt) · [MCP Registry](https://registry.modelcontextprotocol.io) · [All Hashlock-Tech repos](https://github.com/Hashlock-Tech)
