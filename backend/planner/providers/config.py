import os
from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
class ProviderConfig:
    openroutes_api_key: str | None
    locationiq_api_key: str | None
    maptiler_api_key: str | None
    
    timeout_seconds: int = 10
    
    @classmethod
    def from_env(cls) -> Self:
        return cls(
            openroutes_api_key=os.getenv("OPENROUTES_API_KEY"),
            locationiq_api_key=os.getenv("LOCATIONIQ_API_KEY"),
            maptiler_api_key=os.getenv("MAPTILER_API_KEY"),
            timeout_seconds=int(os.getenv("PLANNER_API_TIMEOUT", "10")),
        )

provider_config = ProviderConfig.from_env()
