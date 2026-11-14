import random
import math
import time
import sys
import os
import glob
sys.setrecursionlimit(5000)

# ====== SIMULATED ANNEALING =====
# decisão de projeto: cidade inicial eh 1
# rotas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] sera a representacao

def calcula_custo(rota, matriz):
    custo_total = 0

    for i in range(len(rota)):
        cidade = rota[i]
        if i < len(rota) - 1:
            cidade_adjacente = rota[i + 1]
        else:
            cidade_adjacente = rota[0]

        if matriz[cidade - 1][cidade_adjacente - 1] > 0:
            custo_total += matriz[cidade - 1][cidade_adjacente - 1]
        else:
            return float('inf')

    return custo_total

def gerar_vizinhos(rota, matriz):
    nova_rota = rota.copy()

    for i in range(100):
        elemento1 = random.randint(1,len(rota) - 1)            # sorteia as posicoes a serem trocadas
        elemento2 = random.randint(1,len(rota) - 1)

        while elemento1 == elemento2:
            elemento2 = random.randint(1, len(rota) - 1)

        nova_rota = rota.copy()
        nova_rota[elemento1], nova_rota[elemento2] = nova_rota[elemento2], nova_rota[elemento1]     # troca os elementos especificos que foram permutados para gerar um vizinho

        if calcula_custo(nova_rota, matriz) != float('inf'):
            return nova_rota

    return None

def temp_inicial(rota_inicial, T_baixa, sa_max, matriz):
    custo_inicial = calcula_custo(rota_inicial, matriz)
    if custo_inicial == float('inf'):
        print("ERRO: Rota inicial inválida!")
        return None
    while True:
        vizinhos_aceitos = 0
        vizinhos_avaliados = 0

        tentativas = 0
        limite_tentativas = sa_max * 100

        while vizinhos_avaliados < sa_max:
            vizinho = gerar_vizinhos(rota_inicial, matriz)
            tentativas += 1

            if tentativas > limite_tentativas:
                print("Não foi possível encontrar vizinhos válidos suficientes.")
                return None

            if vizinho is None:
                continue

            custo_vizinho = calcula_custo(vizinho, matriz)
            vizinhos_avaliados += 1
            # === CRITERIO DE METROPOLIS ===
            delta_e = custo_vizinho - custo_inicial

            if delta_e <= 0:
                vizinhos_aceitos += 1
            else:
                probabilidade = math.exp(-delta_e/T_baixa)
                if probabilidade > random.random():                     # gera um valor entre 0 e 1 e compara com a probabilidade
                    vizinhos_aceitos += 1

        taxa_aceitacao = (vizinhos_aceitos / vizinhos_avaliados) * 100

        if taxa_aceitacao > 90:
            return T_baixa
        else:
            T_baixa *= 1.1

def simulated_annealing(rota_inicial, matriz, sa_max, alfa, T_baixa):
    T_min = 0.000001

    temperatura = temp_inicial(rota_inicial, T_baixa, sa_max, matriz)
    if temperatura is None:
        return None, float('inf')

    rota_atual = rota_inicial.copy()
    melhor_rota = rota_inicial.copy()

    custo_atual = calcula_custo(rota_atual, matriz)
    melhor_custo = custo_atual

    while temperatura > T_min:
        vizinhos_avaliados = 0

        tentativas = 0
        limite_tentativas = sa_max * 100

        while vizinhos_avaliados < sa_max:
            vizinho = gerar_vizinhos(rota_atual, matriz)
            tentativas += 1

            if tentativas > limite_tentativas:
                print("Não foi possível encontrar vizinhos válidos suficientes.")
                return melhor_rota, melhor_custo

            if vizinho is None:
                continue

            custo_vizinho = calcula_custo(vizinho, matriz)

            vizinhos_avaliados += 1

            # === CRITERIO DE METROPOLIS ===
            delta_e = custo_vizinho - custo_atual

            if delta_e <= 0:
                rota_atual = vizinho.copy()
                custo_atual = custo_vizinho
            else:
                probabilidade = math.exp(-delta_e/temperatura)
                if probabilidade > random.random():
                    rota_atual = vizinho.copy()
                    custo_atual = custo_vizinho

            if custo_atual < melhor_custo:
                melhor_custo = custo_atual
                melhor_rota = rota_atual.copy()

        # === RESFRIAMENTO ===
        temperatura *= alfa

    return melhor_rota, melhor_custo

# cria uma lista inicial com todos os pontos
def gerar_rota_inicial(matriz, num_vertices):
    rota = [1]
    visitadas = {1}

    def buscar():
        cidade_atual = rota[-1]

        if len(rota) == num_vertices:
            return matriz[cidade_atual - 1][rota[0] - 1] > 0

        vizinhos = []

        for cidade in range(1, num_vertices + 1):
            if cidade not in visitadas and matriz[cidade_atual - 1][cidade - 1] > 0:
                vizinhos.append(cidade)

        random.shuffle(vizinhos)

        for vizinho in vizinhos:
            rota.append(vizinho)
            visitadas.add(vizinho)

            if buscar():
                return True

            rota.pop()
            visitadas.remove(vizinho)

        return False

    if buscar():
        return rota

    return None

# --------- TESTE ------------
# configuracoes estabelecidas apos testes de tempo de execucao
sa_max =30
alfa = 0.95
T_baixa = 0.1

pasta_entradas = "entradas"
pasta_saidas = "saidas"

os.makedirs(pasta_saidas, exist_ok=True)

arquivos = sorted(glob.glob(os.path.join(pasta_entradas, "*.txt")))

for caminho_entrada in arquivos:

    nome_entrada = os.path.basename(caminho_entrada)
    nome_saida = nome_entrada.replace("Entrada", "Saida")
    caminho_saida = os.path.join(pasta_saidas, nome_saida)

    print(f"\nProcessando {nome_entrada}...")

    matriz = []

    with open(caminho_entrada, "r", encoding="utf-8") as f:
        conteudo = f.readlines()
        num_vertices = int(conteudo[0])

        for linha in conteudo[1:]:
            matriz.append(list(map(int, linha.split())))

    # Verifica se a matriz é simétrica
    simetrica = True

    for i in range(num_vertices):
        for j in range(num_vertices):
            if matriz[i][j] != matriz[j][i]:
                simetrica = False
                break
        if not simetrica:
            break

    if not simetrica:
        print(f"ERRO: {nome_entrada} não possui matriz simétrica.")
        continue

    with open(caminho_saida, "w", encoding="utf-8") as saida:

        for execucao in range(1, 4):

            tempo_inicio = time.time()

            rota_inicial = gerar_rota_inicial(matriz, num_vertices)

            if rota_inicial is None:
                saida.write(
                    f"Execução {execucao}: Não foi encontrada uma rota válida.\n\n"
                )
                continue

            melhor_rota, melhor_custo = simulated_annealing(
                rota_inicial, matriz, sa_max, alfa, T_baixa
            )

            tempo_fim = time.time()

            saida.write(f"Execução {execucao}:\n")
            saida.write(f"Melhor rota: {melhor_rota}\n")
            saida.write(f"Custo: {melhor_custo}\n\n")

            print(
                f"Execução {execucao}/3 concluída. "
                f"Custo: {melhor_custo}"
            )

    print(f"Resultado salvo em: {caminho_saida}")

print("\nTodas as entradas foram processadas!")
