from typing import List, Dict, Tuple
import networkx as nx
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class OutputFormatter:

    @staticmethod
    def print_terminal(resultado: List[Tuple], graph: nx.MultiGraph) -> None:

        result_by_materia: Dict[str, List[Dict]] = {}

        for d_node, p_node, s_node, h_node in resultado:
            d_info = graph.nodes[d_node]
            p_info = graph.nodes[p_node]
            s_info = graph.nodes[s_node]
            h_info = graph.nodes[h_node]

            chave = f"{d_info['nome']} ({d_info['sigla_real']})"
            entry = {
                "dia": h_info['dia'],
                "hora": h_info['faixa'],
                "prof": p_info['nome'],
                "sala": s_info['nome'],
                "parte": d_info['parte']
            }

            if chave not in result_by_materia:
                result_by_materia[chave] = []
            result_by_materia[chave].append(entry)

        print("\n" + "=" * 60)
        print("           GRADE HORÁRIA GERADA")
        print("=" * 60)

        for mat_nome in sorted(result_by_materia.keys()):
            aulas = result_by_materia[mat_nome]
            print(f"\n>> {mat_nome}")

            for aula in sorted(aulas, key=lambda x: x['parte']):
                print(f"   Parte {aula['parte']}: {aula['dia']} - {aula['hora']}")
                print(f"           Prof: {aula['prof']} | Sala: {aula['sala']}")

        print("\n" + "=" * 60 + "\n")

    @staticmethod
    def generate_pdf(resultado: List[Tuple], 
                    graph: nx.MultiGraph,
                    filename: str = "grade_completa.pdf") -> None:

        print(f"\nGerando PDF: {filename}...")

        doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Grade Horária Gerada", styles['Title']))
        elements.append(Spacer(1, 20))

        def sort_key(res):
            d_node = graph.nodes[res[0]]
            return (
                str(d_node.get('curso', '')),
                d_node.get('periodo') or 99,
                d_node.get('nome', '')
            )

        resultado_ordenado = sorted(resultado, key=sort_key)

        style_cell_normal = ParagraphStyle(
            'cell_normal',
            parent=styles['Normal'],
            fontSize=8,
            leading=10
        )
        style_cell_bold = ParagraphStyle(
            'cell_bold',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            fontName='Helvetica-Bold'
        )

        data = [[
            'Disciplina',
            'Detalhes\n(Curso | Período | Sem | Tipo)',
            'Parte',
            'Dia / Hora',
            'Professor / Sala'
        ]]

        for d_node, p_node, s_node, h_node in resultado_ordenado:
            d_info = graph.nodes[d_node]
            p_info = graph.nodes[p_node]
            s_info = graph.nodes[s_node]
            h_info = graph.nodes[h_node]

            texto_disciplina = (
                f"{d_info['nome']}<br/>"
                f"<b>({d_info['sigla_real']})</b>"
            )

            periodo = d_info.get('periodo') or "-"
            texto_detalhes = (
                f"<b>Curso:</b> {d_info['curso']}<br/>"
                f"<b>Per:</b> {periodo}º | "
                f"<b>Sem:</b> {d_info['semestre']}<br/>"
                f"<i>{d_info['tipo'].capitalize()}</i>"
            )

            texto_parte = str(d_info['parte'])

            texto_hora = (
                f"<b>{h_info['dia']}</b><br/>"
                f"{h_info['faixa']}"
            )

            texto_prof = (
                f"{p_info['nome']}<br/>"
                f"<font color='blue'>{s_info['nome']}</font>"
            )
            row = [
                Paragraph(texto_disciplina, style_cell_bold),
                Paragraph(texto_detalhes, style_cell_normal),
                texto_parte,
                Paragraph(texto_hora, style_cell_normal),
                Paragraph(texto_prof, style_cell_normal)
            ]
            data.append(row)
        col_widths = [200, 140, 40, 120, 250]
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ]))
        elements.append(t)
        doc.build(elements)
        print(f"✓ PDF gerado com sucesso: {filename}\n")