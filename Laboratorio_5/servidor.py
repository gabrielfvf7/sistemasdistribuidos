import rpyc
from rpyc.utils.server import ThreadedServer 
PORTA = 10001

lista_topicos = {}
historico_mensagens = {}

class Echo(rpyc.Service):
    def on_connect(self, conn):
        print("Conexao iniciada: {}".format(conn))
    def on_disconnect(self, conn):           
        print("Conexao finalizada: {}".format(conn))

    def exposed_desconectar(self, conn):
        for topico in lista_topicos:
            if (conn in lista_topicos[topico]):
                del lista_topicos[topico][conn]
        return

    def exposed_echo(self, msg, topico):
        ret = self.envia_mensagem(msg, topico)
        return ret
        
    def exposed_inscreve(self, topico, myPrint, conn):
        if topico in lista_topicos:
            if conn in lista_topicos[topico]:
                return 'Você já se inscreveu neste tópico'
            else:
                lista_topicos[topico][conn] = myPrint
        else:
            lista_topicos[topico] = {conn: myPrint}
        if topico in historico_mensagens:
            myPrint('Inscrito com sucesso!\n')
            myPrint('Este tópico já continha as seguintes mensagens:')
            for mensagem in historico_mensagens[topico]:
                myPrint(mensagem)
            return '\n--Fim das mensagens--\n'
        return 'Inscrito com sucesso!\n'
    
    def envia_mensagem(self, msg, topico):
        if topico in lista_topicos:
            if len(lista_topicos[topico]) > 0:
                for conn in lista_topicos[topico]:
                    lista_topicos[topico][conn]('Nova mensagem no tópico {}:\n{}'.format(topico, msg))
                    if topico in historico_mensagens:
                        historico_mensagens[topico].append(msg)
                    else:
                        historico_mensagens[topico] = [msg]
                return 'Envio feito com sucesso!'
            else:
                if topico in historico_mensagens:
                        historico_mensagens[topico].append(msg)
                else:
                    historico_mensagens[topico] = [msg]
                return '\nNão há clientes inscritos neste tópico, mas eles receberão a mensagem assim que se inscreverem'
        else:
            lista_topicos[topico] = {}
            historico_mensagens[topico] = [msg]
            return 'Este tópico não existia e foi criado.\nClientes que se inscreverem nele, receberão sua mensagem!'

if __name__ == "__main__":
	srv = ThreadedServer(Echo(), port = PORTA, protocol_config = {"allow_public_attrs" : True})
	srv.start()
