import socket
from select import select
import sys
import threading


HOST = ""  # '' possibilita acessar qualquer endereco alcancavel da maquina local
PORTA = 10000  # porta onde chegarao as mensagens para essa aplicacao

# defina a lista de I/O de interessa
# já vem inclusa a entrada padrão
entradas = [sys.stdin]
# guarda conexões ativas
conexoes = {}
# lock para resolver problemas de corrida
lock = threading.Lock()


def formataTexto(texto):  # função auxiliar usada para retirar alguns sinais de pontuação das palavras, que poderiam atrapalhar a contagem
    return texto.replace("?", "").replace(",", "").replace(".", "").replace("!", "")


def contador(palavraParaContar, texto):  # função usada para contar o número de ocorrências de uma dada palavra em um arquivo
    ocorrencias = 0  # inicializa a variável responsável por armazenar o valor de ocorrências da palavra
    for linha in texto:  # loop que itera por cada linha do texto
        for palavra in linha.split():  # loop que itera por cada palavra do texto, o split é usado para separar a linha em palavras
            palavraFormatada = formataTexto(palavra)  # chama a função auxiliar para retirada de pontuação
            if palavraFormatada == palavraParaContar:  # verifica se a palavra atual é igual à palavra buscada
                ocorrencias += 1  # caso as palavras sejam iguais, incrementa a quantidade de ocorrências
    return ocorrencias


def leitor(fileToRead):  # função auxiliar para realizar a leitura do arquivo
    try:  # a função open é envolta dentro de um try para poder tratar o erro de arquivo não encontrado
        with open(fileToRead, "r") as foundFile:  # abre o arquivo em modo de leitura
            return foundFile.readlines()  # retorna as linhas do arquivo como uma lista
    except FileNotFoundError:  # caso o arquivo não seja encontrado, a função open dispara a exceção FileNotFoundError
        raise Exception("O arquivo solicitado não foi encontrado.\n")  # aqui a exceção é disparada com a mensagem de erro referente


def iniciaServidor():  # função que inicia o servidor
    # cria o socket para comunicação
    sock = socket.socket()

    # vincula a interface e porta para comunicacao
    sock.bind((HOST, PORTA))

    # define limite maximo de conexões pendentes e se coloca em modo de espera
    sock.listen(5)

    # configura o socket para modo não bloqueante
    sock.setblocking(False)

    # adiciona o socket na lista de entradas
    entradas.append(sock)

    # retorna o sock criado
    return sock


def aceitaConexao(sock):  # função que aceita novas conexões
    # aceita conexão com o próximo cliente
    clientSock, address = sock.accept()

    # uso do lock para não ocorrer problema de corrida
    lock.acquire()
    # adiciona o socket e endereco da nova conexao
    conexoes[clientSock] = address
    lock.release()

    # retorna o socket e endereco da nova conexao
    return clientSock, address


def recebeMensagem(clientSock, address):
    while True:  # roda em loop enquanto a mensagem de sair não for recebida
        # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
        msg = clientSock.recv(1024)  # argumento indica a qtde maxima de dados
        if not msg:  # encerra conexão com o cliente caso não recebe mensagem
            print("Encerrando conexão com o cliente {}\n".format(address))
            # uso do lock para evitar problema de corrida
            lock.acquire()
            del conexoes[clientSock]
            lock.release()
            clientSock.close()
            return
        msgDecodada = msg.decode("utf-8")  # faz a decodificação da mensagem de bytes para string
        if msgDecodada == "sair":  # encerra conexão com o cliente caso receba mensagem de encerramento da conexão
            print("Encerrando conexão com o cliente {a}\n".format(address))
            clientSock.close()
            return
        print("Recebida a mensagem: '{m}' do cliente {a}".format(m=msgDecodada, a=address))  # mostra a mensagem enviada pelo cliente
        respostaParaCliente = ""  # inicializa a variável que irá guardar a mensagem que será enviada para o cliente

        # nome do arquivo e a palavra que deseja ser contada são separadas, onde o nome do arquivo ficará na posição 0 e a palavra na posição 1
        conteudoMsg = (msgDecodada.split())  
        try:  # try usado para pegar a exceção disparada caso o arquivo não seja encontrado

            # chama a função de leitura para receber o conteúdo do arquivo, no formato de lista de strings, onde cada string é uma linha do texto
            conteudoArquivo = leitor(conteudoMsg[0])
            print("Cliente {} pediu para contar as ocorrências da palavra {} no arquivo {}".format(address, conteudoMsg[1], conteudoMsg[0]))
            
            # chama a função que retorna o número de ocorrências da palavra requisitada no arquivo
            ocorrenciasDaPalavra = contador(conteudoMsg[1], conteudoArquivo)
            
            # define a mensagem que será enviada para o cliente em caso de sucesso
            respostaParaCliente = ("A palavra buscada aparece {n} vezes no arquivo\n".format(n=ocorrenciasDaPalavra))
            print("Enviando resposta para o cliente {}".format(address))
        except Exception as error:  # aqui é onde a exceção disparada ao não encontrar o arquivo será tratada
            respostaParaCliente = str(error)  # a mensagem retornada ao cliente é definida como a mensagem de erro da exceção
        respostaEncoded = respostaParaCliente.encode("utf-8")  # codifica a mensagem para bytes para poder ser enviada para o cliente
        clientSock.send(respostaEncoded)  # envia para o cliente a mensagem final


def main():
    socket = iniciaServidor()
    clientes = []  # armazena os processos criados para fazer join
    print("Preparado para aceitar conexões")
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
                clientes.append(cliente)
            elif pronto == sys.stdin:
                msg = input()
                if msg == "sair":  # solicitação de finalização a partir do servidor
                    # apenas encerra quando não há clientes conectados
                    for client in clientes:
                        client.join()
                    socket.close()
                    sys.exit()
                # comando para mostrar conexões do servidor
                elif msg == "hist":
                    print(str(conexoes.values()))


main()
