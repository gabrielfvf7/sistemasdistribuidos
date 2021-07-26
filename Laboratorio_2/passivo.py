import socket

def formataTexto(texto): # função auxiliar usada para retirar alguns sinais de pontuação das palavras, que poderiam atrapalhar a contagem
    return texto.replace('?', '').replace(',', '').replace('.', '').replace('!', '')

def contador(palavraParaContar, texto): # função usada para contar o número de ocorrências de uma dada palavra em um arquivo
    ocorrencias = 0 # inicializa a variável responsável por armazenar o valor de ocorrências da palavra
    for linha in texto: # loop que itera por cada linha do texto
        for palavra in linha.split(): # loop que itera por cada palavra do texto, o split é usado para separar a linha em palavras
            palavraFormatada = formataTexto(palavra) # chama a função auxiliar para retirada de pontuação
            if palavraFormatada == palavraParaContar: # verifica se a palavra atual é igual à palavra buscada
                ocorrencias += 1 # caso as palavras sejam iguais, incrementa a quantidade de ocorrências
    return ocorrencias


def leitor(fileToRead): # função auxiliar para realizar a leitura do arquivo
    try: # a função open é envolta dentro de um try para poder tratar o erro de arquivo não encontrado
        with open(fileToRead, "r") as foundFile: # abre o arquivo em modo de leitura
            return foundFile.readlines() # retorna as linhas do arquivo como uma lista
    except FileNotFoundError: # caso o arquivo não seja encontrado, a função open dispara a exceção FileNotFoundError
        raise Exception("O arquivo solicitado não foi encontrado.\n") # aqui a exceção é disparada com a mensagem de erro referente


def servidor():
    HOST = ""  # '' possibilita acessar qualquer endereco alcancavel da maquina local
    PORTA = 6000  # porta onde chegarao as mensagens para essa aplicacao

    # cria um socket para comunicacao
    sock = socket.socket()  # valores default: socket.AF_INET, socket.SOCK_STREAM

    # vincula a interface e porta para comunicacao
    sock.bind((HOST, PORTA))

    # define o limite maximo de conexoes pendentes e coloca-se em modo de espera por conexao
    sock.listen(1)

    # aceita a primeira conexao da fila (chamada pode ser BLOQUEANTE)
    while True:
        (
            novoSock,
            endereco,
        ) = sock.accept()  # retorna um novo socket e o endereco do par conectado
        print("Conectado com: ", endereco)

        while True:  # roda em loop enquanto a mensagem de sair não for recebida
            # depois de conectar-se, espera uma mensagem (chamada pode ser BLOQUEANTE))
            msg = novoSock.recv(1024)  # argumento indica a qtde maxima de dados
            if not msg: # encerra conexão com o cliente caso não recebe mensagem
                print("Encerrando conexão com o cliente\n")
                break
            msgDecodada = msg.decode(
                "utf-8"
            )  # faz a decodificação da mensagem de bytes para string
            if msgDecodada == "sair": # encerra conexão com o cliente caso receba mensagem de encerramento da conexão
                print("Encerrando conexão com o cliente\n")
                break
            print(
                "Recebida a mensagem:", msgDecodada
            )  # mostra a mensagem enviada pelo cliente
            respostaParaCliente = "" # inicializa a variável que irá guardar a mensagem que será enviada para o cliente
            conteudoMsg = msgDecodada.split() # nome do arquivo e a palavra que deseja ser contada são separadas, onde o nome do arquivo ficará na posição 0 e a palavra na posição 1
            try: # try usado para pegar a exceção disparada caso o arquivo não seja encontrado
                conteudoArquivo = leitor(conteudoMsg[0]) # chama a função de leitura para receber o conteúdo do arquivo, no formato de lista de strings, onde cada string é uma linha do texto
                ocorrenciasDaPalavra = contador(conteudoMsg[1], conteudoArquivo) # chama a função que retorna o número de ocorrências da palavra requisitada no arquivo
                respostaParaCliente = (
                    "A palavra buscada aparece {n} vezes no arquivo\n".format(
                        n=ocorrenciasDaPalavra
                    )
                ) # define a mensagem que será enviada para o cliente em caso de sucesso
            except Exception as error: # aqui é onde a exceção disparada ao não encontrar o arquivo será tratada
                respostaParaCliente = str(error) # a mensagem retornada ao cliente é definida como a mensagem de erro da exceção
            respostaEncoded = respostaParaCliente.encode("utf-8") # codifica a mensagem para bytes para poder ser enviada para o cliente
            novoSock.send(respostaEncoded)  # envia para o cliente a mensagem final

        # fecha o socket da conexao
        novoSock.close()

    # fecha o socket principal
    sock.close()

servidor() # chama a função principal da aplicação servidor
