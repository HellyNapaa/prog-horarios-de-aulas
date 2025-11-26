from typing import Dict, List, Tuple, Set
import networkx as nx


class ConflictBuilder:

    def __init__(self,
                 graph: nx.MultiGraph,
                 candidate_info: Dict[str, Tuple]):

        self.graph = graph
        self.candidate_info = candidate_info

    def build(self, strict_mode: bool = True) -> nx.Graph:
        A = nx.Graph()
        cids = list(self.candidate_info.keys())
        A.add_nodes_from(cids)

        for i in range(len(cids)):
            for j in range(i + 1, len(cids)):
                ci, cj = cids[i], cids[j]
                if self._has_conflict(ci, cj, strict_mode):
                    A.add_edge(ci, cj)

        return A

    def _has_conflict(self, ci: str, cj: str, strict_mode: bool) -> bool:

        di, pi, si, hi = self.candidate_info[ci]   # disciplina, prof, sala, slot
        dj, pj, sj, hj = self.candidate_info[cj]

        # -------------------------------
        # Regra 1 – Mesma disciplina
        # -------------------------------
        if di == dj:
            return True

        # -------------------------------
        # Regra 2 – Mesmo professor no mesmo horário
        # -------------------------------
        if pi == pj and hi == hj:
            return True

        # -------------------------------
        # Regra 3 – Mesma sala no mesmo horário
        # -------------------------------
        if si == sj and hi == hj:
            return True

        disc_i_id = self.graph.nodes[di].get('id')
        disc_j_id = self.graph.nodes[dj].get('id')

        # -------------------------------
        # Regra 4 – Conflito de Grade
        # -------------------------------
        if hi == hj:
            curso_i = self.graph.nodes[di].get('curso')
            periodo_i = self.graph.nodes[di].get('periodo')
            curso_j = self.graph.nodes[dj].get('curso')
            periodo_j = self.graph.nodes[dj].get('periodo')

            if (curso_i and curso_j and periodo_i and periodo_j):
                if (str(curso_i) == str(curso_j) and
                    int(periodo_i) == int(periodo_j) and
                    disc_i_id != disc_j_id):
                    return True

        dia_i = self.graph.nodes[hi].get('dia')
        dia_j = self.graph.nodes[hj].get('dia')
        horaid_i = self.graph.nodes[hi].get('hora_id')
        horaid_j = self.graph.nodes[hj].get('hora_id')

        # Duracao do slot (assume 1h se não tiver)
        dur_i = self.graph.nodes[hi].get("duracao", 1)
        dur_j = self.graph.nodes[hj].get("duracao", 1)

        # -------------------------------
        # Regra 5 – Máximo 8h do mesmo professor no mesmo dia
        # -------------------------------
        if pi == pj and dia_i == dia_j:
            if (dur_i + dur_j) > 8:
                return True

        # -------------------------------
        # Regra 6 – Duplas adjacentes (caso não permitido)
        # -------------------------------
        if (disc_i_id == disc_j_id and
            dia_i == dia_j and
            abs(horaid_i - horaid_j) == 1):
            return True

        # -------------------------------
        # Regra 7 – Strict Mode: disciplina deve ter mesma sala
        # -------------------------------
        if strict_mode and disc_i_id == disc_j_id and si != sj:
            return True

        return False
