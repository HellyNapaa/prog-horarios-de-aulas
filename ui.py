from typing import List, Optional, Tuple


class UserInterface:

    @staticmethod
    def prompt_filters() -> Tuple[Optional[List[int]],
                                   Optional[List[int]],
                                   Optional[List[str]]]:

        semestres: Optional[List[int]] = None
        periodos: Optional[List[int]] = None
        cursos: Optional[List[str]] = None

        print("\n Gerar carga horária de qual semestre? (1 ou 2)")
        escolha = input(" ➤ Digite: ").strip()

        if escolha == "1":
            semestres = [1]
        elif escolha == "2":
            semestres = [2]
        else:
            print(" Insira um semestre válido (1 ou 2).")
            return UserInterface.prompt_filters()  # pede de novo

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
