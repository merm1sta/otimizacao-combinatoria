# por formalismo, considera-se que cada rainha estara posicionada em uma coluna distinta da outra (facilita a modelagem)
# com isso, ao inves de matriz, sera usado um vetor: indice representa a coluna e o valor correspondente aquela posicao representa a linha
# a abordagem sera: avaliar todas as rainhas e o numero de ataques fornecido por cada movimento; ir atualizando o melhor movimento (com menor num de ataques)
# para o algoritmo nao ficar preso em um otimo local:
#           - se houver empate, aceitara o primeiro movimento com numero igual de ataques
#           - se nao houver melhora, encerra a tentativa com até 5 movimentos de empate (sem melhora)

import os
import glob
import random

def calcula_ataques(posicao_rainhas):
    total_ataques = 0

    for i in range(len(posicao_rainhas)):                       # avalia a rainha da primeira coluna ...
        for j in range(i + 1, len(posicao_rainhas)):            # ... com as rainhas das colunas seguintes
            # tem ataque na mesma linha?
                if posicao_rainhas[i] == posicao_rainhas[j]:
                    total_ataques += 1
                elif abs(posicao_rainhas[i] - posicao_rainhas[j]) == abs(i - j):
                    total_ataques += 1

    return total_ataques

# um pequeno ajuste fez com que ele deixasse de ser estritamente guloso, pois ficava preso com 8 rainhas
def avalia_movimento(posicao_rainhas, n, configuracoes_visitadas):
    ataques_movimento = calcula_ataques(posicao_rainhas)                       # quant de ataques do melhor movimento encontrado comeca com a sol atual
    movimento = 0                               # linha para a qual a rainha foi movimentada
    rainha_movida = 0                           # coluna da rainha que foi movida
    melhora = False                             # para auxiliar a escapar de minimos locais
    escape = False                              # estrategia extra
    retrocessa = False                          # para escapar de um problema

    for i in range(n):           # percorre todas as rainhas
        for j in range(n):                   # percorre todas as linhas possiveis
            # evitar que sua linha inicial seja avaliada desnecessariamente
            if j + 1 == posicao_rainhas[i]:
                continue
            # movimenta a rainha da coluna i para a linha seguinte
            testa_posicao = posicao_rainhas.copy()
            testa_posicao[i] = j + 1                                # troca a linha da rainha
            tupla = tuple(testa_posicao)
            if tupla not in configuracoes_visitadas:
                novo_movimento = calcula_ataques(testa_posicao)
                if ataques_movimento > novo_movimento:                  # se o novo movimento proporcionar menos ataques
                    ataques_movimento = novo_movimento
                    movimento = j + 1
                    rainha_movida = i
                    melhora = True

    if not melhora:
        movimentos_escape = []
        for i in range(n):
            for j in range(n):
                # evitar que sua linha inicial seja avaliada desnecessariamente
                if j + 1 == posicao_rainhas[i]:
                    continue
                nova_config = posicao_rainhas.copy()
                nova_config[i] = j + 1

                ataques_sem_melhora = calcula_ataques(nova_config)
                tupla = tuple(nova_config)

                if tupla not in configuracoes_visitadas and ataques_sem_melhora == ataques_movimento:
                    movimentos_escape.append((i, j + 1))
                    escape = True

        if movimentos_escape:
            sorteados = random.choice(movimentos_escape)
            rainha_movida, movimento = sorteados
            escape = True

    # permite retrocesso breve
    if not melhora and not escape:
        movimento_retrocesso = []
        for i in range(n):
            for j in range(n):
                if j + 1 == posicao_rainhas[i]:
                    continue
                retrocesso = posicao_rainhas.copy()
                retrocesso[i] = j + 1
                ataques_retrocesso = calcula_ataques(retrocesso)
                tupla = tuple(retrocesso)

                if ataques_retrocesso == calcula_ataques(posicao_rainhas) + 1 and tupla not in configuracoes_visitadas:
                    movimento_retrocesso.append((i, j + 1))

        if movimento_retrocesso:
            rainha_movida, movimento = random.choice(movimento_retrocesso)
            retrocessa = True


    return rainha_movida, movimento, ataques_movimento, melhora, escape, retrocessa


def greedy(posicao_rainhas, n):
    configuracoes_visitadas = []
    configuracoes_visitadas.append(tuple(posicao_rainhas))  # config inicial

    aumentos_consecutivos = 0
    escapes_consecutivos = 0
    sucesso = False

    while calcula_ataques(posicao_rainhas) > 0 and escapes_consecutivos < 20 and aumentos_consecutivos < 5:
        rainha, movimento, ataques_movimento, melhora, escape, retrocessa = avalia_movimento(posicao_rainhas, n, configuracoes_visitadas)
        if melhora:
            escapes_consecutivos = 0
            aumentos_consecutivos = 0
        elif escape:
            escapes_consecutivos += 1
            aumentos_consecutivos = 0
        elif retrocessa:
            aumentos_consecutivos += 1
            escapes_consecutivos = 0
        else:
            print("Configuração em que a busca parou:", posicao_rainhas)
            print("Quantidade de ataques:", calcula_ataques(posicao_rainhas))
            print("ERRO: Não foi encontrado nenhum movimento válido!")
            break
        posicao_rainhas[rainha] = movimento
        nova_tupla = tuple(posicao_rainhas)
        configuracoes_visitadas.append(nova_tupla)

    if escapes_consecutivos == 20:
        print("ERRO: Atingiu o limite de escapes consecutivos.")

    if aumentos_consecutivos == 5:
        print("ERRO: Atingiu o limite de retrocessos consecutivos.")

    if calcula_ataques(posicao_rainhas) == 0:
        print("SUCESSO: Solução encontrada!")
        sucesso = True
        return posicao_rainhas, sucesso
    else:
        print("ERRO: Não foi possível encontrar nenhuma solução válida durante a busca.")
        return posicao_rainhas, sucesso

# ==================== LEITURA E ESCRITA DOS ARQUIVOS ======================
pasta_entradas = "entradas"
pasta_saidas = "saidas"

os.makedirs(pasta_saidas, exist_ok=True)

arquivos = sorted(glob.glob(os.path.join(pasta_entradas, "*.txt")),
            key=lambda arquivo: int(os.path.splitext(os.path.basename(arquivo))[0])
)

for caminho_entrada in arquivos:
    nome_entrada = os.path.basename(caminho_entrada)
    nome_saida = nome_entrada.replace("Entrada", "Saida")
    caminho_saida = os.path.join(pasta_saidas, nome_saida)

    print(f"\nProcessando {nome_entrada}...")

    with open(caminho_entrada, "r", encoding="utf-8") as f:
        conteudo = f.readlines()
        n = int(conteudo[0])                                            # numero de rainhas
        posicao_rainhas = list(map(int, conteudo[1].split()))           # posicionamento das rainhas em cada linha

        if n <= 0:
            print("ERRO: Número de rainhas inválido.")
            continue

        if len(posicao_rainhas) != n:
            print("ERRO: Rainhas insuficientes (ou em excesso) no tabuleiro!")
            continue

        # verifica se nao ha posicoes invalidas (casa inexistente no tabuleiro n x n)
        erro = False
        for i in range(n):
            if posicao_rainhas[i] > n or posicao_rainhas[i] < 1:
                print(f"ERRO: Posição da Rainha {i + 1} é inválida!")
                erro = True

        if erro:
            continue

    solucao, sucesso = greedy(posicao_rainhas, n)

    if not sucesso:
        print("ERRO: Busca encerrada sem encontrar uma solução válida.")
        continue

    with open(caminho_saida, "w", encoding="utf-8") as saida:
        for i in range(len(solucao)):
            saida.write(f"Rainha {i + 1} - Posição: ({i + 1}, {solucao[i]})\n")         # imrpime no formato (coluna, linha)

    print(f"Resultado salvo em: {caminho_saida}")

print("\nTodas as entradas foram processadas!")

