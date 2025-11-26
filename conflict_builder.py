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
        di, pi, si, hi = self.candidate_info[ci]
        dj, pj, sj, hj = self.candidate_info[cj]

        # Mesma disciplina (partes diferentes não podem ser ao mesmo tempo)
        if di == dj:
            return True

        # Mesmo professor no mesmo horário
        if pi == pj and hi == hj:
            return True

        # Mesma sala no mesmo horário
        if si == sj and hi == hj:
            return True

        disc_i_id = self.graph.nodes[di].get('id')
        disc_j_id = self.graph.nodes[dj].get('id')
        
        # Conflito de Grade (Mesmo Curso + Mesmo Período) no mesmo horário ---
        if hi == hj:
            curso_i = self.graph.nodes[di].get('curso')
            periodo_i = self.graph.nodes[di].get('periodo')
            curso_j = self.graph.nodes[dj].get('curso')
            periodo_j = self.graph.nodes[dj].get('periodo')
            
            # Verifica se ambos têm curso/período definidos
            if (curso_i and curso_j and periodo_i and periodo_j):
                # Se for o mesmo curso, mesmo período, e matérias DIFERENTES
                if (str(curso_i) == str(curso_j) and 
                    int(periodo_i) == int(periodo_j) and 
                    disc_i_id != disc_j_id):
                    return True

        dia_i = self.graph.nodes[hi].get('dia')
        dia_j = self.graph.nodes[hj].get('dia')
        horaid_i = self.graph.nodes[hi].get('hora_id')
        horaid_j = self.graph.nodes[hj].get('hora_id')

        # Mesma disciplina em horários adjacentes no mesmo dia (ex: M1 e M2 colados)
        if (disc_i_id == disc_j_id and 
            dia_i == dia_j and 
            abs(horaid_i - horaid_j) == 1):
            return True

        # Strict Mode: Mesma disciplina deve ser na mesma sala (opcional)
        if strict_mode and disc_i_id == disc_j_id and si != sj:
            return True
            
        return False