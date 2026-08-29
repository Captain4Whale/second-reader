"""Producer-specific adapters for the producer-neutral Annotation Pack pipeline."""

from src.annotation_pack.producers.reading_product import (
    ADAPTER_VERSION as READING_PRODUCT_ADAPTER_VERSION,
    ReadingProductProducerAdapter,
)
from src.annotation_pack.producers.second_reader import (
    ADAPTER_VERSION as LEGACY_PHASE9_ADAPTER_VERSION,
    LegacyAttentionalV2Phase9Adapter,
    SecondReaderProducerAdapter,
)

__all__ = [
    "LEGACY_PHASE9_ADAPTER_VERSION",
    "LegacyAttentionalV2Phase9Adapter",
    "READING_PRODUCT_ADAPTER_VERSION",
    "ReadingProductProducerAdapter",
    "SecondReaderProducerAdapter",
]
