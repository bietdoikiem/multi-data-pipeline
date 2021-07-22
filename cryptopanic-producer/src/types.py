from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# Declare type hints for CryptoPanic response
@dataclass
class CryptoPanicResponse:
  '''Class for persisting the fetch response from CryptoPanic'''
  count: int
  next: Optional[str]
  previous: Optional[str]
  results: list


@dataclass
class CryptoPanicSchema:
  '''Class foro determining the schema to send through Kafka topic'''
  kind: str
  source_title: str
  source_domain: str
  title: str
  published_at: str
  url: str
