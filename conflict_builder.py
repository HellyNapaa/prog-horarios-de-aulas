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

        if di == dj:
            return True

        if pi == pj and hi == hj:
            return True

        if si == sj and hi == hj:
            return True

        disc_i_id = self.graph.nodes[di].get('id')
        disc_j_id = self.graph.nodes[dj].get('id')
        dia_i = self.graph.nodes[hi].get('dia')
        dia_j = self.graph.nodes[hj].get('dia')
        horaid_i = self.graph.nodes[hi].get('hora_id')
        horaid_j = self.graph.nodes[hj].get('hora_id')

        if (disc_i_id == disc_j_id and 
            dia_i == dia_j and 
            abs(horaid_i - horaid_j) == 1):
            return True

        if strict_mode and disc_i_id == disc_j_id and si != sj:
            return True
        return False