import socket
import json
import sys
from select import select

entradas = [sys.stdin]

idProprio = ""


def mostraMenu():
    print(
        "/msg {id}: para enviar uma mensagem \n/sair: para sair \n/help: para mostrar o menu\n/listar: mostra users ativos"
    )


def cliente():
    HOST = "localhost"  # maquina onde esta o par passivo
    PORTA = 12000  # porta que o par passivo esta escutando

    # cria socket
    sock = socket.socket()  # default: socket.AF_INET, socket.SOCK_STREAM

    # conecta-se com o par passivo
    sock.connect((HOST, PORTA))
    response = sock.recv(1024)  # recebe a resposta do servidor
    response = response.decode("utf-8")
    idProprio = response
    entradas.append(sock)
    mostraMenu()

    while True:  # roda em loop enquanto a mensagem de sair não for recebida
        leitura, escrita, excecao = select(entradas, [], [])
        for pronto in leitura:
            if pronto == sys.stdin:
                messageToSend = input()
                if "/msg" in messageToSend:
                    msgSplit = messageToSend.split(" ")
                    conteudo = input("Digite sua mensagem:\n")
                    msgJson = json.dumps(
                        {
                            "de": idProprio,
                            "para": msgSplit[1],
                            "tipo": "msg",
                            "texto": conteudo,
                        }
                    )
                    sock.send(str.encode(f"{len(msgJson)},{msgJson}"))
                if "/sair" == messageToSend:
                    sock.close()
                    sys.exit()
                if "/help" == messageToSend:
                    mostraMenu()
                if "/listar" == messageToSend:
                    msgJson = json.dumps(
                        {
                            "de": idProprio,
                            "para": 0,
                            "tipo": "cmd",
                            "texto": "listar",
                        }
                    )
                    sock.send(str.encode(f"{len(msgJson)},{msgJson}"))
            elif pronto == sock:
                response = sock.recv(1024)  # recebe a resposta do servidor
                response = response.decode("utf-8")
                msgSplit = response.split(",{")
                tamanhoMsg = msgSplit[0]
                msgJson = "{" + msgSplit[1]

                while int(tamanhoMsg) - len(msgJson) > 0:
                    msgJson = msgJson + sock.recv(1024).decode("utf-8")
                jsonTratado = json.loads(msgJson)
                textoMsg = jsonTratado["text"]
                fromMsg = jsonTratado["de"]
                print(f"from {fromMsg}: {textoMsg}\n")


# chama a funçao principal da aplicação cliente
cliente()
