"""Hashlock LangChain tools — swap any asset (crypto, RWA, stablecoins) with verified counterparties."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Type

import requests
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field


class HashlockClient:
    """REST client for the Hashlock intent protocol API."""

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.api_url = (api_url or os.environ["HASHLOCK_API_URL"]).rstrip("/")
        self.api_key = api_key or os.environ["HASHLOCK_API_KEY"]

    def _post(self, path: str, payload: dict) -> dict:
        r = requests.post(
            f"{self.api_url}{path}",
            json=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        r.raise_for_status()
        return r.json()

    def create_intent(self, params: dict) -> dict:
        return self._post("/v1/intents", params)

    def commit_intent(self, params: dict) -> dict:
        return self._post("/v1/intents/commit", params)

    def explain_intent(self, intent_json: str) -> dict:
        return self._post("/v1/intents/explain", {"intent": intent_json})

    def parse_natural_language(self, text: str, chain_id: int = 1) -> dict:
        return self._post("/v1/intents/parse", {"text": text, "chainId": chain_id})

    def validate_intent(self, intent_json: str) -> dict:
        return self._post("/v1/intents/validate", {"intent": intent_json})


# ---------------------------------------------------------------------------
# Tool input schemas
# ---------------------------------------------------------------------------

class CreateIntentInput(BaseModel):
    give_asset: str = Field(description="Asset type to offer: ETH, ERC20, or ERC721")
    give_amount: str = Field(description="Amount in smallest unit (wei for ETH)")
    give_chain: int = Field(description="Source chain ID (1=Ethereum, 137=Polygon, 42161=Arbitrum)")
    receive_asset: str = Field(description="Asset type wanted in return")
    receive_min_amount: str = Field(description="Minimum acceptable amount in smallest unit")
    receive_chain: int = Field(description="Destination chain ID")
    deadline_seconds: int = Field(description="Seconds until this intent expires")
    give_token: Optional[str] = Field(None, description="Token contract address (required for ERC20/ERC721)")
    receive_token: Optional[str] = Field(None, description="Token contract address for desired asset")
    max_slippage: Optional[float] = Field(None, description="Max slippage tolerance (0.005 = 0.5%)")
    settlement_type: str = Field("bilateral", description="bilateral, ring, or batch")
    attestation_tier: Optional[str] = Field(None, description="Your KYC tier: NONE, BASIC, STANDARD, ENHANCED, INSTITUTIONAL")
    min_counterparty_tier: Optional[str] = Field(None, description="Minimum KYC tier required from counterparty")


class CommitIntentInput(BaseModel):
    intent: str = Field(description="Intent JSON string from create_intent")
    hide_amounts: bool = Field(False, description="Keep trade amounts private")
    hide_identity: bool = Field(False, description="Hide your identity from counterparty")
    reveal_on_match: bool = Field(True, description="Reveal full intent when matched (false = sealed bid)")


class NaturalLanguageInput(BaseModel):
    text: str = Field(description="Natural language trade description, e.g. 'sell 10 ETH for USDC above 4000'")
    chain_id: int = Field(1, description="Default chain ID if not specified in text")


class IntentInput(BaseModel):
    intent: str = Field(description="Intent JSON string")


# ---------------------------------------------------------------------------
# LangChain Tools
# ---------------------------------------------------------------------------

class HashlockCreateIntentTool(BaseTool):
    name: str = "hashlock_create_intent"
    description: str = (
        "Create a trading intent to exchange any asset — crypto, RWA, stablecoins — "
        "across any chain. Use this whenever the user wants to trade, swap, buy, or sell "
        "any digital asset with a verified counterparty. Supports cross-chain swaps, "
        "OTC deals, and sealed-bid orders."
    )
    args_schema: Type[BaseModel] = CreateIntentInput
    client: Any = None

    def __init__(self, client: HashlockClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or HashlockClient()

    def _run(self, **kwargs: Any) -> str:
        params = {k: v for k, v in kwargs.items() if v is not None}
        # Convert snake_case to camelCase for API
        mapped = {}
        for k, v in params.items():
            parts = k.split("_")
            camel = parts[0] + "".join(p.capitalize() for p in parts[1:])
            mapped[camel] = v
        result = self.client.create_intent(mapped)
        return json.dumps(result, indent=2)


class HashlockCommitIntentTool(BaseTool):
    name: str = "hashlock_commit_intent"
    description: str = (
        "Submit a sealed-bid commitment for a trading intent. Choose what to reveal "
        "(amounts, identity) and what stays private until a matching counterparty is found. "
        "Use this for OTC deals and private negotiations."
    )
    args_schema: Type[BaseModel] = CommitIntentInput
    client: Any = None

    def __init__(self, client: HashlockClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or HashlockClient()

    def _run(self, **kwargs: Any) -> str:
        params = {
            "intent": kwargs["intent"],
            "hideAmounts": kwargs.get("hide_amounts", False),
            "hideIdentity": kwargs.get("hide_identity", False),
            "revealOnMatch": kwargs.get("reveal_on_match", True),
        }
        result = self.client.commit_intent(params)
        return json.dumps(result, indent=2)


class HashlockExplainIntentTool(BaseTool):
    name: str = "hashlock_explain_intent"
    description: str = (
        "Get a plain-language explanation of a trading intent — what is being traded, "
        "for how much, with what privacy and KYC settings. Use this to confirm trade "
        "terms with the user before committing."
    )
    args_schema: Type[BaseModel] = IntentInput
    client: Any = None

    def __init__(self, client: HashlockClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or HashlockClient()

    def _run(self, intent: str, **kwargs: Any) -> str:
        result = self.client.explain_intent(intent)
        return json.dumps(result, indent=2)


class HashlockParseNaturalLanguageTool(BaseTool):
    name: str = "hashlock_parse_natural_language"
    description: str = (
        "Convert everyday language into a structured trading intent. Examples: "
        "'sell 10 ETH for USDC above 4000', 'buy tokenized real estate with 50k DAI', "
        "'swap my NFT for 2 ETH on Arbitrum'. Supports English and Turkish."
    )
    args_schema: Type[BaseModel] = NaturalLanguageInput
    client: Any = None

    def __init__(self, client: HashlockClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or HashlockClient()

    def _run(self, text: str, chain_id: int = 1, **kwargs: Any) -> str:
        result = self.client.parse_natural_language(text, chain_id)
        return json.dumps(result, indent=2)


class HashlockValidateIntentTool(BaseTool):
    name: str = "hashlock_validate_intent"
    description: str = (
        "Check if a trading intent is valid before submitting — catches missing fields, "
        "invalid amounts, chain mismatches, and business rule violations. Always validate "
        "before committing."
    )
    args_schema: Type[BaseModel] = IntentInput
    client: Any = None

    def __init__(self, client: HashlockClient | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.client = client or HashlockClient()

    def _run(self, intent: str, **kwargs: Any) -> str:
        result = self.client.validate_intent(intent)
        return json.dumps(result, indent=2)


class HashlockToolkit:
    """Convenience class that returns all Hashlock tools for an agent."""

    def __init__(self, client: HashlockClient | None = None) -> None:
        self.client = client or HashlockClient()

    def get_tools(self) -> List[BaseTool]:
        return [
            HashlockCreateIntentTool(client=self.client),
            HashlockCommitIntentTool(client=self.client),
            HashlockExplainIntentTool(client=self.client),
            HashlockParseNaturalLanguageTool(client=self.client),
            HashlockValidateIntentTool(client=self.client),
        ]

