import subprocess
import re
import sys
from concurrent.futures import ThreadPoolExecutor

AGENTES = {
    "count": ("othello_minimax_count", "Contagem de Peças"),
    "mask": ("othello_minimax_mask", "Valor Posicional"),
    "custom": ("othello_minimax_custom", "Heurística Customizada")
}

PARTIDAS = [
    ("count", "mask"), ("mask", "count"),
    ("count", "custom"), ("custom", "count"),
    ("mask", "custom"), ("custom", "mask")
]

def rodar_partida(args):
    idx, (b_key, w_key) = args
    b_file, b_name = AGENTES[b_key]
    w_file, w_name = AGENTES[w_key]
    
    # Criamos nomes de logs específicos para evitar conflitos de gravação concorrente
    cmd = [
        sys.executable, "server.py", "othello", 
        f"advsearch/your_agent/{b_file}.py", 
        f"advsearch/your_agent/{w_file}.py", 
        "-d", "5.0", "-p", "0",
        "-o", f"results_{idx}.xml", "-l", f"history_{idx}.txt"
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    out = res.stdout
    
    score_b = re.findall(r"Player 1.*?:\s*(\d+)", out)
    score_w = re.findall(r"Player 2.*?:\s*(\d+)", out)
    pts_b = score_b[0] if score_b else "?"
    pts_w = score_w[0] if score_w else "?"
    
    vencedor = b_name if int(pts_b) > int(pts_w) else (w_name if int(pts_w) > int(pts_b) else "Empate")
    
    # Limpa logs temporários individuais
    try:
        import os
        os.remove(f"results_{idx}.xml")
        os.remove(f"history_{idx}.txt")
    except:
        pass
        
    return f"| **{idx}** | {b_name} | {w_name} | {vencedor} | {pts_b} x {pts_w} |"

def main():
    print("Iniciando as 6 partidas concorrentemente. Aguarde...")
    
    with ThreadPoolExecutor() as executor:
        linhas = list(executor.map(rodar_partida, enumerate(PARTIDAS, 1)))
        
    print("RESULTADOS DO MINI-TORNEIO")
    print("*" * 50)
    print("| Partida | Agente Preto (B) | Agente Branco (W) | Vencedor | Placar Final (B x W) |")
    print("|:---:|:---|:---|:---:|:---:|")
    for linha in sorted(linhas):
        print(linha)

if __name__ == "__main__":
    main()
