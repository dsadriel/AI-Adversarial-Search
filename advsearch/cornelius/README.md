<!--

> Usar https://dillinger.io para salvar em PDF

O relatório deve conter:
○ Nomes, cartões de matrícula e turma dos integrantes do grupo;

○ Bibliotecas que precisem ser instaladas para executar sua implementação;

○ Resultado da sua avaliação da poda alfa-beta no tic-tac-toe misere (ver item “a” seção
2.3);

○ Para o Othello:
  ■ Explique a heurística customizada e, caso tenha sido utilizada alguma fonte (como artigo ou site), indique a fonte também, explicando como as fontes foram utilizadas (a heurística foi utilizada conforme apresentada na fonte, foi uma combinação de ideias de fontes diferentes, foi totalmente projetada pelo grupo, sem utilização de fontes,...);
  ■ descrição do critério de parada do agente (profundidade máxima fixa? aprofundamento iterativo parado por tempo?etc);

  ■ Resultado da avaliação (ver item “b” da seção 2.3);
  ■ Explique a implementação escolhida para o torneio.
  ■ Extras: Relate qualquer item opcional (como implementação do MCTS) ou melhoria não mencionada (técnicas adicionais para melhorar o minimax não vistas em aula) que você tenha realizado e, caso tenha utilizado fontes extras para auxiliar, mencione as fontes e como foram utilizadas.
  ■ Utilização de chatbots ou agentes de IA: Façam uma declaração explícita sobre o uso de qualquer chatbot ou agente de IA baseado em LLMs (como ChatGPT, Claude, Gemini, Copilot, etc). Caso o grupo não tenha utilizado, apenas informe isso explicitamente. Caso o grupo tenha utilizado de alguma forma, relate como foi utilizado (atenção para os usos não permitidos discutidos a seguir).

Observação: É encorajado que os grupos consultem outras fontes, se quiserem e não há nenhum problema caso técnicas eu heurísticas sejam utilizadas tais como estão nas fontes. ChatGPT também vale (desde que seja uma conversa para ajudar a projetar a heurística)

-->

# Relatório de Implementação - Busca com Adversário

## Integrantes do Grupo
* Adriel de Souza (00579100)
* Arthur Chagas Bridi (00585225)
* Rafael Stephanou (00590367)


## a) Avaliação do Minimax no Tic-Tac-Toe Misere

### (i) O minimax sempre ganha ou empata jogando contra o `randomplayer`?
> **Sim.** Por se tratar de um jogo com fator de ramificação pequeno e profundidade máxima de 9 turnos, a árvore de busca é pequena o suficiente para ser totalmente resolvida pelo minimax. O minimax perfeito joga de forma ótima e nunca perde para um jogador aleatório.
### (ii) O minimax sempre empata jogando contra si mesmo?
> **Sim.** Como o jogo tem empate como resultado de jogo perfeito a partir do estado inicial, dois agentes perfeitos minimax jogando um contra o outro resultarão sempre em empate.
### (iii) O minimax não perde para você quando você usa a sua melhor estratégia?
> **Sim.** Como a busca é ilimitada (profundidade máxima) e o minimax é perfeito, é matematicamente impossível para um jogador humano vencer o agente. O melhor resultado que um humano consegue obter é o empate.

---

## b) Avaliação do Minimax no Othello

### Heurística Customizada e Fases de Jogo
Nossa heurística customizada baseia-se na no artigo ["An Analysis of Heuristics in Othello"](https://www.scribd.com/document/353439817/An-Analysis-of-Heuristics-in-Othello). Ela calcula uma combinação linear normalizada de quatro fatores:

1. **Coin Parity (Paridade de Peças):** A diferença percentual entre a quantidade de peças do jogador e do oponente.
2. **Mobility (Mobilidade):** A facilidade de movimentação (diferença no número de lances legais disponíveis). Tenta encurralar o adversário.
3. **Corners (Cantos):** Prioridade absoluta para a captura de quinas (posições estáveis que nunca mudam de dono) e penalização de posições adjacentes a cantos vazios.
4. **Stability (Estabilidade):** Avaliação de quais peças já estão seguras (estáveis) versus peças flanqueáveis (instáveis).

Os pesos dessas sub-heurísticas variam dinamicamente dependendo da fase do jogo:
* **Early Game (menos de 20 peças):** Foco em mobilidade para restringir o oponente e preparação para quinas. `W_CORNERS = 3`, `W_STABILITY = 1`, `W_MOBILITY = 5`, `W_COUNT = 0`.
* **Mid Game (entre 20 e 50 peças):** Transição estratégica focada em estabilidade e cantos. `W_CORNERS = 5`, `W_STABILITY = 5`, `W_MOBILITY = 1`, `W_COUNT = 0`.
* **Late Game (mais de 50 peças):** Foco absoluto na contagem de peças para garantir a pontuação máxima de vitória. `W_CORNERS = 5`, `W_STABILITY = 3`, `W_MOBILITY = 1`, `W_COUNT = 5`.

#### Origem e Sintonia dos Pesos:
Os pesos acima não foram importados de fórmulas prontas de literatura. Eles são frutos de um refinamento empírico manual realizado pelo grupo:
- **Ajuste de Mobilidade:** Testamos a influência da mobilidade variando de 3x, 5x e 10x menos peso em relação às quinas. Descobrimos que um peso de mobilidade alto no início (`5`) e baixo nas fases posteriores (`1`) era essencial para manter a busca profunda sem perder a capacidade de encurralar o adversário.
- **Divisão por Fases:** Introduzimos a ativação dinâmica do `W_COUNT` (paridade de moedas) apenas no final do jogo (`Late Game`), mantendo-o nulo nas fases iniciais. Isso evitou que o agente capturasse muitas peças prematuramente no início e ficasse sem opções de movimentos válidos no meio de jogo.
- **Validação:** Rodamos simulações locais comparando variações de pesos candidatas da literatura, mas a calibração manual desenvolvida pelo grupo provou-se a mais consistente e com a maior taxa de peças nos testes locais contra os agentes `count` e `mask`.



### Critério de Parada
O agente utiliza **Busca por Aprofundamento Iterativo (Iterative Deepening)**. Ele realiza buscas completas de profundidade incremental (iniciando em 1) e utiliza um controle de tempo. Se a busca estourar o limite interno de **4,9 segundos** (a fim de respeitar os 5 segundos máximos do torneio de forma segura), uma exceção `TimeoutException` é levantada, interrompendo o ciclo e retornando o melhor movimento encontrado na iteração completa anterior.
---

## Resultados do Mini-Torneio de Othello

Abaixo está a tabela de resultados do torneio interno entre os três agentes (`Count`, `Mask` e `Custom`):

| Partida | Agente Preto (B) | Agente Branco (W) | Vencedor | Placar Final (B x W) |
|:---:|:---|:---|:---:|:---:|
| **1** | Contagem de Peças | Valor Posicional | Valor Posicional | 23 x 41 |
| **2** | Valor Posicional | Contagem de Peças | Valor Posicional | 37 x 27 |
| **3** | Contagem de Peças | Heurística Customizada | Heurística Customizada | 7 x 57 |
| **4** | Heurística Customizada | Contagem de Peças | Heurística Customizada | 51 x 13 |
| **5** | Valor Posicional | Heurística Customizada | Heurística Customizada | 22 x 42 |
| **6** | Heurística Customizada | Valor Posicional | Heurística Customizada | 33 x 31 |

**Agente Mais Bem-Sucedido:** **Heurística Customizada** (4 vitórias, 183 peças capturadas no total).
> Os agentes possuem comportamento não-determinístico devido ao aprofundamento iterativo limitado por tempo, mas a Heurística Customizada mostrou-se consistentemente superior aos agentes `Count` e `Mask` em todas as partidas.
---

## Implementação do Agente de Torneio
A nossa estratégia escolhida para o torneio oficial utiliza o algoritmo Minimax com Poda Alfa-Beta, usando a **Heurística Customizada** parametrizada por fase de jogo com aprofundamento iterativo por tempo (timeout seguro em 4.7s). Essa configuração se provou superior tanto na facilidade de capturar cantos quanto na consistência em encurralar os oponentes através do cálculo de mobilidade.

---

## Declaração de Uso de IA (LLMs)
Durante o desenvolvimento do projeto, foram utilizadas IAs generativas como ferramenta de apoio, principalmente como meio de realizar brainstorming, tirar dúvidas conceituais, auxiliar no debug de códigos e polir a escrita do relatório. Todas as funções criadas foram desenvolvidas e validadas pelos membros do grupo.