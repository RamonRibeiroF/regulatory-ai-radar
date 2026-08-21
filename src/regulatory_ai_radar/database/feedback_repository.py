from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from regulatory_ai_radar.database.models import ArticleFeedback


@dataclass(frozen=True, slots=True)
class FeedbackRecord:
    """Representa o feedback humano retornado pelo repositório."""

    article_id: int
    human_rating: int
    notes: str | None
    created_at: datetime
    updated_at: datetime


class ArticleFeedbackRepository:
    """Fornece operações de banco para o feedback humano."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def get_by_article_id(
        self,
        article_id: int,
    ) -> FeedbackRecord | None:
        """Retorna o feedback atual de uma notícia."""

        # Passo 1: procura o feedback associado à notícia.
        feedback = self.session.scalar(
            select(ArticleFeedback).where(
                ArticleFeedback.article_id == article_id
            )
        )

        if feedback is None:
            return None

        # Passo 2: converte o modelo em um registro estável.
        return self._to_record(feedback)

    def save(
        self,
        article_id: int,
        human_rating: int,
        notes: str | None = None,
    ) -> FeedbackRecord:
        """Cria ou atualiza o feedback de uma notícia."""

        # Passo 3: valida a avaliação antes de acessar o banco.
        if human_rating < 1 or human_rating > 5:
            raise ValueError(
                "Human rating must be between 1 and 5."
            )

        normalized_notes = self._normalize_notes(notes)

        try:
            # Passo 4: procura um feedback existente.
            feedback = self.session.scalar(
                select(ArticleFeedback).where(
                    ArticleFeedback.article_id == article_id
                )
            )

            if feedback is None:
                # Passo 5: cria o primeiro feedback da notícia.
                feedback = ArticleFeedback(
                    article_id=article_id,
                    human_rating=human_rating,
                    notes=normalized_notes,
                )

                self.session.add(feedback)

            else:
                # Passo 6: atualiza o feedback atual.
                feedback.human_rating = human_rating
                feedback.notes = normalized_notes
                feedback.updated_at = datetime.now(timezone.utc)

            # Passo 7: persiste o feedback em uma transação.
            self.session.commit()
            self.session.refresh(feedback)

        except Exception:
            # Passo 8: desfaz as mudanças se a transação falhar.
            self.session.rollback()
            raise

        return self._to_record(feedback)

    def count(self) -> int:
        """Retorna o total de notícias avaliadas."""

        # Passo 9: conta os registros atuais de feedback.
        total = self.session.scalar(
            select(
                func.count(ArticleFeedback.id)
            )
        )

        return total or 0

    @staticmethod
    def _normalize_notes(
        notes: str | None,
    ) -> str | None:
        """Normaliza uma observação humana opcional."""

        if notes is None:
            return None

        normalized_notes = " ".join(notes.split())

        return normalized_notes or None

    @staticmethod
    def _to_record(
        feedback: ArticleFeedback,
    ) -> FeedbackRecord:
        """Converte um modelo ORM em um registro do repositório."""

        return FeedbackRecord(
            article_id=feedback.article_id,
            human_rating=feedback.human_rating,
            notes=feedback.notes,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
        )
