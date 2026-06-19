import random
import time
from .utils import TimeoutException
from typing import Tuple, Callable

TIME_LIMIT = 4.7

def MIN(state, alpha, beta, depth, start, eval_func, player):
    if time.time() - start > TIME_LIMIT: 
        raise TimeoutException()

    if (state.is_terminal() or depth == 0):
        return eval_func(state, player)
    val = float('inf')
    for legal_move in sorted(state.legal_moves()):
        val = min(val, MAX(state.next_state(legal_move), alpha, beta, depth - 1, start, eval_func, player))
        beta = min(beta, val)
        if beta <= alpha:
            break
    return val

    
def MAX(state, alpha, beta, depth, start, eval_func, player):
    if time.time() - start > TIME_LIMIT:
        raise TimeoutException()

    if (state.is_terminal() or depth == 0):
        return eval_func(state, player)
    val = float('-inf')
    for legal_move in sorted(state.legal_moves()):
        val = max(val, MIN(state.next_state(legal_move), alpha, beta, depth - 1, start, eval_func, player))
        alpha = max(alpha, val)
        if beta <= alpha:
            break
    return val


def minimax_move(state, max_depth:int, start, eval_func:Callable) -> Tuple[int, int]:
    """
    Returns a move computed by the minimax algorithm with alpha-beta pruning for the given game state.
    :param state: state to make the move (instance of GameState)
    :param max_depth: maximum depth of search (-1 = unlimited)
    :param eval_func: the function to evaluate a terminal or leaf state (when search is interrupted at max_depth)
                    This function should take a GameState object and a string identifying the player,
                    and should return a float value representing the utility of the state for the player.
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """
    bestAction = None
    bestValue = float('-inf')

    for legal_move in sorted(state.legal_moves()):
        value = MIN(state.next_state(legal_move), float('-inf'), float('inf'), max_depth - 1, start, eval_func, state.player)
        if value > bestValue:
            bestValue = value
            bestAction = legal_move
    return bestAction





