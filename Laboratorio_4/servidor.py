import socket
from select import select
import sys
import threading
import json

HOST = ""
PORTA = 6000

entradas = [sys.stdin]
conexoes = {}
socketsClientes = {}
idsDisponiveis = list(range(1, 20))
lock = threading.Lock()


def iniciaServidor():
    sock = socket.socket()
    sock.bind((HOST, PORTA))
    sock.listen(5)
    sock.setblocking(False)
    entradas.append(sock)
    return sock


def atribuirId():
    return idsDisponiveis.pop(0)


def liberarId(id):
    return idsDisponiveis.append(id)


def aceitaConexao(sock):
    clientSock, address = sock.accept()
    lock.acquire()
    clientId = atribuirId()
    conexoes[clientSock] = {"address": address, "id": clientId}
    socketsClientes[clientId] = clientSock
    clientSock.send(str.encode(f"{clientId}"))
    lock.release()
    idsUsersAtivos = []
    for user in list(conexoes.values()):
        idsUsersAtivos.append(user["id"])
    enviaMensagem(0, clientId, f"Users ativos: {idsUsersAtivos}")
    # clientSock.send(str.encode(f"{idsUsersAtivos}"))

    print(f"{clientId} se conectou. End: {str(address)}")

    return clientSock, address


def listarUsuarios():
    idsUsuariosAtivos = []
    for user in list(conexoes.values()):
        idsUsuariosAtivos.append(user["id"])
    return idsUsuariosAtivos


def enviaMensagem(idRemetente, idDestinatario, conteudo):
    if idDestinatario in idsDisponiveis:
        remetente = socketsClientes[idRemetente]
        msgJson = json.dumps(
            {
                "de": 0,
                "para": idDestinatario,
                "tipo": "msg",
                "text": "Usuario nao encontrado",
            }
        )
        print("enviou msg")
        remetente.send(str.encode(f"{len(msgJson)},{msgJson}"))
    else:
        destinatario = socketsClientes[idDestinatario]
        msgJson = json.dumps(
            {
                "de": idRemetente,
                "para": idDestinatario,
                "tipo": "msg",
                "text": conteudo,
            }
        )
        destinatario.send(str.encode(f"{len(msgJson)},{msgJson}"))


def recebeMensagem(clientSock, address):
    clienteId = conexoes[clientSock]["id"]
    while True:  # roda em loop enquanto a mensagem de sair não for recebida
        # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
        msg = clientSock.recv(1024)  # argumento indica a qtde maxima de dados
        if not msg:  # encerra conexão com o cliente caso não recebe mensagem
            print("Encerrando conexão com o cliente {}\n".format(address))
            # uso do lock para evitar problema de corrida
            lock.acquire()
            del conexoes[clientSock]
            del socketsClientes[clienteId]
            liberarId(clienteId)
            lock.release()
            clientSock.close()
            return
        msgDecodada = msg.decode(
            "utf-8"
        )  # faz a decodificação da mensagem de bytes para string
        msgSplit = msgDecodada.split(",{")
        tamanhoMsg = msgSplit[0]
        msgJson = "{" + msgSplit[1]

        while int(tamanhoMsg) - len(msgJson) > 0:
            msgJson = msgJson + clientSock.recv(1024).decode("utf-8")

        jsonTratado = json.loads(msgJson)
        tipoMsg = jsonTratado["tipo"]
        textoMsg = jsonTratado["texto"]
        destinatarioMsg = jsonTratado["para"]

        if tipoMsg == "msg":
            enviaMensagem(clienteId, destinatarioMsg, textoMsg)
        elif tipoMsg == "cmd":
            if textoMsg == "listar":
                idsUsers = listarUsuarios()
                # mandar msg
            elif textoMsg == "sair":
                lock.acquire()
                del conexoes[clientSock]
                del socketsClientes[clienteId]
                liberarId(clienteId)
                lock.release()
                clientSock.close()
                print("Encerrando conexão com o cliente {}\n".format(address))
                return


def main():
    socket = iniciaServidor()
    while True:
        leitura, escrita, excecao = select(entradas, [], [])
        for pronto in leitura:
            if pronto == socket:  # novo pedido de conexao
                clientSocket, address = aceitaConexao(socket)  # aceita nova conexao
                print("Conexão estabelecida com:", address)

                # cria nova thread para atender ao cliente conectado
                cliente = threading.Thread(
                    target=recebeMensagem, args=(clientSocket, address)
                )
                cliente.start()
            elif pronto == sys.stdin:
                msg = input()
                if msg == "sair":  # solicitação de finalização a partir do servidor
                    # apenas encerra quando não há clientes conectados
                    for client in conexoes:
                        client.join()
                    socket.close()
                    sys.exit()
                # comando para mostrar conexões do servidor
                elif msg == "hist":
                    print(str(conexoes.values()))


main()
