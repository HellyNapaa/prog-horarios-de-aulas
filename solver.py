import time
import networkx as nx
from typing import Dict, List, Set, Tuple, Optional


class ConflictGraphSolver:

    def __init__(self,
                 candidatos_por_parte: Dict[str, List[str]],
                 candidate_info: Dict[str, Tuple],
                 conflict_graph: nx.Graph,
                 original_graph: nx.MultiGraph = None): # Adicionado para acessar dados de curso/periodo

        self.candidatos_por_parte = candidatos_por_parte
        self.candidate_info = candidate_info
        self.conflict_graph = conflict_graph
        self.original_graph = original_graph
        self.adj_sets = {cid: set(conflict_graph.neighbors(cid))
                        for cid in conflict_graph.nodes()}

        self.parts_sorted = sorted(
            candidatos_por_parte.keys(),
            key=lambda p: len(candidatos_por_parte[p])
        )

        self.chosen: List[str] = []
        self.best_solution: Optional[List[str]] = None
        self.solutions_found: List[List[str]] = [] # Armazena múltiplas soluções
        self.nodes_explored = 0
        self.start_time = time.time()

    def solve(self, verbose: bool = True, time_limit: int = 15) -> bool:
        """
        Executa o solver.
        :param time_limit: Tempo máximo em segundos para tentar encontrar a MELHOR solução.
        """
        self.start_time = time.time()
        self.nodes_explored = 0
        self.chosen = []
        self.solutions_found = []

        if verbose:
            print(f"Iniciando busca com limite de {time_limit}s para otimização...")

        # Tenta encontrar soluções até o tempo acabar
        try:
            self._backtrack_optimize(0, verbose, time_limit)
        except TimeoutError:
            if verbose: print("\nTempo limite atingido.")
        except Exception as e:
            print(f"Erro durante busca: {e}")

        # Se não encontrou nenhuma
        if not self.solutions_found:
            return False

        # Escolhe a melhor solução baseada nos gaps (janelas)
        if self.original_graph:
            if verbose: 
                print(f"\nAnalisando {len(self.solutions_found)} soluções candidatas...")
            
            # Escolhe a solução com menor pontuação de gap
            best_sol = min(self.solutions_found, key=lambda s: self.calculate_gap_score(s))
            self.best_solution = best_sol
            
            if verbose:
                score = self.calculate_gap_score(best_sol)
                print(f"Melhor solução escolhida (Score de Gaps: {score})")
        else:
            # Se não tiver o grafo original, pega a primeira
            self.best_solution = self.solutions_found[0]

        elapsed = time.time() - self.start_time
        if verbose:
            print(f"\n{'='*50}")
            print(f"Processo finalizado.")
            print(f"Tempo: {elapsed:.2f}s | Nós explorados: {self.nodes_explored}")
            print(f"Soluções encontradas: {len(self.solutions_found)}")
            print(f"{'='*50}\n")

        return True

    def _backtrack_optimize(self, idx: int, verbose: bool, time_limit: int):
        # Checagem periódica de tempo
        if self.nodes_explored % 1000 == 0:
            if time.time() - self.start_time > time_limit:
                # Só lança timeout se JÁ temos pelo menos uma solução
                if self.solutions_found:
                    raise TimeoutError()
        
        self.nodes_explored += 1

        if verbose and self.nodes_explored % 50000 == 0:
            elapsed = time.time() - self.start_time
            print(f"> Explorados: {self.nodes_explored}, Soluções: {len(self.solutions_found)}, Tempo: {elapsed:.1f}s")

        if idx >= len(self.parts_sorted):
            # Encontrou uma solução completa!
            self.solutions_found.append(self.chosen.copy())
            if verbose:
                print(f"  [!] Solução #{len(self.solutions_found)} encontrada.")
            
            # Opcional: Se já achou muitas soluções boas, pode parar antes
            if len(self.solutions_found) >= 50:
                raise TimeoutError()
            return

        part = self.parts_sorted[idx]
        
        # Itera sobre candidatos
        for cand in self.candidatos_por_parte[part]:
            # Verifica conflito com os já escolhidos
            if any(c in self.adj_sets[cand] for c in self.chosen):
                continue
            
            self.chosen.append(cand)
            self._backtrack_optimize(idx + 1, verbose, time_limit)
            self.chosen.pop()

    def calculate_gap_score(self, solution_candidates: List[str]) -> int:
        """
        Calcula penalidade para janelas (gaps) na grade de cada período/curso.
        """
        schedule_map = {} 
        
        for cand_id in solution_candidates:
            d_node, _, _, h_node = self.candidate_info[cand_id]
            
            d_data = self.original_graph.nodes[d_node]
            h_data = self.original_graph.nodes[h_node]
            
            curso = d_data.get('curso')
            periodo = d_data.get('periodo')
            
            if not curso or not periodo:
                continue
            
            # Agrupa aulas por Curso + Período + Dia
            key = (curso, periodo, h_data['dia'])
            if key not in schedule_map:
                schedule_map[key] = []
            schedule_map[key].append(h_data['hora_id'])
            
        total_gaps = 0
        
        for key, hours in schedule_map.items():
            hours.sort()
            if len(hours) > 1:
                # Verifica buracos entre aulas
                for i in range(len(hours) - 1):
                    # Ex: Aula1 as 7h (id 0), Aula2 as 10h (id 2). Gap = 2 - 0 - 1 = 1 buraco.
                    gap = hours[i+1] - hours[i] - 1
                    if gap > 0:
                        # Penalidade quadrática para evitar janelas grandes
                        total_gaps += (gap * gap)
                        
        return total_gaps

    def get_solution(self) -> Optional[List[Tuple]]:
        if self.best_solution is None:
            return None
        return [self.candidate_info[cid] for cid in self.best_solution]