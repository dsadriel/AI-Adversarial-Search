import ctypes
import threading
from typing import Tuple, Callable
from .utils import TimeoutException

# default = 4.9
TIME_LIMIT = 4.9

def MIN(state, alpha, beta, depth, eval_func, player):
    if state.is_terminal() or depth == 0:
        return eval_func(state, player)
    val = float('inf')
    for legal_move in state.legal_moves():
        val = min(val, MAX(state.next_state(legal_move), alpha, beta, depth - 1 if depth > 0 else depth, eval_func, player))
        beta = min(beta, val)
        if beta <= alpha:
            break
    return val


def MAX(state, alpha, beta, depth, eval_func, player):
    if state.is_terminal() or depth == 0:
        return eval_func(state, player)
    val = float('-inf')
    for legal_move in state.legal_moves():
        val = max(val, MIN(state.next_state(legal_move), alpha, beta, depth - 1 if depth > 0 else depth, eval_func, player))
        alpha = max(alpha, val)
        if beta <= alpha:
            break
    return val


def minimax_move(state, max_depth: int, eval_func: Callable) -> Tuple[int, int]:
    """
    Returns a move computed by the minimax algorithm with alpha-beta pruning for the given game state.
    :param state: state to make the move (instance of GameState)
    :param max_depth: maximum depth of search (-1 = unlimited)
    :param eval_func: the function to evaluate a terminal or leaf state (when search is interrupted at max_depth).
                    This function should take a GameState object and a string identifying the player,
                    and should return a float value representing the utility of the state for the player.
    :return: (int, int) tuple with x, y coordinates of the move (remember: 0 is the first row/column)
    """
    best_action = None
    best_value = float('-inf')
    alpha = float('-inf')

    for legal_move in state.legal_moves():
        value = MIN(state.next_state(legal_move), alpha, float('inf'), max_depth - 1 if max_depth > 0 else max_depth, eval_func, state.player)
        if value > best_value:
            best_value = value
            best_action = legal_move
        alpha = max(alpha, best_value)
    return best_action


def iterative_deepening_minimax_move(state, eval_func: Callable) -> Tuple[int, int]:
    # Define uma função auxiliar que lança uma exceção assíncrona (TimeoutException)
    # em uma thread específica usando a API C do Python (ctypes).
    # Isso é usado para forçar a parada da busca iterativa quando o tempo limite é atingido.
    def _raise_exception_in_thread(thread_id):
        ctypes.pythonapi.PyThreadState_SetAsyncExc(
          ctypes.c_ulong(thread_id),
         ctypes.py_object(TimeoutException)
        )

    # Obtém o identificador da thread atual e cria um temporizador (timer).
    # Quando o tempo (TIME_LIMIT) esgotar, o temporizador chamará a função 
    # _raise_exception_in_thread para interromper a execução na thread principal.
    calling_thread_id = threading.current_thread().ident
    timer = threading.Timer(TIME_LIMIT, _raise_exception_in_thread, args=[calling_thread_id])

    best_move = None

    try:
        timer.start()
        for depth in range(1, 65):
            best_move = minimax_move(state, depth, eval_func)
    except TimeoutException:
        pass
    finally:
        timer.cancel()

    return best_move
