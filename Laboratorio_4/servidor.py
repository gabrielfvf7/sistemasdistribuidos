import socket
from select import select
import sys
import threading
import json

HOST = ""
PORTA = 10000

entradas = [sys.stdin]
conexoes = {}
socketsClientes = {}
idsDosClientes = list(range(1, 20))
lock = threading.lock()

def iniciaServidor():
    sock = socket.socket()
    sock.bind((HOST, PORTA))
    sock.listen(5)
    sock.setblocking(False)
    entradas.append(sock)
    return sock

def atribuirId():
    return idsDosClientes.pop(0)

def liberarId(id):
    return idsDosClientes.append(id)

def aceitaConexao(sock):
    clientSock, address = sock.accept()
    lock.acquire()
    clientId = atribuirId()
    conexoes[clientSock] = {
        "address": address,
        "id": clientId
    }
    socketsClientes[clientId] = clientSock
    lock.release()
    idsUsersAtivos = []
    for user in list(conexoes.values()):
        idsUsersAtivos.append(u['id'])
    clientSock.send(str.encode(f"{idsUsersAtivos}"))
    
    print(f"{clientId} se conectou. End: {str(address)}")

    return clientSock, address

def listarUsuarios():
    idsUsuariosAtivos = []
    for user in list(conexoes.values()):
        idsUsuariosAtivos.append(user["id"])
    return idsUsuariosAtivos

