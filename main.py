import sys
from typing import List, Optional


from config import SEMANA, HORARIOS, HORARIOS_NOTURNOS
from models import Disciplina, Professor, Sala, Slot
from data_processor import DataProcessor
from graph_builder import GraphBuilder
from conflict_builder import ConflictBuilder
from solver import ConflictGraphSolver
from output_formatter import OutputFormatter
from ui import UserInterface


from materias import materias
from professores import professores
from salas import salas


def main():
    try:
        print("\n📚 Carregando dados...")

        disciplinas = DataProcessor.build_disciplinas(materias)
        salas_obj = DataProcessor.build_salas(salas)
        slots = DataProcessor.build_slots()

        professores_obj = DataProcessor.build_professores(professores, disciplinas)

        UserInterface.print_summary(
            len(disciplinas),
            len(professores_obj),
            len(salas_obj),
            len(slots)
        )

        print("🔍 Aplicando filtros...")
        semestres, periodos, cursos = UserInterface.prompt_filters()

        disciplinas_filtradas = DataProcessor.filter_disciplinas(
            disciplinas,
            semestres=semestres,
            periodos=periodos,
            cursos=cursos
        )

        if not disciplinas_filtradas:
            UserInterface.print_info(
                "Nenhuma disciplina encontrada para esse filtro.",
                level="error"
            )
            sys.exit(1)

        UserInterface.print_info(
            f"{len(disciplinas_filtradas)} disciplina(s) selecionada(s)",
            level="success"
        )

        print("\n📖 Dividindo disciplinas em partes...")
        disciplinas_partes = DataProcessor.split_disciplinas_em_partes(
            disciplinas_filtradas
        )

        UserInterface.print_info(
            f"{len(disciplinas_partes)} parte(s) de disciplinas para alocar",
            level="success"
        )

        print("\n🌐 Construindo grafo multilayer...")
        graph_builder = GraphBuilder()
        graph_builder.add_nodes(disciplinas_partes, professores_obj, salas_obj, slots)
        graph_builder.add_edges(disciplinas_partes, professores_obj, salas_obj, slots)

        graph = graph_builder.get_graph()
        UserInterface.print_info(
            f"Grafo com {graph.number_of_nodes()} nós e {graph.number_of_edges()} arestas",
            level="success"
        )
        OutputFormatter.generate_graph_pdf(graph, "graph_visualization.pdf")

        print("\n🎯 Gerando candidatos...")
        try:
            graph_builder.generate_candidates(disciplinas_partes)
        except ValueError as e:
            UserInterface.print_info(str(e), level="error")
            sys.exit(1)

        total_candidatos = sum(len(c) for c in graph_builder.candidatos_por_parte.values())
        UserInterface.print_info(
            f"{total_candidatos} candidatos gerados",
            level="success"
        )

        print("\n⚔️  Construindo grafo de conflitos...")
        conflict_builder = ConflictBuilder(graph, graph_builder.candidate_info)
        conflict_graph = conflict_builder.build(strict_mode=True)

        UserInterface.print_info(
            f"Grafo de conflitos com {conflict_graph.number_of_nodes()} nós "
            f"e {conflict_graph.number_of_edges()} arestas (conflitos)",
            level="success"
        )

        print("\n🔬 Resolvendo com backtracking + MRV (Otimizado)...")
        solver = ConflictGraphSolver(
            graph_builder.candidatos_por_parte,
            graph_builder.candidate_info,
            conflict_graph,
            graph_builder.get_graph()
        )

        found = solver.solve(verbose=True, time_limit=30)

        print("\n🚦 Iniciando processo de busca...")
        found = solver.solve(verbose=True)
        print("\n✅ Processo de busca concluído.")

        if not found:
            UserInterface.print_info(
                "Não foi possível encontrar uma alocação viável "
                "que satisfaça todas as restrições rígidas.",
                level="error"
            )
            sys.exit(1)

        print("\n📋 Decodificando solução...")
        resultado = solver.get_solution()
        print("\n📊 Gerando imagem do grafo da solução...")
        OutputFormatter.generate_solution_graph_image(resultado, "solution_graph.png")
        print("\n🖨️  Formatando resultados para saída...")

        if not resultado:
            UserInterface.print_info("Solução vazia", level="error")
            sys.exit(1)

        UserInterface.print_info(
            f"Solução encontrada: {len(resultado)} alocações",
            level="success"
        )
        print("\n📊 Exibindo resultados...")
        OutputFormatter.print_terminal(resultado, graph)
        print("\n📦 Gerando arquivo PDF com a solução...")

        OutputFormatter.generate_pdf(resultado, graph)
        UserInterface.print_info(
            "✨ Agendamento concluído com sucesso!",
            level="success"
        )
        print("\n✨ Agendamento concluído com sucesso!")

        OutputFormatter.generate_teacher_workload_pdf(resultado, graph)
        UserInterface.print_info(
            "✨ PDF de Carga Horária dos Professores gerado com sucesso!",
            level="success"
        )

    except Exception as e:
        UserInterface.print_info(f"Erro inesperado: {str(e)}", level="error")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()