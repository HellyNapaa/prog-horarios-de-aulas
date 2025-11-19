import time
import networkx as nx
from typing import Dict, List, Set, Tuple, Optional


class ConflictGraphSolver:

    def __init__(self,
                 candidatos_por_parte: Dict[str, List[str]],
                 candidate_info: Dict[str, Tuple],
                 conflict_graph: nx.Graph):

        self.candidatos_por_parte = candidatos_por_parte
        self.candidate_info = candidate_info
        self.conflict_graph = conflict_graph
        self.adj_sets = {cid: set(conflict_graph.neighbors(cid))
                        for cid in conflict_graph.nodes()}

        self.parts_sorted = sorted(
            candidatos_por_parte.keys(),
            key=lambda p: len(candidatos_por_parte[p])
        )

        self.chosen: List[str] = []
        self.best_solution: Optional[List[str]] = None
        self.nodes_explored = 0
        self.start_time = time.time()

    def solve(self, verbose: bool = True) -> bool:
        self.start_time = time.time()
        self.nodes_explored = 0
        self.chosen = []

        found = self._backtrack(0, verbose)

        elapsed = time.time() - self.start_time
        if verbose:
            print(f"\n{'='*50}")
            print(f"Backtracking finalizado: {found}")
            print(f"Tempo: {elapsed:.2f}s | Nós explorados: {self.nodes_explored}")
            print(f"{'='*50}\n")

        return found

    def _backtrack(self, idx: int, verbose: bool) -> bool:
        self.nodes_explored += 1

        if verbose and self.nodes_explored % 10000 == 0:
            elapsed = time.time() - self.start_time
            print(f"> Explorados: {self.nodes_explored}, "
                  f"Profundidade: {idx}/{len(self.parts_sorted)}, "
                  f"Tempo: {elapsed:.1f}s")
        if idx >= len(self.parts_sorted):
            self.best_solution = self.chosen.copy()
            return True
        part = self.parts_sorted[idx]
        for cand in self.candidatos_por_parte[part]:
            if any(c in self.adj_sets[cand] for c in self.chosen):
                continue
            self.chosen.append(cand)
            if self._backtrack(idx + 1, verbose):
                return True
            self.chosen.pop()
        return False

    def get_solution(self) -> Optional[List[Tuple]]:
        if self.best_solution is None:
            return None
        return [self.candidate_info[cid] for cid in self.best_solution]