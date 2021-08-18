import socket
from select import select
import sys
import threading
import json

HOST = ""
PORTA = 12000

entradas = [sys.stdin]
conexoes = {}
socketsClientes = {}
idsDisponiveis = list(range(1, 20))
lock = threading.Lock()


def iniciaServidor():
    sock = socket.socket()
    sock.bind((HOST, PORTA))
    sock.listen(20)
    sock.setblocking(False)
    entradas.append(sock)
    return sock


def atribuirId():
    return idsDisponiveis.pop(0)


def liberarId(id):
    return idsDisponiveis.append(id)


def notificaUsuarios(novoUser):
    for conexao in conexoes.values():
        enviaMensagem("Server", conexao["id"], f"Usuario {novoUser} se conectou")


def aceitaConexao(sock):
    clientSock, address = sock.accept()
    lock.acquire()
    clientId = atribuirId()
    notificaUsuarios(clientId)
    conexoes[clientSock] = {"address": address, "id": clientId}
    socketsClientes[clientId] = clientSock
    clientSock.send(str.encode(f"{clientId}"))
    lock.release()
    idsUsersAtivos = []
    for user in list(conexoes.values()):
        idsUsersAtivos.append(user["id"])
    enviaMensagem("Server", clientId, f"Users ativos: {idsUsersAtivos}")
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
                "de": "Server",
                "para": idDestinatario,
                "tipo": "msg",
                "text": "Usuario nao encontrado",
            }
        )
        remetente.send(str.encode(f"{len(msgJson)},{msgJson}"))
    else:
        destinatario = socketsClientes[int(idDestinatario)]
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
    while True:
        msg = clientSock.recv(1024)
        if not msg:
            print("Encerrando conexão com o cliente {}\n".format(address))
            lock.acquire()
            del conexoes[clientSock]
            del socketsClientes[clienteId]
            liberarId(clienteId)
            lock.release()
            clientSock.close()
            return
        msgDecodada = msg.decode("utf-8")
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
                enviaMensagem("Servidor", clienteId, str(idsUsers))
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
            if pronto == socket:
                clientSocket, address = aceitaConexao(socket)
                print("Conexão estabelecida com:", address)
                cliente = threading.Thread(
                    target=recebeMensagem, args=(clientSocket, address)
                )
                cliente.start()
            elif pronto == sys.stdin:
                msg = input()
                if msg == "sair":
                    for client in conexoes:
                        client.join()
                    socket.close()
                    sys.exit()
                elif msg == "hist":
                    print(str(conexoes.values()))


main()
