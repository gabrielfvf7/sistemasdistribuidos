import socket
import json
import sys
from select import select

entradas = [sys.stdin]

idProprio = ""


def cliente():
    HOST = "localhost"  # maquina onde esta o par passivo
    PORTA = 6000  # porta que o par passivo esta escutando

    # cria socket
    sock = socket.socket()  # default: socket.AF_INET, socket.SOCK_STREAM

    # conecta-se com o par passivo
    sock.connect((HOST, PORTA))
    response = sock.recv(1024)  # recebe a resposta do servidor
    response = response.decode("utf-8")
    idProprio = response
    entradas.append(sock)

    while True:  # roda em loop enquanto a mensagem de sair não for recebida
        leitura, escrita, excecao = select(entradas, [], [])
        for pronto in leitura:
            if pronto == sys.stdin:
                messageToSend = input()
                if "/msg" in messageToSend:
                    msgSplit = messageToSend.split(" ")
                    conteudo = input("Digite sua mensagem")
                    msgJson = json.dumps(
                        {
                            "de": idProprio,
                            "para": msgSplit[1],
                            "tipo": "msg",
                            "texto": conteudo,
                        }
                    )
                    sock.send(str.encode(f"{len(msgJson)},{msgJson}"))
            elif pronto == sock:
                response = sock.recv(1024)  # recebe a resposta do servidor
                response = response.decode("utf-8")
                print(response)

        # envia a mensagem para o servidor
        # if messageToSend == "sair":  # se a mensagem for sair, encerra o loop
        #     print("Encerrando conexão")
        #     break
        # decodifica a mensagem recebido para string
        # print(response)  # mostra a mensagem para o usuário
        # print("---------------------------------------------------------------")
        # repeat = input(
        #     "Se deseja encerrar a conexão, digite 'sair' e dê enter, caso queira continuar apenas dê enter\n"
        # )
        # if repeat == "sair":
        #     print("\nEncerrando conexão")
        #     break
    sock.close()  # fecha a conexão
    print("Conexão encerrada")
    print("---------------------------------------------------------------")


# chama a funçao principal da aplicação cliente
cliente()
