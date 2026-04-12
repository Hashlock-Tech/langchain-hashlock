# langchain-hashlock

LangChain tool integration for [Hashlock](https://hashlock.ai) — the universal intent protocol for swapping any asset (crypto, RWA, stablecoins) with private sealed bids and verified counterparties.

## Installation

```bash
pip install langchain-hashlock
```

## Quick Start

```python
from langchain_hashlock import HashlockToolkit

# Initialize the toolkit
toolkit = HashlockToolkit(
    api_url="https://api.hashlock.ai",
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
    api_url="https://api.hashlock.ai",
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
    api_url="https://api.hashlock.ai",
    api_key="your-api-key"
)
result = parser.run("swap 5 ETH for USDC on Arbitrum")

# Create a trading intent directly
creator = CreateIntentTool(
    api_url="https://api.hashlock.ai",
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

- `HASHLOCK_API_URL` — API endpoint (default: https://api.hashlock.ai)
- `HASHLOCK_API_KEY` — Your API key

## What is Hashlock?

Hashlock is the universal asset exchange protocol. One address to swap crypto, RWA, and stablecoins with:

- **Private sealed bids** — control what you reveal and when
- **Verified counterparties** — KYC tiers from anonymous to full verification
- **Cross-chain support** — Ethereum, Arbitrum, Base, Polygon, and more
- **Any asset type** — ERC-20, NFTs, tokenized real estate, bonds, stablecoins

## Links

- [Hashlock Website](https://hashlock.ai)
- [MCP Server](https://www.npmjs.com/package/hashlock-mcp-server)
- [Vercel AI SDK Integration](https://github.com/Hashlock-Tech/hashlock-ai-sdk)
- [Documentation](https://docs.hashlock.ai)

## License

MIT
# langchain-hashlock
LangChain tools for Hashlock — swap any asset (crypo, RWA, stablecoins) with private sealed bids and veified counterparties
