#Ver documentação em: https://rpyc.readthedocs.io/en/latest/

# Servidor de echo usando RPC 
import rpyc #modulo que oferece suporte a abstracao de RPC
#servidor que dispara um processo filho a cada conexao
from rpyc.utils.server import ThreadedServer 

from threading import RLock
# porta de escuta do servidor de echo
PORTA = 10001

broadcast_lock = RLock()
lista_topicos = {}

# classe que implementa o servico de echo
class Echo(rpyc.Service):
	# executa quando uma conexao eh criada
    conexao = ''
    def on_connect(self, conn):
        self.conexao = conn
        print("Conexao iniciada: ")
    def on_disconnect(self, conn):
        global lista_topicos
        for topico in lista_topicos:
            for connection in topico:
                if conn == connection:
                    topico.remove(conn)
        print("Conexao finalizada: ")
    def exposed_echo(self, msg, topico):
        ret = self.envia_mensagem(msg, topico)
        return ret
        
    def exposed_inscreve(self, topico, myPrint):
        global lista_topicos
        if topico in lista_topicos:
            lista_topicos[topico].append(myPrint)
        else:
            lista_topicos[topico] = [myPrint]
        return 'Inscrito com sucesso'
    
    def envia_mensagem(self, msg, topico):
        global lista_topicos
        with broadcast_lock:
            if topico in lista_topicos:
                if len(lista_topicos[topico]) > 0:
                    for myPrint in lista_topicos[topico]:
                        myPrint(msg)
                    return 'Envio feito com sucesso!'
                else:
                    print('entrou no else')
                    return 'Não há clientes inscritos neste tópico!'
            else:
                lista_topicos[topico] = []
                return 'Este tópico não existia e foi criado!'
  



def processa_msg(msg):
    jsonTratado = json.loads(msg)
    tipo = jsonTratado["tipo"]
    conteudo = jsonTratado["conteudo"]
    topico_cliente = jsonTratado["topico"]    

# dispara o servidor
if __name__ == "__main__":
	srv = ThreadedServer(Echo(), port = PORTA, protocol_config = {"allow_public_attrs" : True})
	srv.start()


### Tipos de servidores
#https://rpyc.readthedocs.io/en/latest/api/utils_server.html

#servidor que dispara uma nova thread a cada conexao
#from rpyc.utils.server import ThreadedServer

#servidor que atende uma conexao e termina
#from rpyc.utils.server import OneShotServer

### Configuracoes do protocolo RPC
#https://rpyc.readthedocs.io/en/latest/api/core_protocol.html#rpyc.core.protocol.DEFAULT_CONFIG