import random
from typing import Tuple
from ..othello.gamestate import GameState
from ..othello.board import Board
from .minimax import minimax_move
import time
from .utils import TimeoutException
from .utils import normalize
# Voce pode criar funcoes auxiliares neste arquivo
# e tambem modulos auxiliares neste pacote.
#
# Nao esqueca de renomear 'your_agent' com o nome
# do seu agente.

CORNERS = [(0, 0), (0, 7), (7, 0), (7, 7)]



W_CAPTURED = 1.0
W_POTENTIAL = 0.5
W_UNLIKELY = 0.5


def make_move(state) -> Tuple[int, int]:
    """
    Returns a move for the given game state
    :param state: state to make the move
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """

    start = time.time()

    for depth in range (1, 65):
        try:
            move = minimax_move(state, depth, start, evaluate_custom)
        
        except TimeoutException:
            break

    return move 



def evaluate_custom(state, player:str) -> float:
    """
    Evaluates an othello state from the point of view of the given player. 
    If the state is terminal, returns its utility. 
    If non-terminal, returns an estimate of its value based on your custom heuristic
    :param state: state to evaluate (instance of GameState)
    :param player: player to evaluate the state for (B or W)
    """
    # heuristic_value = corners * x1 + stability * x2 + mobility * x3
    heuristic_value = corners_heuristic(state, player)

    return heuristic_value


def corners_heuristic(state, player:str) -> float:
    return (
        W_CAPTURED * evaluate_corners_captured(state, player)
        + W_POTENTIAL * evaluate_potential_corners(state, player)
        + W_UNLIKELY * evaluate_unlikely_corners(state, player)
    )


def evaluate_corners_captured(state, player:str) -> float:
    player_corner_value = 0
    opponent_corner_value = 0
    opponent = Board.opponent(player)

    for corner in CORNERS:
        if state.board.tiles[corner[0]][corner[1]] == player:
            player_corner_value += 1
        elif state.board.tiles[corner[0]][corner[1]] == opponent:
            opponent_corner_value += 1

    return normalize(player_corner_value, opponent_corner_value)


def evaluate_potential_corners(state, player:str) -> float:
    opponent = Board.opponent(player)
    player_moves = state.board.legal_moves(player)
    opponent_moves = state.board.legal_moves(opponent)

    # Qtd de cantos vazios que o jogador pode chegar em 1 lance
    player_potential = 0
    opponent_potential = 0

    for corner in CORNERS:
        if state.board.tiles[corner[0]][corner[1]] != Board.EMPTY:
            continue  
        in_player = corner in player_moves
        in_opponent = corner in opponent_moves
        # excluimos potential corners simetricos para nao diluir o valor na normalizacao 
        if in_player and not in_opponent:
            player_potential += 1
        elif in_opponent and not in_player:
            opponent_potential += 1

    return normalize(player_potential, opponent_potential)


def evaluate_unlikely_corners(state, player:str) -> float:

    """Penaliza pecas coladas a um canto vazio"""
    opponent = Board.opponent(player)

    player_adjacent = 0    
    opponent_adjacent = 0  

    for cx, cy in CORNERS:
        if state.board.tiles[cx][cy] != Board.EMPTY:
            continue
        for dx, dy in Board.DIRECTIONS:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < 8 and 0 <= ny < 8:
                neighbor = state.board.tiles[nx][ny]
                if neighbor == player:
                    player_adjacent += 1
                elif neighbor == opponent:
                    opponent_adjacent += 1

   
    return normalize(opponent_adjacent, player_adjacent)