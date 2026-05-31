"""
Confidence scoring for RoO determinations.

Replaces ad-hoc magic numbers (0.92, 0.75, 0.6) with a principled model:

  confidence = specificity × completeness × result_scale

Factors
-------
- specificity : how precisely the rule was matched (subheading > heading > chapter default)
- completeness: fraction of BOM lines whose origin is known
- result_scale : FAIL determinations are generally more certain than PASS
- historical  : optional calibration from the corrections table (Platt-style blend)

Once enough corrections accumulate, `HistoricalCalibrator` reads from the DB
and the confidence scores tighten to match observed accuracy.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal


MatchLevel = Literal["subheading", "heading", "chapter", "none"]
ResultType = Literal["pass", "fail", "insufficient_data"]

# Blend weight for historical calibration once sufficient samples exist
_HISTORICAL_WEIGHT = 0.30
_MIN_SAMPLES_FOR_CALIBRATION = 20


@dataclass
class ConfidenceFactors:
    matched_level: MatchLevel
    result_type: ResultType
    total_bom_lines: int = 0
    unknown_origin_lines: int = 0
    rule_text_present: bool = True
    # Filled in by HistoricalCalibrator if enough corrections exist
    historical_accuracy: float | None = None


def compute_confidence(factors: ConfidenceFactors) -> float:
    """
    Return a calibrated confidence score in [0, 1].

    The score is NOT a probability; it encodes how much we trust the
    determination, accounting for rule specificity, BOM data quality,
    and (optionally) observed historical accuracy for this rule type.
    """
    if factors.matched_level == "none" or factors.result_type == "insufficient_data":
        return 0.0

    # ── Specificity ──────────────────────────────────────────────────────────
    specificity = {
        "subheading": 0.92,
        "heading":    0.84,
        "chapter":    0.72,
    }[factors.matched_level]

    if not factors.rule_text_present:
        specificity *= 0.85  # no source text = lower trust

    # ── Data completeness ─────────────────────────────────────────────────────
    if factors.total_bom_lines == 0:
        # No BOM: deterministic engine had nothing to compute — moderate penalty
        completeness = 0.70
    else:
        known = factors.total_bom_lines - factors.unknown_origin_lines
        known_pct = known / factors.total_bom_lines
        # Sigmoid-shaped: 100% known → 1.0; 0% known → 0.60
        completeness = 0.60 + 0.40 * known_pct

    # ── Result direction ──────────────────────────────────────────────────────
    # FAIL is generally more certain: one failing component is enough.
    # PASS requires every condition to be satisfied — more ways to be wrong.
    result_scale = 1.05 if factors.result_type == "fail" else 1.0

    structural = min(1.0, specificity * completeness * result_scale)

    # ── Historical calibration ────────────────────────────────────────────────
    if factors.historical_accuracy is not None:
        score = (
            (1 - _HISTORICAL_WEIGHT) * structural
            + _HISTORICAL_WEIGHT * factors.historical_accuracy
        )
    else:
        score = structural

    return round(min(1.0, max(0.0, score)), 4)


class HistoricalCalibrator:
    """
    Reads from the human_corrections table to compute agreement-level
    accuracy rates. Used to blend structural confidence with observed accuracy.

    Results are cached in-process for the duration of a worker restart.
    In production, the Celery calibration task refreshes the cache periodically.
    """

    _cache: dict[str, float] = {}
    _sample_counts: dict[str, int] = {}
    _loaded: bool = False

    @classmethod
    def load(cls, database_url: str | None = None) -> None:
        """Pull accuracy stats from DB into the in-process cache."""
        url = database_url or os.getenv("DATABASE_URL", "")
        if not url:
            return
        try:
            from sqlalchemy import create_engine, text
            url = url.replace("+asyncpg", "")
            engine = create_engine(url, pool_pre_ping=True)
            with engine.connect() as conn:
                rows = conn.execute(text("""
                    SELECT
                        agreement_code,
                        COUNT(*)                                                   AS total,
                        SUM(CASE WHEN corrected_result = original_result THEN 1 ELSE 0 END) AS correct
                    FROM human_corrections
                    WHERE corrected_result IS NOT NULL
                    GROUP BY agreement_code
                """)).fetchall()
            for row in rows:
                code, total, correct = row
                cls._sample_counts[code] = int(total)
                if int(total) >= _MIN_SAMPLES_FOR_CALIBRATION:
                    cls._cache[code] = float(correct) / float(total)
            cls._loaded = True
        except Exception:
            pass  # DB unavailable — operate uncalibrated

    @classmethod
    def get_accuracy(cls, agreement_code: str) -> float | None:
        if not cls._loaded:
            cls.load()
        return cls._cache.get(agreement_code.lower())

    @classmethod
    def sample_count(cls, agreement_code: str) -> int:
        return cls._sample_counts.get(agreement_code.lower(), 0)
