#Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Cliente de echo usando RPC
import rpyc #modulo que oferece suporte a abstracao de RPC
from select import select
import sys

# endereco do servidor de echo
SERVIDOR = 'localhost'
PORTA = 10001

entradas = [sys.stdin]

class cliente(rpyc.Service):
	# executa quando uma conexao eh criada
	def on_connect(self, conn):
		print("Conexao iniciada:")
	def teste(self, msg):
		print(msg)


def iniciaConexao():
	'''Conecta-se ao servidor.
	Saida: retorna a conexao criada.'''
	conn = rpyc.connect(SERVIDOR, PORTA, config={"allow_all_attrs": True},service = cliente)
	entradas.append(conn)
	
	print(type(conn.root)) # mostra que conn.root eh um stub de cliente
	print(conn.root.get_service_name()) # exibe o nome da classe (servico) oferecido

	return conn

def fazRequisicoes(conn):
	'''Faz requisicoes ao servidor e exibe o resultado.
	Entrada: conexao estabelecida com o servidor'''
	# le as mensagens do usuario ate ele digitar 'fim'
	print("Digite uma mensagem ('fim' para terminar):")
	while True:
		leitura, _, _ = select(entradas, [], [])
		for pronto in leitura:
			if pronto == sys.stdin:
				msg = input()
				if msg == 'fim':
					break
				if msg == 'inscreve':
					topico = input("Digite o topico para se inscrever: ")
					teste = conn.root.inscreve(topico, myPrint)
					print(teste)
				# envia a mensagem do usuario para o servidor
				elif msg == 'envia':
					topico = input("Digite o topico para publicar o anúncio: ")
					msg = input('Digite o conteúdo do anúncio: ')
					ret = conn.root.echo(msg, topico)
					print(ret)
					# imprime a mensagem recebida

	# encerra a conexao
	conn.close()

def myPrint(message):
	print(message)

def main():
	'''Funcao principal do cliente'''
	#inicia o cliente
	conn = iniciaConexao()
	bg = rpyc.BgServingThread(conn)
	#interage com o servidor ate encerrar
	fazRequisicoes(conn)
	bg.stop()

# executa o cliente
if __name__ == "__main__":
	main()