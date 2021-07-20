# Exemplo basico socket (lado passivo)

import socket

HOST = ""  # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 6000  # porta onde chegarao as mensagens para essa aplicacao

# cria um socket para comunicacao
sock = socket.socket()  # valores default: socket.AF_INET, socket.SOCK_STREAM

# vincula a interface e porta para comunicacao
sock.bind((HOST, PORTA))

# define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
sock.listen(1)

# aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
(
    novoSock,
    endereco,
) = sock.accept()  # retorna um novo socket e o endereco do par conectado
print("Conectado com: ", endereco)

while True:  # roda em loop enquanto a mensagem de sair não for recebida
    # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
    msg = novoSock.recv(1024)  # argumento indica a qtde maxima de dados
    msgDecodada = msg.decode(
        "utf-8"
    )  # faz a decodificação da mensagem de bytes para string
    if (
        msgDecodada == "sair"
    ):  # verifica se a mensagem recebdia é igual a palavra reservada para encerrar a conexão
        print("Encerrando conexão")
        break
    else:
        print(
            "Recebida a mensagem:", msgDecodada
        )  # mostra a mensagem enviada pelo cliente
        print("Reenviando para o cliente\n")
    # envia mensagem de resposta
    novoSock.send(msg)  # envia para o cliente a mensagem recebida

# fecha o socket da conexao
novoSock.close()

# fecha o socket principal
sock.close()
