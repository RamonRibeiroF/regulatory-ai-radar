from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from regulatory_ai_radar.entities import NewsItem


CAMARA_PROPOSITIONS_URL = (
    "https://dadosabertos.camara.leg.br/api/v2/proposicoes"
)

CAMARA_PUBLIC_URL = (
    "https://www.camara.leg.br/proposicoesWeb/"
    "fichadetramitacao"
)

SEARCH_TERMS = (
    "inteligência artificial",
    "algoritmo",
    "proteção de dados",
    "dados pessoais",
    "cibersegurança",
    "ativos virtuais",
    "sistema financeiro",
    "banco central",
)

PROPOSITION_TYPES = (
    "PL,PLP,PEC,MPV,PDL"
)


def clean_text(text: str) -> str:
    """Remove unnecessary whitespace from text."""

    return " ".join(text.split())


class CamaraCollector:
    """Collect propositions from the Brazilian Chamber of Deputies."""

    def __init__(self) -> None:
        # Step 1: create a reusable HTTP session.
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "RegulatoryAIRadar/0.1 "
                    "(educational and portfolio project)"
                ),
                "Accept": "application/json",
            }
        )

    def _get_propositions(
        self,
        keyword: str,
        start_date: str,
        end_date: str,
        items: int,
    ) -> list[dict[str, Any]]:
        """Request recent propositions for one regulatory keyword."""

        # Step 2: request propositions from the official API.
        response = self.session.get(
            CAMARA_PROPOSITIONS_URL,
            params={
                "keywords": keyword,
                "siglaTipo": PROPOSITION_TYPES,
                "dataApresentacaoInicio": start_date,
                "dataApresentacaoFim": end_date,
                "ordem": "DESC",
                "ordenarPor": "id",
                "itens": items,
            },
            timeout=(10, 30),
        )

        response.raise_for_status()

        # Step 3: force UTF-8 to preserve Portuguese characters.
        response.encoding = "utf-8"

        payload = response.json()
        propositions = payload.get("dados")

        if not isinstance(propositions, list):
            raise ValueError(
                "The Chamber API returned an invalid response."
            )

        return propositions

    def _build_public_url(
        self,
        proposition_id: int,
    ) -> str:
        """Build the official public page for one proposition."""

        # Step 4: create the official proposition tracking URL.
        return (
            f"{CAMARA_PUBLIC_URL}"
            f"?idProposicao={proposition_id}"
        )

    def _normalize_proposition(
        self,
        proposition: dict[str, Any],
    ) -> NewsItem | None:
        """Convert an API proposition into a normalized news item."""

        proposition_id = proposition.get("id")
        proposition_type = proposition.get("siglaTipo")
        proposition_number = proposition.get("numero")
        proposition_year = proposition.get("ano")
        proposition_summary = proposition.get("ementa")
        published_at = proposition.get("dataApresentacao")

        if (
            not isinstance(proposition_id, int)
            or not proposition_type
            or proposition_number is None
            or proposition_year is None
            or not proposition_summary
        ):
            return None

        # Step 5: clean the proposition metadata.
        clean_type = clean_text(str(proposition_type))
        clean_summary = clean_text(str(proposition_summary))
        clean_date = (
            clean_text(str(published_at))
            if published_at
            else None
        )

        proposition_reference = (
            f"{clean_type} "
            f"{proposition_number}/{proposition_year}"
        )

        title = (
            f"{proposition_reference}: "
            f"{clean_summary}"
        )

        # Step 6: create the shared normalized news structure.
        return NewsItem(
            source="CAMARA",
            title=title,
            url=self._build_public_url(
                proposition_id
            ),
            published_at=clean_date,
            summary=clean_summary,
            body=None,
            collected_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

    def collect(
        self,
        limit: int = 5,
        lookback_days: int = 90,
    ) -> list[NewsItem]:
        """Collect the latest relevant legislative propositions."""

        if limit <= 0:
            return []

        if lookback_days <= 0:
            raise ValueError(
                "lookback_days must be greater than zero."
            )

        current_date = datetime.now(
            timezone.utc
        ).date()

        start_date = (
            current_date
            - timedelta(days=lookback_days)
        )

        # Step 7: define the official presentation-date interval.
        formatted_start_date = start_date.isoformat()
        formatted_end_date = current_date.isoformat()

        # Request enough candidates before applying the final limit.
        items_per_term = min(
            max(limit * 4, 20),
            100,
        )

        propositions_by_id: dict[
            int,
            dict[str, Any],
        ] = {}

        # Step 8: search every configured regulatory topic.
        for keyword in SEARCH_TERMS:
            propositions = self._get_propositions(
                keyword=keyword,
                start_date=formatted_start_date,
                end_date=formatted_end_date,
                items=items_per_term,
            )

            # Step 9: remove propositions found by multiple searches.
            for proposition in propositions:
                proposition_id = proposition.get("id")

                if not isinstance(proposition_id, int):
                    continue

                propositions_by_id[proposition_id] = (
                    proposition
                )

        news_items: list[NewsItem] = []

        # Step 10: normalize every unique valid proposition.
        for proposition in propositions_by_id.values():
            news_item = self._normalize_proposition(
                proposition
            )

            if news_item is None:
                continue

            news_items.append(news_item)

        # Step 11: sort all propositions from newest to oldest.
        news_items.sort(
            key=lambda item: (
                item.published_at or ""
            ),
            reverse=True,
        )

        # Step 12: return only the latest requested propositions.
        return news_items[:limit]