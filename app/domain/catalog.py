"""Fonte central de valores de negócio; não há classificação automática em US02."""

from enum import StrEnum

CATALOG_VERSION = "1"


class Category(StrEnum):
    ACESSO = "acesso"
    DEFEITO = "defeito"
    INFRAESTRUTURA = "infraestrutura"
    DUVIDA = "duvida"
    OUTROS = "outros"


class Priority(StrEnum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class TicketStatus(StrEnum):
    ABERTO = "aberto"
    RESOLVIDO = "resolvido"


class TriageStatus(StrEnum):
    PENDENTE = "pendente"
    EM_ANALISE = "em_analise"
    SUGERIDA = "sugerida"
    FALHA = "falha"
    REVISADA = "revisada"
