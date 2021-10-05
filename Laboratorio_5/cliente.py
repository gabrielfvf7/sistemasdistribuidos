import rpyc
from select import select
import sys
SERVIDOR = 'localhost'
PORTA = 10001

entradas = [sys.stdin]
def mostraMenu():
	print("\nComandos disponíveis:")
	print("/inscreve: Para se inscrever em um topico")
	print("/envia: Para enviar mensagem a um topico")
	print("/sair: Para encerrar o programa")
	print("/help: Para mostrar novamente o menu de comandos")
	print("------------------------------------------------------\n")
class cliente(rpyc.Service):
	# executa quando uma conexao eh criada
	def on_connect(self, conn):
		print("Conectado com sucesso.")
		mostraMenu()

def iniciaConexao():
	conn = rpyc.connect(SERVIDOR, PORTA, config={"allow_all_attrs": True},service = cliente)
	entradas.append(conn)
	return conn

def fazRequisicoes(conn):
	while True:
		leitura, _, _ = select(entradas, [], [])
		for pronto in leitura:
			if pronto == sys.stdin:
				msg = input()
				if msg == '/help':
					mostraMenu()
				elif msg == '/sair':
					conn.root.desconectar(conn)
					return
				elif msg == '/inscreve':
					topico = input("Digite o topico para se inscrever: ")
					ret = conn.root.inscreve(topico, myPrint, conn)
					print(ret)
				elif msg == '/envia':
					topico = input("Digite o topico para publicar o anúncio: ")
					msg = input('Digite o conteúdo do anúncio: ')
					ret = conn.root.echo(msg, topico)
					print('{}\n'.format(ret))

def myPrint(message):
	print(message)

def main():
	conn = iniciaConexao()
	bg = rpyc.BgServingThread(conn)
	fazRequisicoes(conn)
	bg.stop()

if __name__ == "__main__":
	main()