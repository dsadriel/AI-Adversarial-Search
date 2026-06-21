class TimeoutException(Exception):
    """Exceção customizada para interromper a busca do Minimax por limite de tempo."""
    pass


def normalize(player_value: float, opponent_value: float) -> float:
    total = player_value + opponent_value
    if total != 0:
        return 100 * (player_value - opponent_value) / total
    return 0