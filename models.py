from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Disciplina:
    id: str
    sigla_real: str
    nome: str
    tipo: str
    carga: int
    curso: str
    periodo: int
    semestre: int
    prof_responsavel: str

    def __post_init__(self):
        if self.carga <= 0:
            raise ValueError(f"Carga horária deve ser > 0: {self.nome}")
        if self.tipo not in ['obrigatoria', 'optativa']:
            raise ValueError(f"Tipo inválido: {self.tipo}")


@dataclass
class DisciplinaParte:
    sub_id: str
    parte: int
    carga: int
    disciplina_base: Disciplina

    def __getattr__(self, name: str) -> Any:
        return getattr(self.disciplina_base, name)


@dataclass
class Professor:
    id: str
    nome: str
    disciplinas_aptas: List[str] = field(default_factory=list)


@dataclass
class Sala:
    id: str
    nome: str


@dataclass
class Slot:
    id: str
    dia: str
    hora_id: int
    faixa: str


@dataclass
class Alocacao:
    disciplina_sub_id: str
    professor: Professor
    sala: Sala
    slot: Slot