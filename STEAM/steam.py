import requests
def buscar_jogo(nome):

    url = "https://store.steampowered.com/api/storesearch/"

    parametros = {"term": nome, "l": "brazilian", "cc": "br"}

    resposta = requests.get(url, params=parametros, timeout=15)
    dados = resposta.json()

    resultados = dados.get("items", [])

    if not resultados:
        print("Nenhum jogo encontrado!")
        return None

    jogos = []

    for jogo in resultados:
        jogos.append({
            "nome": jogo.get("name"),
            "app_id": jogo.get("id"),
        })

    return jogos



def consultar_jogo(app_id):
    url = f"https://store.steampowered.com/api/appdetails"

    parametros = {"appids": app_id, "cc": "br", "l": "brazilian"}

    resposta = requests.get(url, params=parametros, timeout=15)
    dados = resposta.json()
    
    print("Resposta recebida da Steam!")

    if not dados[str(app_id)]["success"]:
        print("Jogo não encontrado!")
        return None
    
    else:
        jogo = dados[str(app_id)]["data"]

        preco = jogo.get("price_overview")

        if preco:
            preco_original = preco.get("initial") / 100
            preco_atual = preco.get("final") / 100
            desconto = preco.get("discount_percent")

            preco_original = f"R$ {preco_original:.2f}".replace(".", ",")
            preco_atual = f"R$ {preco_atual:.2f}".replace(".", ",")

        else:
            preco_original = "Indisponível"
            preco_atual = "Indisponível"
            desconto = 0

        return {
            "nome": jogo.get("name"),
            "header": jogo.get("header_image"),
            "link": f"https://store.steampowered.com/app/{app_id}/",
            "avaliacao": jogo.get("metacritic", {}).get("score"),
            "preco_original": preco_original,
            "preco_atual": preco_atual,
            "desconto": desconto
        }


def pesquisar_e_consultar(nome,escolha):

    jogos = buscar_jogo(nome)

    if not jogos:
        return None

    if escolha < 1 or escolha > len(jogos):
        print("Escolha inválida!")
        return None

    app_id = jogos[escolha - 1]["app_id"]

    detalhes = consultar_jogo(app_id)

    return detalhes