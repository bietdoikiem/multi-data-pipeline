from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# Declare type hints for CryptoPanic response
@dataclass
class CryptoPanicResponse(dict):
  count: int
  next: Optional[str]
  previous: Optional[str]
  results: list


@dataclass
class CryptoPanicSchema(dict):
  kind: str
  source_title: str
  source_domain: str
  title: str
  published_at: str
  url: str
