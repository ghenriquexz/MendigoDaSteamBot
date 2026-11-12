import os
import requests

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN_TELEGRAM")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

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

verificar_bot()


def enviar_mensagem(chat_id, texto):
    resposta = requests.post(f"{BASE_URL}sendMessage", data={"chat_id": chat_id, "text": texto}, timeout=15)
    dados_resposta = resposta.json()

    print ("Resposta do Mendigo:", dados_resposta.get("ok"))

def receber_mensagens():
    resposta_mensagem = requests.get(f"{BASE_URL}getUpdates", timeout=15)
    dados_mensagem = resposta_mensagem.json()

    if not dados_mensagem.get("ok"):
        print("Erro ao receber mensagens:", dados_mensagem.get("error_code"))
        return
        
    mensagens = dados_mensagem.get("result", [])

    for atualização in mensagens:
        mensagem = atualização.get("message")
        update_id = atualização.get("update_id")

        if not mensagem:
            ultimo_update_id = update_id
            continue

        chat_id = mensagem["chat"]["id"]
        texto = mensagem.get("text", "")

        print(f"Mensagem recebida de {chat_id}: {texto}")

        if texto == "/start":
            enviar_mensagem(chat_id, "Olá! Eu sou o MendigoDaSteamBot! 🎮\n\nEm breve vou encontrar as melhores promoções da Steam para você!")
            
        elif texto == "/ajuda":
            enviar_mensagem(chat_id, "Comandos disponíveis:\n\n/start - Iniciar o bot\n/ajuda - Ver os comandos disponíveis\n\nEm breve, mais funcionalidades serão adicionadas!")
            
        else:
            enviar_mensagem(chat_id, "Desculpe, não entendi sua mensagem. Por favor, use /start ou /ajuda para obter assistência.")
            
        ultimo_update_id = update_id
        if ultimo_update_id is not None:
            proximo_offset = ultimo_update_id + 1
            
        requests.get(
        f"{BASE_URL}getUpdates",
        params={
            "offset": proximo_offset
        },
        timeout=15
        )

    print("Atualizações processadas!")

if __name__ == "__main__":
    if verificar_bot():
        receber_mensagens()