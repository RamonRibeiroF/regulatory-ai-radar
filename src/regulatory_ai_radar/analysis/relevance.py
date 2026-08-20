from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass


# Step 1: define the score thresholds used by the analyzer.
MEDIUM_RELEVANCE_SCORE = 30
HIGH_RELEVANCE_SCORE = 60
MAXIMUM_RELEVANCE_SCORE = 100

NON_ALPHANUMERIC_PATTERN = re.compile(
    r"[^a-z0-9]+"
)


# Step 2: represent one weighted regulatory keyword.
@dataclass(frozen=True, slots=True)
class KeywordRule:
    """Represent a keyword and its regulatory relevance weight."""

    keyword: str
    category: str
    weight: int


# Step 3: define the result returned by the relevance analyzer.
@dataclass(frozen=True, slots=True)
class RelevanceResult:
    """Represent the regulatory relevance analysis of an article."""

    score: int
    level: str
    is_relevant: bool
    matched_keywords: tuple[str, ...]
    matched_categories: tuple[str, ...]


# Step 4: define auditable keyword rules for the initial scoring model.
KEYWORD_RULES = (
    KeywordRule(
        keyword="inteligência artificial",
        category="artificial_intelligence",
        weight=20,
    ),
    KeywordRule(
        keyword="artificial intelligence",
        category="artificial_intelligence",
        weight=20,
    ),
    KeywordRule(
        keyword="regulação de ia",
        category="ai_regulation",
        weight=20,
    ),
    KeywordRule(
        keyword="regulation of artificial intelligence",
        category="ai_regulation",
        weight=20,
    ),
    KeywordRule(
        keyword="ai act",
        category="ai_regulation",
        weight=20,
    ),
    KeywordRule(
        keyword="governança de ia",
        category="ai_governance",
        weight=16,
    ),
    KeywordRule(
        keyword="ai governance",
        category="ai_governance",
        weight=16,
    ),
    KeywordRule(
        keyword="ia generativa",
        category="generative_ai",
        weight=16,
    ),
    KeywordRule(
        keyword="generative ai",
        category="generative_ai",
        weight=16,
    ),
    KeywordRule(
        keyword="risco de modelo",
        category="model_risk",
        weight=14,
    ),
    KeywordRule(
        keyword="model risk",
        category="model_risk",
        weight=14,
    ),
    KeywordRule(
        keyword="decisão automatizada",
        category="automated_decisions",
        weight=14,
    ),
    KeywordRule(
        keyword="automated decision",
        category="automated_decisions",
        weight=14,
    ),
    KeywordRule(
        keyword="sandbox regulatório",
        category="regulatory_innovation",
        weight=12,
    ),
    KeywordRule(
        keyword="regulatory sandbox",
        category="regulatory_innovation",
        weight=12,
    ),
    KeywordRule(
        keyword="lgpd",
        category="data_protection",
        weight=12,
    ),
    KeywordRule(
        keyword="proteção de dados",
        category="data_protection",
        weight=10,
    ),
    KeywordRule(
        keyword="data protection",
        category="data_protection",
        weight=10,
    ),
    KeywordRule(
        keyword="reconhecimento facial",
        category="biometrics",
        weight=10,
    ),
    KeywordRule(
        keyword="facial recognition",
        category="biometrics",
        weight=10,
    ),
    KeywordRule(
        keyword="instituição financeira",
        category="financial_regulation",
        weight=10,
    ),
    KeywordRule(
        keyword="financial institution",
        category="financial_regulation",
        weight=10,
    ),
    KeywordRule(
        keyword="banco central",
        category="financial_regulation",
        weight=10,
    ),
    KeywordRule(
        keyword="central bank",
        category="financial_regulation",
        weight=10,
    ),
    KeywordRule(
        keyword="privacidade",
        category="data_protection",
        weight=8,
    ),
    KeywordRule(
        keyword="privacy",
        category="data_protection",
        weight=8,
    ),
    KeywordRule(
        keyword="algoritmo",
        category="algorithms",
        weight=8,
    ),
    KeywordRule(
        keyword="algorithm",
        category="algorithms",
        weight=8,
    ),
    KeywordRule(
        keyword="inteligência de dados",
        category="data_intelligence",
        weight=6,
    ),
    KeywordRule(
        keyword="data intelligence",
        category="data_intelligence",
        weight=6,
    ),
    KeywordRule(
        keyword="ia",
        category="artificial_intelligence",
        weight=6,
    ),
    KeywordRule(
        keyword="ai",
        category="artificial_intelligence",
        weight=6,
    ),
)


# Step 5: normalize text for accent-insensitive keyword matching.
def normalize_text(text: str | None) -> str:
    """Normalize text for consistent keyword comparison."""

    if not text:
        return ""

    text_without_accents = unicodedata.normalize(
        "NFKD",
        text,
    ).encode(
        "ascii",
        "ignore",
    ).decode(
        "ascii"
    )

    normalized_text = NON_ALPHANUMERIC_PATTERN.sub(
        " ",
        text_without_accents.lower(),
    )

    return " ".join(
        normalized_text.split()
    )


# Step 6: check whether a complete keyword exists in normalized text.
def contains_keyword(
    normalized_text: str,
    normalized_keyword: str,
) -> bool:
    """Check whether a normalized keyword occurs as complete words."""

    searchable_text = f" {normalized_text} "
    searchable_keyword = f" {normalized_keyword} "

    return searchable_keyword in searchable_text


# Step 7: convert a numerical score into a relevance level.
def determine_relevance_level(score: int) -> str:
    """Return the relevance level associated with a score."""

    if score >= HIGH_RELEVANCE_SCORE:
        return "high"

    if score >= MEDIUM_RELEVANCE_SCORE:
        return "medium"

    return "low"


class RelevanceAnalyzer:
    """Calculate an auditable regulatory relevance score."""

    def __init__(
        self,
        rules: tuple[KeywordRule, ...] = KEYWORD_RULES,
    ) -> None:
        self.rules = rules

    def analyze(
        self,
        title: str,
        summary: str | None = None,
        body: str | None = None,
    ) -> RelevanceResult:
        """Analyze the regulatory relevance of one article."""

        # Step 8: normalize the title and complete article content.
        normalized_title = normalize_text(
            title
        )

        normalized_content = normalize_text(
            " ".join(
                part
                for part in (
                    title,
                    summary,
                    body,
                )
                if part
            )
        )

        total_score = 0
        matched_keywords: list[str] = []
        matched_categories: list[str] = []

        # Step 9: apply every keyword rule to the article.
        for rule in self.rules:
            normalized_keyword = normalize_text(
                rule.keyword
            )

            if not contains_keyword(
                normalized_content,
                normalized_keyword,
            ):
                continue

            keyword_score = rule.weight

            # Step 10: increase the weight when the keyword is in the title.
            if contains_keyword(
                normalized_title,
                normalized_keyword,
            ):
                keyword_score += round(
                    rule.weight * 0.5
                )

            total_score += keyword_score
            matched_keywords.append(
                rule.keyword
            )

            if rule.category not in matched_categories:
                matched_categories.append(
                    rule.category
                )

        # Step 11: limit the final score and determine its level.
        final_score = min(
            total_score,
            MAXIMUM_RELEVANCE_SCORE,
        )

        relevance_level = determine_relevance_level(
            final_score
        )

        # Step 12: return the complete and explainable result.
        return RelevanceResult(
            score=final_score,
            level=relevance_level,
            is_relevant=(
                final_score
                >= MEDIUM_RELEVANCE_SCORE
            ),
            matched_keywords=tuple(
                matched_keywords
            ),
            matched_categories=tuple(
                matched_categories
            ),
        )