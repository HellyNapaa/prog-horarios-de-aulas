from typing import List, Dict, Tuple
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import random

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

DIAS_ORDENADOS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]


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
                "dia": h_info["dia"],
                "hora": h_info["faixa"],
                "prof": p_info["nome"],
                "sala": s_info["nome"],
                "parte": d_info["parte"]
            }

            result_by_materia.setdefault(chave, []).append(entry)

        print("\n" + "=" * 60)
        print(" GRADE HORÁRIA GERADA")
        print("=" * 60)

        for mat_nome in sorted(result_by_materia.keys()):
            aulas = result_by_materia[mat_nome]
            print(f"\n>> {mat_nome}")
            for aula in sorted(aulas, key=lambda x: x["parte"]):
                print(f" Parte {aula['parte']}: {aula['dia']} - {aula['hora']}")
                print(f" Prof: {aula['prof']} | Sala: {aula['sala']}")

        print("\n" + "=" * 60 + "\n")

    @staticmethod
    def generate_pdf(
        resultado: List[Tuple],
        graph: nx.MultiGraph,
        filename: str = "grade_completa.pdf"
    ) -> None:

        print(f"\nGerando PDF: {filename}...")

        doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()

        # Título
        elements.append(Paragraph("Grade Horária (Timetable)", styles["Title"]))
        elements.append(Spacer(1, 20))

        # Estilos
        text_normal = ParagraphStyle("normal", fontSize=6, leading=7)
        text_bold = ParagraphStyle("bold", fontSize=7, leading=8, fontName="Helvetica-Bold")

        # Organizar timetable
        timetable: Dict[str, Dict[str, List[str]]] = {}

        for d_node, p_node, s_node, h_node in resultado:
            d = graph.nodes[d_node]
            p = graph.nodes[p_node]
            s = graph.nodes[s_node]
            h = graph.nodes[h_node]

            hora = h["faixa"]
            dia = h["dia"]

            timetable.setdefault(hora, {d: [] for d in DIAS_ORDENADOS})

            texto = (
                f"<b>{d['nome']}</b> ({d['sigla_real']})<br/>"
                f"Parte {d['parte']}<br/>"
                f"{p['nome']}<br/>"
                f"<font color='blue'>{s['nome']}</font>"
            )

            timetable[hora][dia].append(texto)

        horarios_ordenados = sorted(timetable.keys())

        # Criar tabela
        data = [["Horário"] + DIAS_ORDENADOS]

        for hora in horarios_ordenados:
            row = [Paragraph(f"<b>{hora}</b>", text_bold)]

            for dia in DIAS_ORDENADOS:
                aulas = timetable[hora][dia]
                if not aulas:
                    row.append("")
                else:
                    row.append(Paragraph("<br/><br/>".join(aulas), text_normal))

            data.append(row)

        col_widths = [70] + [150] * 5

        t = Table(data, colWidths=col_widths, repeatRows=1, splitByRow=1)

        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER")
        ]))

        elements.append(t)

        doc.build(elements)
        print(f"✓ PDF gerado com sucesso: {filename}")

    @staticmethod
    def generate_graph_pdf(graph: nx.MultiGraph, filename="graph_visualization.pdf"):

        print("\nGerando imagem e PDF do grafo...")

        # 1. Salvar imagem PNG
        img_path = "graph_temp_image.png"

        plt.figure(figsize=(20, 12))
        pos = nx.spring_layout(graph, k=0.3, iterations=50)

        nx.draw_networkx_nodes(graph, pos, node_size=500, node_color="lightblue")
        nx.draw_networkx_edges(graph, pos, width=1)
        nx.draw_networkx_labels(graph, pos, font_size=7)

        plt.axis("off")
        plt.savefig(img_path, dpi=200, bbox_inches="tight")
        plt.close()

        # 2. Criar PDF com redimensionamento automático
        doc = SimpleDocTemplate(filename, pagesize=landscape(A4))
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Visualização do Grafo", styles["Title"]))
        elements.append(Spacer(1, 20))

        # Tamanho máximo dentro da página
        max_width = 750
        max_height = 430

        from reportlab.platypus import Image
        img = Image(img_path)

        # Reduzir automaticamente a imagem se necessário
        if img.drawWidth > max_width:
            scale = max_width / img.drawWidth
            img.drawWidth = max_width
            img.drawHeight *= scale

        if img.drawHeight > max_height:
            scale = max_height / img.drawHeight
            img.drawHeight = max_height
            img.drawWidth *= scale

        elements.append(img)

        doc.build(elements)

        print(f"✓ PDF do grafo gerado com sucesso: {filename}")



    def generate_solution_graph_image(solution: List[Tuple], filename: str) -> None:
        plt.figure(figsize=(12, 8))
        G = nx.Graph()
        for d_node, p_node, s_node, h_node in solution:
            G.add_node(d_node)
            G.add_node(p_node)
            G.add_node(s_node)
            G.add_node(h_node)
            G.add_edge(d_node, p_node)
            G.add_edge(d_node, s_node)
            G.add_edge(d_node, h_node)
        pos = nx.spring_layout(G, k=0.15, iterations=20)
        nx.draw(G, pos, with_labels=True, node_size=300, font_size=6)
        plt.savefig(filename, dpi=200)
        plt.close()
        print(f"✓ Imagem do grafo da solução salva como: {filename}")

