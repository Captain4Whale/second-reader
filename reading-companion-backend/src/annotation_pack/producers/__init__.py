"""Producer-specific adapters for the producer-neutral Annotation Pack pipeline."""

from src.annotation_pack.producers.second_reader import (
    ADAPTER_VERSION,
    SecondReaderProducerAdapter,
)

__all__ = ["ADAPTER_VERSION", "SecondReaderProducerAdapter"]
