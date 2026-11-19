import os
import requests
import time

import sys
sys.path.append(os.path.abspath("../STEAM"))

from steam import buscar_jogo, consultar_jogo

from dotenv import load_dotenv

load_dotenv(os.path.abspath("../CONFIG/.env"))

TOKEN = os.getenv("TOKEN_TELEGRAM")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
pesquisas_pendentes = {}


def verificar_bot():
    if not TOKEN:
        print("Token do bot não encontrado. Verifique o arquivo .env.")
        return False

    print("Token do bot encontrado. Iniciando o bot...")
    resposta = requests.get(f"{BASE_URL}getMe", timeout=15)

    DADOS = resposta.json()
    if DADOS.get("ok"):
        print(f"Bot iniciado com sucesso! Nome do bot: {DADOS['result']['first_name']}")
        print("Nome:", DADOS["result"]["first_name"])
        print("Usuário:", DADOS["result"]["username"]) 
        return True
    else:
        print("ERRO:", DADOS["error_code"])
        return False

def enviar_mensagem(chat_id, texto):
    resposta = requests.post(f"{BASE_URL}sendMessage", data={"chat_id": chat_id, "text": texto}, timeout=15)
    dados_resposta = resposta.json()

    print ("Resposta do Mendigo:", dados_resposta.get("ok"))

def enviar_foto(chat_id, imagem, legenda):
    resposta = requests.post(
        f"{BASE_URL}sendPhoto",
        data={
            "chat_id": chat_id,
            "photo": imagem,
            "caption": legenda
        },
        timeout=30
    )

    dados = resposta.json()
    print("Foto enviada:", dados.get("ok"))


def receber_mensagens():
    offset = None

    print("Aguardando mensagens...")

    try:
        while True:

            parametros = {"timeout": 30}

            if offset is not None:
                parametros["offset"] = offset

            try:
                resposta_mensagem = requests.get(
                    f"{BASE_URL}getUpdates",
                    params=parametros,
                    timeout=35
                )

            except requests.exceptions.RequestException as erro:
                print("Erro ao receber mensagens:", erro)
                print("Tentando conectar novamente...")
                time.sleep(5)
                continue

            dados_mensagem = resposta_mensagem.json()

            if not dados_mensagem.get("ok"):
                print("Erro ao receber mensagens:")
                print("Código:", dados_mensagem.get("error_code"))
                print("Descrição:", dados_mensagem.get("description"))

                time.sleep(5)
                continue

            mensagens = dados_mensagem.get("result", [])

            for atualizacao in mensagens:

                update_id = atualizacao.get("update_id")
                offset = update_id + 1

                mensagem = atualizacao.get("message")

                if not mensagem:
                    continue

                chat_id = mensagem["chat"]["id"]
                texto = mensagem.get("text", "")

                print(f"Mensagem recebida de {chat_id}: {texto}")

                if texto == "/start":
                    enviar_mensagem(
                        chat_id,
                        "Olá! Eu sou o MendigoDaSteamBot! 🎮\n\n Vou encontrar as melhores promoções da Steam para você! \n\n Qualquer dúvida, use /ajuda ! 😎"
                    )

                elif texto == "/ajuda":
                    enviar_mensagem(
                        chat_id,
                        "Comandos disponíveis:\n\n/start - Iniciar o bot\n/ajuda - Ver os comandos disponíveis\n\n /preco - Pesquisar jogo por preço\n\nExemplo: /preco Cyberpunk 2077\n\nEm breve, mais funcionalidades serão adicionadas!"
                    )

                elif chat_id in pesquisas_pendentes and texto.isdigit():

                    jogos = pesquisas_pendentes[chat_id]
                    escolha = int(texto)

                    if escolha < 1 or escolha > len(jogos):
                        enviar_mensagem(
                            chat_id,
                            f"Escolha um número entre 1 e {len(jogos)}."
                        )

                    else:
                        jogo_escolhido = jogos[escolha - 1]

                        app_id = jogo_escolhido["app_id"]

                        detalhes = consultar_jogo(app_id)

                        pesquisas_pendentes.pop(chat_id)

                        if detalhes:
                            legenda = (
                            f"🎮 {detalhes['nome']}\n\n"
                            f"Preço original: {detalhes['preco_original']}\n"
                            f"Preço atual: {detalhes['preco_atual']}\n"
                            f"Desconto: {detalhes['desconto']}%\n\n"
                            f"🔗 {detalhes['link']}"
                            )

                            enviar_foto(
                                chat_id,
                                detalhes["header"],
                                legenda
                            )

                        else:
                            enviar_mensagem(
                                chat_id,
                                "Não foi possível consultar os detalhes desse jogo."
                            )

                elif texto.startswith("/preco"):
                    nome_jogo = texto.replace("/preco", "", 1).strip()

                    if not nome_jogo:
                        enviar_mensagem(
                            chat_id,
                            "Digite o nome do jogo. Exemplo: /preco Portal 2"
                        )
                        continue

                    enviar_mensagem(
                        chat_id,
                        f'Pesquisando "{nome_jogo}" na Steam...'
                    )

                    jogos = buscar_jogo(nome_jogo)

                    if not jogos:
                        enviar_mensagem(
                            chat_id,
                            f"Não encontrei '{nome_jogo}' na Steam."
                        )
                        continue

                    pesquisas_pendentes[chat_id] = jogos[:5]

                    mensagem_jogos = "Selecione o jogo desejado:\n\n"

                    for i, jogo in enumerate(jogos[:5], start=1):
                        mensagem_jogos += f"{i}. {jogo['nome']}\n"

                    mensagem_jogos += "\nDigite o número correspondente ao jogo."
                    enviar_mensagem(chat_id, mensagem_jogos)


                else:
                    enviar_mensagem(
                        chat_id,
                        "Desculpe, não entendi sua mensagem. Por favor, use /start ou /ajuda para obter assistência."
                    )

    except KeyboardInterrupt:
        print("\nBot interrompido pelo usuário.")


if __name__ == "__main__":
    if verificar_bot():
        receber_mensagens()
