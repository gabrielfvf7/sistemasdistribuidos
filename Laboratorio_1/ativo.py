# Exemplo basico socket (lado ativo)

import socket

HOST = "localhost"  # maquina onde esta o par passivo
PORTA = 6000  # porta que o par passivo esta escutando

# cria socket
sock = socket.socket()  # default: socket.AF_INET, socket.SOCK_STREAM

# conecta-se com o par passivo
sock.connect((HOST, PORTA))

while True:  # roda em loop enquanto a mensagem de sair não for recebida
    messageToSend = input(
        'Escreva sua mensagem: (Digite "sair" para encerrar a conexão)\n'
    )  # pega o input digitado pelo usuário
    messageEncoded = messageToSend.encode(
        "utf-8"
    )  # faz a codificação da mensagem, passando de string para bytes
    sock.send(messageEncoded)  # envia a mensagem para o servidor
    if messageToSend == "sair":  # se a mensagem for sair, encerra o loop
        print("Encerrando conexão")
        break
    response = sock.recv(1024)  # recebe a resposta do servidor
    response = response.decode("utf-8")  # decodifica a mensagem recebido para string
    print("Mensagem recebida do servidor:", response, "\n")
sock.close()  # fecha a conexão
