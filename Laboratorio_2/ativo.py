import socket

def cliente():
    HOST = "localhost"  # maquina onde esta o par passivo
    PORTA = 6000  # porta que o par passivo esta escutando

    # cria socket
    sock = socket.socket()  # default: socket.AF_INET, socket.SOCK_STREAM

    # conecta-se com o par passivo
    sock.connect((HOST, PORTA))

    while True:  # roda em loop enquanto a mensagem de sair não for recebida
        messageToSend = input(
            "Digite o nome do arquivo completo junto de sua extensão seguida da palavra que deseja buscar e dê enter\nExemplo: exemplo.txt maçã\nOu digite 'sair' para terminar a sessão\n"
        )  # pega o input digitado pelo usuário
        messageEncoded = messageToSend.encode(
            "utf-8"
        )  # faz a codificação da mensagem, passando de string para bytes
        sock.send(messageEncoded)  # envia a mensagem para o servidor
        if messageToSend == "sair":  # se a mensagem for sair, encerra o loop
            print("Encerrando conexão")
            break
        response = sock.recv(1024)  # recebe a resposta do servidor
        response = response.decode(
            "utf-8"
        )  # decodifica a mensagem recebido para string
        print(response) # mostra a mensagem para o usuário
        print('---------------------------------------------------------------')
        repeat = input("Se deseja encerrar a conexão, digite 'sair' e dê enter, caso queira continuar apenas dê enter\n")
        if repeat == "sair":
            print("\nEncerrando conexão")
            break
    sock.close()  # fecha a conexão
    print('Conexão encerrada')
    print('---------------------------------------------------------------')

# chama a funçao principal da aplicação cliente
cliente()
