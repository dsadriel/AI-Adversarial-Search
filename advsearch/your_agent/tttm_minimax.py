import random
from typing import Tuple
from ..tttm.gamestate import GameState
from ..tttm.board import Board
from .minimax import minimax_move

# Voce pode criar funcoes auxiliares neste arquivo
# e tambem modulos auxiliares neste pacote.
#
# Nao esqueca de renomear 'your_agent' com o nome
# do seu agente.


def make_move(state: GameState) -> Tuple[int, int]:
    """
    Retorna uma jogada calculada pelo algoritmo minimax para o estado de jogo fornecido.
    :param state: estado para fazer a jogada
    :return: tupla (int, int) com as coordenadas x, y da jogada (lembre-se: 0 é a primeira linha/coluna)
    """
    
    return minimax_move(state, float('inf'), utility)

def utility(state, player:str) -> float:
    """
    Retorna a utilidade de um estado (terminal) 
    """
    winner = state.winner()
    if winner == player:
        return 1.0
    elif winner is None:
        return 0.0
    else:
        return -1.0
