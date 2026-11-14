# cada arquivo eh composto por uma capacidade max do recipiente, numero de itens e peso de cada item
# teremos tres valores: C_max, n e C_item
# interessante armazenar quais itens foram adicionados em recipientes
import random
import math
import os
import glob

def peu(C_max, itens):
    if C_max <= 0:
        print("ERRO: Não há capacidade definida para os recipientes!")
        return None

    n = len(itens)
    for i in range(n):
        if itens[i] < 0 or itens[i] > C_max:
            print("ERRO: Itens com pesaos inválidos!")
            return None

    recipientes = []  # itens em cada recip
    capacidade_restante = []  # espaco livre em cada recip

    itens_restantes = itens.copy()

    while itens_restantes:
        indice = random.randrange(len(itens_restantes))  # escolhe um item aleatorio
        item = itens_restantes.pop(indice)

        alocado = False

        for i in range(len(recipientes)):  # enquanto houver recip para testar
            if item <= capacidade_restante[i]:  # se o tamanho do item for menor ou igual a capacidade restante do recip
                recipientes[i].append(item)  # recipiente recebe o item
                capacidade_restante[i] -= item  # capacidade restante é decrementado o valor do item add
                alocado = True  # foi possivel alocar
                break

        if not alocado:  # se nao foi possivel alocar em nenhum recipiente
            recipientes.append([item])  # cria um recipiente novo com os itens
            capacidade_restante.append(C_max - item)  # atualiza a capacidade do recip

    teto_superior = len(recipientes)

    # ========= PD =========
    itens_ordenados = sorted(itens, reverse=True)  # organiza em ordem decrescente para facilitar na escolha do item

    # eh necessario conhecer o proximo item e a capacidade de cada recip

    # memorizacao de estados ja explorados
    estados_explorados = set()

    # em todos os problemas, sempre ha um teto min de recipientes
    soma = 0
    for i in range(len(itens)):
        soma += itens[i]

    min_recip = math.ceil(soma / C_max)  # -> calcula num min de recipientes em cada caso

    def func_recursiva(indice, capacidade_restante, distribuicao_recip):
        capacidades = sorted(capacidade_restante.copy())
        estado_atual = indice, tuple(capacidades)

        if indice == len(itens_ordenados):  # chegou no ultimo item da lista, ou seja, todos foram alocados
            return distribuicao_recip

        if estado_atual in estados_explorados:  # estados explorados armazena estados que falharam
            return None

        quant_recip = len(capacidade_restante)
        item_atual = itens_ordenados[indice]

        for i in range(quant_recip):
            espacos = capacidade_restante.copy()  # copia o estado dos recips
            itens_adicionados = []
            for j in range(quant_recip):
                itens_adicionados.append(distribuicao_recip[j].copy())
            if item_atual <= espacos[i]:  # se couber
                espacos[i] -= item_atual  # aloca
                # espacos = sorted(espacos)               # reordena4
                itens_adicionados[i].append(item_atual)
                resultado = func_recursiva(indice + 1, espacos, itens_adicionados)
                if resultado is not None:
                    return resultado

        estados_explorados.add(estado_atual)
        return None

    estado_inicial = []
    for i in range(min_recip):
        estado_inicial.append(C_max)

    novos_recip = min_recip
    novos_estados = estado_inicial.copy()

    distribuicao_recip = []
    for i in range(min_recip):
        distribuicao_recip.append([])

    solucao = func_recursiva(0, novos_estados, distribuicao_recip)

    while solucao is None and novos_recip < teto_superior:
        novos_recip += 1
        novos_estados.append(C_max)
        estados_explorados = set()
        nova_distribuicao = []
        for i in range(novos_recip):
            nova_distribuicao.append([])
        solucao = func_recursiva(0, novos_estados, nova_distribuicao)

    if solucao is None:
        solucao = recipientes

    return solucao

# ------------------- LEITURA E ESCRITA DE ARQUIVOS -----------------------
pasta_entradas = "entradas"
pasta_saidas = "saidas"

os.makedirs(pasta_saidas, exist_ok=True)

arquivos = sorted(glob.glob(os.path.join(pasta_entradas, "*.txt")))

for caminho_entrada in arquivos:

    nome_entrada = os.path.basename(caminho_entrada)
    nome_saida = nome_entrada.replace("Entrada", "Saida")
    caminho_saida = os.path.join(pasta_saidas, nome_saida)

    print(f"\nProcessando {nome_entrada}...")

    with open(caminho_entrada, "r", encoding="utf-8") as f:
        conteudo = f.readlines()
        C_max = int(conteudo[0])
        itens = list(map(int, conteudo[2].split()))


    with open(caminho_saida, "w", encoding="utf-8") as saida:
        solucao = peu(C_max, itens)
        if solucao is None:
            print("ERRO: Solução inválida!")
            continue
        else:
            n_recipientes = len(solucao)

        saida.write(f"Distribuição nos recipientes (1 a {n_recipientes}): {solucao}\n")
        saida.write(f"Número de recipientes: {n_recipientes}\n\n")

    print(f"Resultado salvo em: {caminho_saida}")

print("\nTodas as entradas foram processadas!")