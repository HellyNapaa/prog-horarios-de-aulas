from typing import List, Dict, Set, Tuple
from models import Disciplina, Professor, Sala, Slot, DisciplinaParte
from config import SEMANA, HORARIOS, SLOTS_VALIDOS, HORARIOS_NOTURNOS


class DataProcessor:
    @staticmethod
    def build_disciplinas(raw_materias: List[Dict]) -> List[Disciplina]:
        disciplinas = []
        for i, materia in enumerate(raw_materias):
            if materia.get('ch', 0) <= 0:
                continue
            tipo = 'optativa' if str(materia.get('curso', '')).strip().lower() == 'optativa' else 'obrigatoria'
            disc = Disciplina(
                id=f"{materia['sigla']}_{i}",
                sigla_real=materia['sigla'],
                nome=materia['nome'],
                tipo=tipo,
                carga=materia['ch'],
                curso=materia['curso'],
                periodo=materia.get('periodo'),
                semestre=materia.get('semestre'),
                prof_responsavel=materia.get('prof_responsavel', '')
            )
            disciplinas.append(disc)
        return disciplinas

    @staticmethod
    def build_professores(raw_professores: Dict[str, str], 
                         disciplinas: List[Disciplina]) -> List[Professor]:
        prof_aptas: Dict[str, List[str]] = {}
        for disc in disciplinas:
            if not disc.prof_responsavel:
                continue
            profs = [p.strip() for p in str(disc.prof_responsavel).split(',')]
            for prof_id in profs:
                if prof_id not in prof_aptas:
                    prof_aptas[prof_id] = []
                prof_aptas[prof_id].append(disc.id)
        professores = []
        for prof_id, nome in raw_professores.items():
            prof = Professor(
                id=prof_id,
                nome=nome,
                disciplinas_aptas=prof_aptas.get(prof_id, [])
            )
            professores.append(prof)
        return professores

    @staticmethod
    def build_salas(raw_salas: Dict[str, str]) -> List[Sala]:
        return [Sala(id=sid, nome=nome) for sid, nome in raw_salas.items()]

    @staticmethod
    def build_slots() -> List[Slot]:
        slots = []
        for dia_num, dia_nome in SEMANA.items():
            for hora_id in SLOTS_VALIDOS:
                slot = Slot(
                    id=f"{dia_num}_{hora_id}",
                    dia=dia_nome,
                    hora_id=hora_id,
                    faixa=HORARIOS[hora_id]
                )
                slots.append(slot)
        
        return slots

    @staticmethod
    def filter_disciplinas(disciplinas: List[Disciplina],
                          semestres: List[int] = None,
                          periodos: List[int] = None,
                          cursos: List[str] = None) -> List[Disciplina]:
        filtradas = []
        for disc in disciplinas:
            if semestres is not None and disc.semestre not in semestres:
                continue
            if periodos is not None and disc.periodo not in periodos:
                continue
            if cursos is not None:
                curso_disc = str(disc.curso).strip().upper()
                eh_do_curso = curso_disc in cursos
                eh_optativa = disc.tipo == 'optativa'
                if not (eh_do_curso or eh_optativa):
                    continue
            filtradas.append(disc)
        return filtradas

    @staticmethod
    def split_disciplinas_em_partes(disciplinas: List[Disciplina]) -> List[DisciplinaParte]:
        partes = []
        for disc in disciplinas:
            if disc.carga >= 4:
                num_partes = disc.carga // 2
                for parte_idx in range(num_partes):
                    parte = DisciplinaParte(
                        sub_id=f"{disc.id}_p{parte_idx + 1}",
                        parte=parte_idx + 1,
                        carga=2,
                        disciplina_base=disc
                    )
                    partes.append(parte)
            else:
                parte = DisciplinaParte(
                    sub_id=f"{disc.id}_p1",
                    parte=1,
                    carga=disc.carga,
                    disciplina_base=disc
                )
                partes.append(parte)
        return partes