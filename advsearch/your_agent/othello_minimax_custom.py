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

MID = 20

LATE = 50

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
    game_phase = evaluate_game_phase(state)
    if game_phase == "early":
        W_CORNERS = 3
        W_STABILITY = 1
        W_MOBILITY = 5
        W_COUNT = 0

    elif game_phase == "mid":
        W_CORNERS = 5
        W_STABILITY = 5
        W_MOBILITY = 1
        W_COUNT = 0
    else: 
        W_CORNERS = 5
        W_STABILITY = 3
        W_MOBILITY = 1
        W_COUNT = 5


    heuristic_value = (
        W_CORNERS * corners_heuristic(state, player) + 
        W_STABILITY * stability_heuristic(state, player) + 
        W_MOBILITY * mobility_heuristic(state, player) + 
        W_COUNT * evaluate_count(state, player))
        
    return heuristic_value


def evaluate_game_phase(state) -> str:
    total_pieces = 64 - state.board.num_pieces(Board.EMPTY)
    if total_pieces < MID:
        return "early"
    elif total_pieces < LATE:
        return "mid"
    else:
        return "late"


def mobility_heuristic(state, player:str) -> float:
    opponent = Board.opponent(player)
    num_player_moves = len(state.board.legal_moves(player))
    num_opponent_moves = len(state.board.legal_moves(opponent))

    return normalize(num_player_moves, num_opponent_moves)

def corners_heuristic(state, player:str) -> float:
    W_CAPTURED = 1.0
    W_POTENTIAL = 0.4
    W_UNLIKELY = 1.0

    capt_player, capt_opponent = evaluate_corners_captured(state, player)
    pot_player, pot_opponent = evaluate_potential_corners(state, player)
    unl_player, unl_opponent = evaluate_unlikely_corners(state, player)

    total_player = (
        (W_CAPTURED * capt_player) + 
        (W_POTENTIAL * pot_player) + 
        (W_UNLIKELY * unl_opponent)
    )

    total_opponent = (
        (W_CAPTURED * capt_opponent) + 
        (W_POTENTIAL * pot_opponent) + 
        (W_UNLIKELY * unl_player)
    )

    return normalize(total_player, total_opponent)


        
def evaluate_corners_captured(state, player:str) -> tuple:
    player_corner_value = 0
    opponent_corner_value = 0
    opponent = Board.opponent(player)

    for corner in CORNERS:
        if state.board.tiles[corner[0]][corner[1]] == player:
            player_corner_value += 1
        elif state.board.tiles[corner[0]][corner[1]] == opponent:
            opponent_corner_value += 1

    return (player_corner_value, opponent_corner_value)



def evaluate_potential_corners(state, player:str) -> tuple:
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

    return (player_potential, opponent_potential)



def evaluate_unlikely_corners(state, player:str) -> tuple:

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

   
    return (player_adjacent, opponent_adjacent)



#métodos da Heuristica de estabilidade
W_STABILITY = 1.0
W_INSTABILITY = 1.0

def stability_heuristic(state, player:str) -> float:
    (player_stability, opponent_stability), (player_instability, opponent_instability) = evaluate_stability(state, player)

    total_player = (
        W_STABILITY * player_stability +
        W_INSTABILITY * opponent_instability
    )

    total_opponent = (
        W_STABILITY * opponent_stability +
        W_INSTABILITY * player_instability
    )

    return normalize(total_player, total_opponent)

def evaluate_stability(state, player:str) -> tuple: 
    player_instability = 0
    player_stability = 0

    opponent_instability = 0
    opponent_stability = 0
    #num_movements = 0

    opponent = Board.opponent(player)

    for lin in range(8):
        for col in range(8):
            tile = state.board.tiles[lin][col]
            tile_position = (lin, col)

            if tile == player: #verifica se eh flanqueavel
                result_player = is_unstable(state, player, tile_position)

                if result_player == 0: #se nao for, verifica se eh estavel
                    player_stability += is_stable(state, player, tile_position)
                else:
                    player_instability += 1


            elif tile == opponent:
                result_opp = is_unstable(state, opponent, tile_position)

                if result_opp == 0:
                    opponent_stability += is_stable(state, opponent, tile_position)
                else:
                    opponent_instability += 1
    
    return ((player_stability, opponent_stability),(player_instability, opponent_instability))



def is_unstable(state, player:str, tile_position:tuple) -> bool: 
    """verifica se peça é capturavel
    proximo passo: devolver lista de peças flanqueaveis para economizar nos loops
    no momento retorna verdadeiro ou falso para aquela peça
    """
    opponent = Board.opponent(player)

    directions_pairs = [(0,1), (2,3), (4,7), (5,6)] #emparelha corretamente as directions opostas de board.py para usarmos em duplas

    for dir1_index, dir2_index in directions_pairs:
        dir1_found_opponent = False
        dir1_found_blank = False

        dir1_found_opponent, dir1_found_blank = found_opponent_or_blank(Board.DIRECTIONS[dir1_index], tile_position, state, player, opponent)

        #só vai em frente se achou um ou outro. Se nenhum encontrado, a peça não é capturavel no eixo proposto
        if (dir1_found_opponent or dir1_found_blank):
            dir2_found_opponent, dir2_found_blank = found_opponent_or_blank(Board.DIRECTIONS[dir2_index], tile_position, state, player, opponent)

            found_opponent = dir1_found_opponent or dir2_found_opponent
            found_blank = dir1_found_blank or dir2_found_blank

            if found_opponent and found_blank:
                return True
    
    return False
        

"""
Percorre a partir da posiçao do tile na direçao imposta até parar de encontrar peças do seu tipo
Se após percorrer lista de suas peças, encontrou peça do oponente, retorna (1,0)
Se após percorrer lista de suas peças, encontrou espaço vazio, retorna (0,1)
"""
def found_opponent_or_blank(direction, tile_position, state, player, opponent) -> tuple:
    dx, dy = direction
    tx, ty = tile_position

    tx += dx
    ty += dy

    if not (0 <= tx <= 7 and 0 <= ty <= 7):
        return (False, False)
    
    while state.board.tiles[tx][ty] == player:
        tx += dx
        ty += dy
        if not (0 <= tx <= 7 and 0 <= ty <= 7):  
            return (False, False)

    if state.board.tiles[tx][ty] == opponent:
        return (True, False)
    
    elif state.board.tiles[tx][ty] == Board.EMPTY:
        return (False, True)


def is_stable(state, player:str, tile_position:tuple) -> bool:
    if tile_position in CORNERS:
       return True
    
    return False
    

def evaluate_count(state, player:str) -> float:
    opponent = Board.opponent(player)
    
    player_pieces = state.board.num_pieces(player)
    opponent_pieces = state.board.num_pieces(opponent)
    
    return normalize(player_pieces, opponent_pieces)

    

        

