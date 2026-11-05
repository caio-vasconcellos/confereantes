from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


Severity = Literal["info", "atencao", "alto"]
RiskLevel = Literal["baixo", "atencao", "alto"]


@dataclass(frozen=True, slots=True)
class Finding:
    severity: Severity
    title: str
    evidence: str
    recommendation: str
    points: int


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    score: int
    level: RiskLevel
    findings: list[Finding] = field(default_factory=list)
    explanation: str | None = None
    explanation_model: str | None = None
    explanation_error: str | None = None

    @property
    def summary(self) -> str:
        if self.level == "alto":
            return "Há sinais relevantes de risco. Não pague nem forneça dados antes de confirmar por um canal oficial."
        if self.level == "atencao":
            return "Existem pontos que merecem confirmação independente antes de continuar."
        return "Nenhum sinal forte foi encontrado pelas regras atuais, mas ainda é necessário confirmar a origem."


@dataclass(frozen=True, slots=True)
class HistoryEntry:
    id: int
    created_at: datetime
    level: RiskLevel
    score: int
    summary: str
    findings: list[Finding]
    original_excerpt: str = ""
    received_excerpt: str = ""

