from typing import Dict, List, Set, Tuple
import networkx as nx
from models import DisciplinaParte, Professor, Sala, Slot
from config import HORARIOS_NOTURNOS


class GraphBuilder:

    def __init__(self):
        self.G = nx.MultiGraph()
        self.candidatos_por_parte: Dict[str, List[str]] = {}
        self.candidate_info: Dict[str, Tuple] = {}

    def add_nodes(self, 
                  disciplinas_partes: List[DisciplinaParte],
                  professores: List[Professor],
                  salas: List[Sala],
                  slots: List[Slot]) -> None:
        for disc_parte in disciplinas_partes:
            node_id = f"disc_{disc_parte.sub_id}"
            self.G.add_node(
                node_id,
                layer="disciplina",
                sub_id=disc_parte.sub_id,
                parte=disc_parte.parte,
                carga=disc_parte.carga,
                id=disc_parte.id,
                sigla_real=disc_parte.sigla_real,
                nome=disc_parte.nome,
                tipo=disc_parte.tipo,
                curso=disc_parte.curso,
                periodo=disc_parte.periodo,
                semestre=disc_parte.semestre
            )
        for prof in professores:
            self.G.add_node(
                f"prof_{prof.id}",
                layer="professor",
                id=prof.id,
                nome=prof.nome,
                disciplinas_aptas=prof.disciplinas_aptas
            )
        for sala in salas:
            self.G.add_node(
                f"sala_{sala.id}",
                layer="sala",
                id=sala.id,
                nome=sala.nome
            )
        for slot in slots:
            self.G.add_node(
                f"slot_{slot.id}",
                layer="horario",
                id=slot.id,
                dia=slot.dia,
                hora_id=slot.hora_id,
                faixa=slot.faixa
            )

    def add_edges(self,
                  disciplinas_partes: List[DisciplinaParte],
                  professores: List[Professor],
                  salas: List[Sala],
                  slots: List[Slot]) -> None:
        for disc_parte in disciplinas_partes:
            disc_node = f"disc_{disc_parte.sub_id}"
            for prof in professores:
                if disc_parte.id in prof.disciplinas_aptas:
                    self.G.add_edge(disc_node, f"prof_{prof.id}", camada="disc-prof")
        for disc_parte in disciplinas_partes:
            disc_node = f"disc_{disc_parte.sub_id}"
            for sala in salas:
                self.G.add_edge(disc_node, f"sala_{sala.id}", camada="disc-sala")
        for disc_parte in disciplinas_partes:
            disc_node = f"disc_{disc_parte.sub_id}"
            for slot in slots:
                slot_node = f"slot_{slot.id}"
                if (str(disc_parte.curso).strip().upper() == 'SIN' and
                    disc_parte.tipo == 'obrigatoria' and
                    slot.hora_id not in HORARIOS_NOTURNOS):
                    continue
                preferencial_optativa = (
                    disc_parte.tipo == 'optativa' and slot.hora_id in HORARIOS_NOTURNOS
                )
                self.G.add_edge(
                    disc_node,
                    slot_node,
                    camada="disc-horario",
                    preferencial_optativa=preferencial_optativa
                )

    def generate_candidates(self,
                           disciplinas_partes: List[DisciplinaParte]) -> None:
        for disc_parte in disciplinas_partes:
            disc_node = f"disc_{disc_parte.sub_id}"
            self.candidatos_por_parte[disc_parte.sub_id] = []
            profs_validos = [n for n in self.G.neighbors(disc_node) if n.startswith("prof_")]
            salas_validas = [n for n in self.G.neighbors(disc_node) if n.startswith("sala_")]
            slots_validos = [n for n in self.G.neighbors(disc_node) if n.startswith("slot_")]
            for prof in profs_validos:
                for sala in salas_validas:
                    for slot in slots_validos:
                        cand_id = self._make_cand_id(disc_parte.sub_id, prof, sala, slot)
                        self.candidatos_por_parte[disc_parte.sub_id].append(cand_id)
                        self.candidate_info[cand_id] = (disc_node, prof, sala, slot)
        for sub_id, cands in self.candidatos_por_parte.items():
            if not cands:
                raise ValueError(f"Disciplina {sub_id} não possui candidatos válidos")

    @staticmethod
    def _make_cand_id(dsub: str, prof_node: str, sala_node: str, slot_node: str) -> str:
        return f"assign_{dsub}__{prof_node}__{sala_node}__{slot_node}"

    def get_graph(self) -> nx.MultiGraph:
        return self.G