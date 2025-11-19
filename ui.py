from typing import List, Optional, Tuple


class UserInterface:


    @staticmethod
    def prompt_filters() -> Tuple[Optional[List[int]],
                                   Optional[List[int]],
                                   Optional[List[str]]]:

        semestres: Optional[List[int]] = None
        periodos: Optional[List[int]] = None
        cursos: Optional[List[str]] = None

        print("\n" + "=" * 60)
        print("         CONFIGURAÇÃO DE FILTRO")
        print("=" * 60)

        print("\n[1/3] Filtrar por SEMESTRE? (s/n)")
        if input().strip().lower() == 's':
            print("    Qual semestre? (1, 2 ou ambos separados por vírgula)")
            try:
                semestres = [int(s.strip()) for s in input().strip().split(",")]
                print(f"    ✓ Semestres selecionados: {semestres}")
            except ValueError:
                print("    ✗ Entrada inválida. Ignorando filtro de semestre.")
                semestres = None

        print("\n[2/3] Filtrar por PERÍODO? (s/n)")
        if input().strip().lower() == 's':
            print("    Qual período? (ex: 1,2 ou 5 para só o quinto)")
            try:
                periodos = [int(p.strip()) for p in input().strip().split(",")]
                print(f"    ✓ Períodos selecionados: {periodos}")
            except ValueError:
                print("    ✗ Entrada inválida. Ignorando filtro de período.")
                periodos = None

        print("\n[3/3] Filtrar por CURSO? (s/n)")
        if input().strip().lower() == 's':
            print("    Qual curso? (ex: CCO ou SIN; vários: CCO,SIN)")
            try:
                cursos = [c.strip().upper() for c in input().strip().split(",")]
                print(f"    ✓ Cursos selecionados: {cursos}")
            except ValueError:
                print("    ✗ Entrada inválida. Ignorando filtro de curso.")
                cursos = None
        print()
        return semestres, periodos, cursos

    @staticmethod
    def print_info(message: str, level: str = "info") -> None:
        symbols = {
            "info": "ℹ",
            "warning": "⚠",
            "error": "✗",
            "success": "✓"
        }
        symbol = symbols.get(level, "•")
        print(f"{symbol} {message}")

    @staticmethod
    def print_summary(num_disciplinas: int,
                     num_professores: int,
                     num_salas: int,
                     num_slots: int) -> None:
        print("\n" + "=" * 60)
        print("         SUMÁRIO DE DADOS CARREGADOS")
        print("=" * 60)
        print(f"Disciplinas: {num_disciplinas}")
        print(f"Professores: {num_professores}")
        print(f"Salas:       {num_salas}")
        print(f"Slots:       {num_slots}")
        print("=" * 60 + "\n")