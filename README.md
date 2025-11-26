# Gerador de Horários Escolares - Abordagem via Teoria dos Grafos 🎓

Este projeto implementa uma solução para o **Problema de Cronograma Universitário (University Course Timetabling Problem - UCTP)** modelando-o como um Problema de Satisfação de Restrições (CSP) resolvido através de algoritmos em grafos.

## 🧠 Fundamentação Teórica (Grafos)

A solução baseia-se na redução do problema de alocação para o problema de encontrar um **Conjunto Independente** num Grafo de Conflitos.

1.  **Grafo de Candidatos ($G_{cand}$):**
    * Inicialmente, gera-se um grafo onde as arestas representam a viabilidade de conexão entre Entidades (Disciplina $\leftrightarrow$ Professor $\leftrightarrow$ Sala $\leftrightarrow$ Horário).
    * A partir deste, geram-se "Candidatos de Alocação" (tuplas únicas representando uma aula possível).

2.  **Grafo de Conflitos ($G_{conf} = (V, E)$):**
    * **Vértices ($V$):** Cada nó representa uma alocação candidata específica (ex: *Matéria X, Prof Y, Sala Z, Horário W*).
    * **Arestas ($E$):** Existe uma aresta $(u, v) \in E$ se, e somente se, a alocação $u$ entra em conflito com a alocação $v$.
    * **Conflitos mapeados:** Sobreposição de horários do mesmo professor, mesma sala ou mesma turma e professor com carga horária acima de 8 horas diárias.

3.  **Solução via Conjunto Independente:**
    * Uma grade horária válida corresponde a um **Conjunto Independente** de vértices em $G_{conf}$.
    * O objetivo é encontrar um subconjunto de vértices $S \subseteq V$ tal que, para quaisquer dois vértices $u, v \in S$, não exista aresta conectando-os, e $|S| = N$ (total de aulas necessárias).

## 🚀 Algoritmos Implementados

* **Construção de Grafo Multilayer:** Mapeamento de relacionamentos `networkx`.
* **Backtracking com Heurística MRV (Minimum Remaining Values):** O solver prioriza as disciplinas com menor número de candidatos disponíveis ("fail-first"), podando a árvore de busca rapidamente ao encontrar arestas no grafo de conflitos.
* **Otimização de "Gaps":** Função de custo quadrática para minimizar janelas entre aulas.

## 🛠️ Como Executar

1.  Instale as dependências necessárias:
    ```bash
    pip install networkx matplotlib reportlab
    ```

2.  Execute o ficheiro principal:
    ```bash
    python main.py
    ```

3.  Siga as instruções no terminal para selecionar o semestre (1 ou 2).
4.  Verifique os arquivos gerados na pasta: `grade_completa.pdf` e `solution_graph.png`.

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o ficheiro [LICENSE](LICENSE) para mais detalhes.

**Autor(a):** Hellen Napoleão, Caio Henrique, Quezia Adla e Vinicius Ferreira