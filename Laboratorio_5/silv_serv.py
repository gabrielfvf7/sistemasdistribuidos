#Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Servidor de echo usando RPC 
import rpyc #modulo que oferece suporte a abstracao de RPC

#servidor que dispara um processo filho a cada conexao
from rpyc.utils.server import ThreadedServer 

# porta de escuta do servidor de echo
PORTA = 10001

lista_topicos = {}

# classe que implementa o servico de echo
class Echo(rpyc.Service):
	# executa quando uma conexao eh criada
    conexao = ''
    def on_connect(self, conn):
        self.conexao = conn
        print(conn)
        print("Conexao iniciada:")
    def on_disconnect(self, conn):
        print("Conexao finalizada:")
    def exposed_echo(self, msg):
        self.conexao.root.teste("Mensagem")
        return msg
  
def envia_mensagem(msg, topico):
    for conn in lista_topicos[topico]:
        conn.root.mostrarMsg(msg)

def inscreve(topico, conn):
    lista_topicos[topico].append(conn)

def processa_msg(msg):
    jsonTratado = json.loads(msg)
    tipo = jsonTratado["tipo"]
    conteudo = jsonTratado["conteudo"]
    topico_cliente = jsonTratado["topico"]    

# dispara o servidor
if __name__ == "__main__":
	srv = ThreadedServer(Echo, port = PORTA)
	srv.start()


### Tipos de servidores
#https://rpyc.readthedocs.io/en/latest/api/utils_server.html

#servidor que dispara uma nova thread a cada conexao
#from rpyc.utils.server import ThreadedServer

#servidor que atende uma conexao e termina
#from rpyc.utils.server import OneShotServer

### Configuracoes do protocolo RPC
#https://rpyc.readthedocs.io/en/latest/api/core_protocol.html#rpyc.core.protocol.DEFAULT_CONFIG