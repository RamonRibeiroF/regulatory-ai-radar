from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResultadoClassificacaoLocal:
    """Representa uma classificação local validada e auditável."""

    avaliacao_estrelas: int
    evidencia_percentual: int
    justificativa: str
    categorias: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Protege os limites e normaliza os textos do resultado."""

        # Passo 1: restringe as estrelas ao intervalo apresentado no painel.
        if type(self.avaliacao_estrelas) is not int or not (
            1 <= self.avaliacao_estrelas <= 5
        ):
            raise ValueError(
                "avaliacao_estrelas deve ser um inteiro entre 1 e 5."
            )

        # Passo 2: mantém a evidência na escala determinística de 0 a 100.
        if type(self.evidencia_percentual) is not int or not (
            0 <= self.evidencia_percentual <= 100
        ):
            raise ValueError(
                "evidencia_percentual deve ser um inteiro entre 0 e 100."
            )

        justificativa = " ".join(self.justificativa.split())
        if not justificativa:
            raise ValueError("justificativa não pode ficar vazia.")

        categorias: list[str] = []
        chaves: set[str] = set()
        for categoria in self.categorias:
            categoria_normalizada = " ".join(categoria.split())
            chave = categoria_normalizada.casefold()
            if not categoria_normalizada or chave in chaves:
                continue
            chaves.add(chave)
            categorias.append(categoria_normalizada)

        object.__setattr__(self, "justificativa", justificativa)
        object.__setattr__(self, "categorias", tuple(categorias))


class ClassificadorLocalDeterministico:
    """Converte a análise determinística existente em cinco estrelas."""

    nome_modelo = "classificador-local-deterministico"
    versao_criterios = "1.1"

    @staticmethod
    def _converter_pontuacao_em_estrelas(pontuacao: int) -> int:
        """Aplica faixas proporcionais de 20 pontos, iguais à escala de impacto."""

        if pontuacao < 20:
            return 1
        if pontuacao < 40:
            return 2
        if pontuacao < 60:
            return 3
        if pontuacao < 80:
            return 4
        return 5

    def classificar(
        self,
        *,
        pontuacao: int,
        palavras_chave: tuple[str, ...] = (),
        categorias: tuple[str, ...] = (),
    ) -> ResultadoClassificacaoLocal:
        """Produz estrelas e explicação sem rede, API ou aleatoriedade."""

        # Passo 3: valida a mesma escala usada pela análise de relevância.
        if type(pontuacao) is not int or not 0 <= pontuacao <= 100:
            raise ValueError("pontuacao deve ser um inteiro entre 0 e 100.")

        estrelas = self._converter_pontuacao_em_estrelas(pontuacao)
        faixas = {
            1: "0–19",
            2: "20–39",
            3: "40–59",
            4: "60–79",
            5: "80–100",
        }

        # Passo 4: registra os elementos objetivos que sustentam o resultado.
        justificativa = (
            f"Pontuação determinística {pontuacao}/100, situada na faixa "
            f"{faixas[estrelas]}: {len(palavras_chave)} palavra(s)-chave "
            f"e {len(categorias)} categoria(s) identificada(s)."
        )

        return ResultadoClassificacaoLocal(
            avaliacao_estrelas=estrelas,
            evidencia_percentual=pontuacao,
            justificativa=justificativa,
            categorias=categorias,
        )
