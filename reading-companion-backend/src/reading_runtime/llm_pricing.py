"""Versioned Decimal pricing catalog and provider-usage cost estimates."""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path
from typing import Mapping

from .llm_usage import NormalizedUsage


PRICING_CATALOG_SCHEMA_VERSION = 1
_MILLION = Decimal("1000000")
DEFAULT_PRICING_CATALOG_PATH = Path(__file__).resolve().parents[2] / "config" / "llm_pricing.json"
DEFAULT_LOCAL_PRICING_CATALOG_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "llm_pricing.local.json"
)


class PricingCatalogError(ValueError):
    """Raised when a pricing catalog is invalid or unsupported."""


def _decimal(value: object, *, field: str, nullable: bool = True) -> Decimal | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool):
        raise PricingCatalogError(f"{field} must be a non-negative decimal string or null")
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError) as exc:
        raise PricingCatalogError(f"{field} must be a non-negative decimal string or null") from exc
    if not result.is_finite() or result < 0:
        raise PricingCatalogError(f"{field} must be non-negative and finite")
    return result


def decimal_string(value: Decimal | None) -> str | None:
    """Serialize a Decimal without binary floating-point conversion."""

    return format(value, "f") if value is not None else None


def _timestamp(value: object, *, field: str) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise PricingCatalogError(f"{field} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class PricingSource:
    kind: str
    name: str
    url: str
    observed_at: str

    def to_dict(self) -> dict[str, str]:
        return {
            "kind": self.kind,
            "name": self.name,
            "url": self.url,
            "observed_at": self.observed_at,
        }


@dataclass(frozen=True)
class PricingRule:
    entry_id: str
    provider_id: str
    target_id: str
    model: str
    billing_model: str
    currency: str
    input_per_million: Decimal | None
    output_per_million: Decimal | None
    cache_read_input_per_million: Decimal | None
    cache_write_input_per_million: Decimal | None
    cache_read_pricing_applicable: bool
    cache_write_pricing_applicable: bool
    actual_billed_cost: Decimal | None
    effective_from: datetime | None
    effective_to: datetime | None
    source: PricingSource

    def applies_at(self, at: datetime) -> bool:
        return (self.effective_from is None or at >= self.effective_from) and (
            self.effective_to is None or at < self.effective_to
        )

    def snapshot(self, *, catalog_version: str) -> dict[str, object]:
        payload: dict[str, object] = {
            "catalog_schema_version": PRICING_CATALOG_SCHEMA_VERSION,
            "catalog_version": catalog_version,
            "entry_id": self.entry_id,
            "provider_id": self.provider_id,
            "target_id": self.target_id,
            "model": self.model,
            "billing_model": self.billing_model,
            "currency": self.currency,
            "rates_per_million": {
                "input": decimal_string(self.input_per_million),
                "output": decimal_string(self.output_per_million),
                "cache_read_input": decimal_string(self.cache_read_input_per_million),
                "cache_write_input": decimal_string(self.cache_write_input_per_million),
            },
            "applicable_usage_categories": {
                "cache_read_input": self.cache_read_pricing_applicable,
                "cache_write_input": self.cache_write_pricing_applicable,
            },
            "actual_billed_cost": decimal_string(self.actual_billed_cost),
            "effective_from": self.effective_from.isoformat().replace("+00:00", "Z") if self.effective_from else None,
            "effective_to": self.effective_to.isoformat().replace("+00:00", "Z") if self.effective_to else None,
            "source": self.source.to_dict(),
        }
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        payload["snapshot_hash"] = f"sha256:{hashlib.sha256(encoded).hexdigest()}"
        return payload


@dataclass(frozen=True)
class PricingCatalog:
    catalog_version: str
    rules: tuple[PricingRule, ...]

    @classmethod
    def load(cls, path: Path | str) -> "PricingCatalog":
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PricingCatalogError(f"unable to load pricing catalog: {exc}") from exc
        return cls.from_mapping(payload)

    @classmethod
    def from_mapping(cls, payload: object) -> "PricingCatalog":
        if not isinstance(payload, Mapping):
            raise PricingCatalogError("pricing catalog root must be an object")
        if payload.get("schema_version") != PRICING_CATALOG_SCHEMA_VERSION:
            raise PricingCatalogError(f"unsupported pricing catalog schema_version: {payload.get('schema_version')!r}")
        catalog_version = str(payload.get("catalog_version") or "").strip()
        if not catalog_version:
            raise PricingCatalogError("pricing catalog_version is required")
        raw_entries = payload.get("entries")
        if not isinstance(raw_entries, list) or not raw_entries:
            raise PricingCatalogError("pricing entries must be a non-empty array")
        default_currency = str(payload.get("currency") or "USD").strip().upper() or "USD"
        if default_currency != "USD":
            raise PricingCatalogError(
                "runtime observability v1 only supports USD pricing because its public estimate field is USD-denominated"
            )
        rules = tuple(_parse_rule(entry, default_currency=default_currency, index=index) for index, entry in enumerate(raw_entries))
        identifiers = [rule.entry_id for rule in rules]
        if len(set(identifiers)) != len(identifiers):
            raise PricingCatalogError("pricing entry_id values must be unique")
        return cls(catalog_version=catalog_version, rules=rules)

    def match(
        self,
        *,
        target_id: str | None,
        model: str | None,
        provider_id: str | None = None,
        at: datetime | None = None,
    ) -> PricingRule | None:
        instant = at or datetime.now(timezone.utc)
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=timezone.utc)
        instant = instant.astimezone(timezone.utc)
        requested = {
            "target_id": str(target_id or "").strip().lower(),
            "model": str(model or "").strip().lower(),
            "provider_id": str(provider_id or "").strip().lower(),
        }
        candidates: list[tuple[int, datetime, str, PricingRule]] = []
        for rule in self.rules:
            if not rule.applies_at(instant):
                continue
            rule_model = str(rule.model or "").strip().lower()
            if rule_model not in {"", "*"} and rule_model != requested["model"]:
                continue
            rule_target = str(rule.target_id or "").strip().lower()
            rule_provider = str(rule.provider_id or "").strip().lower()
            if rule_target not in {"", "*"}:
                if rule_target != requested["target_id"]:
                    continue
                # An exact target+model rule is authoritative.  Runtime provider_id
                # is itself the target id in the current registry, so it must not
                # invalidate the higher-priority match.
                score = 100 + (10 if rule_model not in {"", "*"} else 0)
            else:
                if rule_provider not in {"", "*"} and rule_provider != requested["provider_id"]:
                    continue
                score = 50 if rule_provider not in {"", "*"} else 0
                if rule_model not in {"", "*"}:
                    score += 10
            effective = rule.effective_from or datetime.min.replace(tzinfo=timezone.utc)
            candidates.append((score, effective, rule.entry_id, rule))
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
        return candidates[0][3]


@dataclass(frozen=True)
class CostEstimate:
    status: str
    currency: str | None
    billing_model: str
    estimated_usage_value_usd: Decimal | None
    actual_billed_cost: Decimal | None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "status": self.status,
            "currency": self.currency,
            "billing_model": self.billing_model,
            "estimated_usage_value_usd": decimal_string(self.estimated_usage_value_usd),
            "actual_billed_cost": decimal_string(self.actual_billed_cost),
        }


def _parse_rule(raw: object, *, default_currency: str, index: int) -> PricingRule:
    if not isinstance(raw, Mapping):
        raise PricingCatalogError(f"pricing entry {index} must be an object")
    entry_id = str(raw.get("entry_id") or "").strip()
    model = str(raw.get("model") or "").strip()
    target_id = str(raw.get("target_id") or "").strip()
    if not entry_id or not model or not target_id:
        raise PricingCatalogError(f"pricing entry {index} requires entry_id, target_id, and model")
    billing_model = str(raw.get("billing_model") or "unknown").strip().lower()
    if billing_model not in {"metered", "subscription", "free", "unknown"}:
        raise PricingCatalogError(f"pricing entry {entry_id} has unsupported billing_model")
    rates = raw.get("rates_per_million")
    if not isinstance(rates, Mapping):
        raise PricingCatalogError(f"pricing entry {entry_id} rates_per_million must be an object")
    source = raw.get("source")
    if not isinstance(source, Mapping):
        raise PricingCatalogError(f"pricing entry {entry_id} source must be an object")
    effective_from = _timestamp(raw.get("effective_from"), field=f"{entry_id}.effective_from")
    effective_to = _timestamp(raw.get("effective_to"), field=f"{entry_id}.effective_to")
    if effective_from and effective_to and effective_to <= effective_from:
        raise PricingCatalogError(f"pricing entry {entry_id} effective_to must be after effective_from")
    currency = str(raw.get("currency") or default_currency).strip().upper() or default_currency
    if currency != "USD":
        raise PricingCatalogError(
            f"pricing entry {entry_id} uses unsupported currency {currency!r}; v1 supports USD only"
        )
    return PricingRule(
        entry_id=entry_id,
        provider_id=str(raw.get("provider_id") or "*").strip() or "*",
        target_id=target_id,
        model=model,
        billing_model=billing_model,
        currency=currency,
        input_per_million=_decimal(rates.get("input"), field=f"{entry_id}.rates.input"),
        output_per_million=_decimal(rates.get("output"), field=f"{entry_id}.rates.output"),
        cache_read_input_per_million=_decimal(rates.get("cache_read_input"), field=f"{entry_id}.rates.cache_read_input"),
        cache_write_input_per_million=_decimal(rates.get("cache_write_input"), field=f"{entry_id}.rates.cache_write_input"),
        cache_read_pricing_applicable="cache_read_input" in rates,
        cache_write_pricing_applicable="cache_write_input" in rates,
        actual_billed_cost=_decimal(raw.get("actual_billed_cost"), field=f"{entry_id}.actual_billed_cost"),
        effective_from=effective_from,
        effective_to=effective_to,
        source=PricingSource(
            kind=str(source.get("kind") or "unknown").strip() or "unknown",
            name=str(source.get("name") or "").strip(),
            url=str(source.get("url") or "").strip(),
            observed_at=str(source.get("observed_at") or "").strip(),
        ),
    )


def estimate_usage_cost(usage: NormalizedUsage, rule: PricingRule | None) -> CostEstimate:
    """Estimate metered token cost while preserving subscription/null semantics."""

    if rule is None:
        return CostEstimate("unpriced", None, "unknown", None, None)
    if rule.billing_model == "free":
        return CostEstimate("complete", rule.currency, rule.billing_model, Decimal("0"), rule.actual_billed_cost)
    if usage.status != "complete" or usage.input_tokens is None or usage.output_tokens is None:
        return CostEstimate("usage_incomplete", rule.currency, rule.billing_model, None, rule.actual_billed_cost)
    if rule.input_per_million is None or rule.output_per_million is None:
        return CostEstimate("unpriced", rule.currency, rule.billing_model, None, rule.actual_billed_cost)
    cache_read = usage.cache_read_input_tokens
    cache_write = usage.cache_write_input_tokens
    if rule.cache_read_pricing_applicable and cache_read is None:
        return CostEstimate(
            "usage_incomplete_cache_read",
            rule.currency,
            rule.billing_model,
            None,
            rule.actual_billed_cost,
        )
    if rule.cache_write_pricing_applicable and cache_write is None:
        return CostEstimate(
            "usage_incomplete_cache_write",
            rule.currency,
            rule.billing_model,
            None,
            rule.actual_billed_cost,
        )
    cache_read = cache_read or 0
    cache_write = cache_write or 0
    if cache_read and rule.cache_read_input_per_million is None:
        return CostEstimate("unpriced_cache_read", rule.currency, rule.billing_model, None, rule.actual_billed_cost)
    if cache_write and rule.cache_write_input_per_million is None:
        return CostEstimate("unpriced_cache_write", rule.currency, rule.billing_model, None, rule.actual_billed_cost)
    base_input = usage.uncached_input_tokens
    if base_input is None:
        if rule.cache_read_pricing_applicable or rule.cache_write_pricing_applicable:
            return CostEstimate(
                "usage_incomplete_uncached_input",
                rule.currency,
                rule.billing_model,
                None,
                rule.actual_billed_cost,
            )
        base_input = usage.input_tokens
    cache_read_rate = rule.cache_read_input_per_million or Decimal("0")
    cache_write_rate = rule.cache_write_input_per_million or Decimal("0")
    billable_output = usage.billable_output_tokens
    if billable_output is None:
        return CostEstimate(
            "usage_incomplete_billable_output",
            rule.currency,
            rule.billing_model,
            None,
            rule.actual_billed_cost,
        )
    estimated = (
        Decimal(base_input) * rule.input_per_million
        + Decimal(cache_read) * cache_read_rate
        + Decimal(cache_write) * cache_write_rate
        + Decimal(billable_output) * rule.output_per_million
    ) / _MILLION
    return CostEstimate("complete", rule.currency, rule.billing_model, estimated, rule.actual_billed_cost)


def load_pricing_catalog(
    tracked_path: Path | str,
    *,
    local_override_path: Path | str | None = None,
) -> PricingCatalog:
    """Load a complete ignored local override when present, else the tracked catalog."""

    override = Path(local_override_path) if local_override_path is not None else None
    selected = override if override is not None and override.exists() else Path(tracked_path)
    return PricingCatalog.load(selected)


@lru_cache(maxsize=1)
def load_default_pricing_catalog() -> PricingCatalog | None:
    """Load local-or-tracked pricing; absence/invalidity means unpriced."""

    try:
        return load_pricing_catalog(
            DEFAULT_PRICING_CATALOG_PATH,
            local_override_path=DEFAULT_LOCAL_PRICING_CATALOG_PATH,
        )
    except PricingCatalogError:
        return None


__all__ = [
    "CostEstimate",
    "DEFAULT_LOCAL_PRICING_CATALOG_PATH",
    "DEFAULT_PRICING_CATALOG_PATH",
    "PRICING_CATALOG_SCHEMA_VERSION",
    "PricingCatalog",
    "PricingCatalogError",
    "PricingRule",
    "PricingSource",
    "decimal_string",
    "estimate_usage_cost",
    "load_default_pricing_catalog",
    "load_pricing_catalog",
]
