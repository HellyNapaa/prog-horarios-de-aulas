from typing import Dict, List

SEMANA: Dict[int, str] = {
    2: 'Segunda',
    3: 'Terça',
    4: 'Quarta',
    5: 'Quinta',
    6: 'Sexta'
}


HORARIOS: Dict[int, str] = {
    0: "7h00 - 7h55",
    1: "7h55 - 9h45",
    2: "10h10 - 12h00",
    3: "13h30 - 15h20",
    4: "15h45 - 17h35",
    5: "19h00 - 20h40",
    6: "21h00 - 22h40",
    7: "22h40 - 23h30"
}


HORARIOS_NOTURNOS: List[int] = [5, 6, 7]


SLOTS_VALIDOS: List[int] = [i for i in HORARIOS.keys() if i not in [0, 8]]

PDF_FILENAME: str = "grade_completa.pdf"
LOG_STEP: int = 10000