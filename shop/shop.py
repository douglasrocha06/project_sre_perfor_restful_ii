from flask import Flask
from flask_httpauth import HTTPBasicAuth
from pymysql import cursors
from config import mysql
from flask import jsonify
from flask import request
import pymysql
import requests

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.route("/")
@auth.login_required
def index():
	return jsonify("API DE SHOP.", {'Metodo':'GET','endpoint':'http://localhost:5000/api/v1/shop/id','Mensagem':'Visualizar um pedido especifico.'},{'Metodo':'POST','endpoint':'http://localhost:5000/api/v1/shop','Mensagem':'Adicionar um pedido.'}, "API DE CLIENTES.", {'Metodo':'GET','endpoint':'http://localhost:5003/api/v1/clientes','Mensagem':'Visualizar todos os clientes.'},{'Metodo':'GET','endpoint':'http://localhost:5003/api/v1/clientes/ID','Mensagem':'Visualizar um cliente especifico.'},{'Metodo':'GET','endpoint':'http://localhost:5003/api/v1/clientes/NOME','Mensagem':'Visualizar todos os clientes por determinado nome informado.'}, {'Metodo':'POST','endpoint':'http://localhost:5003/api/v1/clientes','Mensagem':'Adicionar um novo cliente.'}, "API DE PRODUTOS.", {'Metodo':'GET','endpoint':'http://localhost:5001/api/v1/produtos','Mensagem':'Visualizar todos os produtos.'},{'Metodo':'GET','endpoint':'http://localhost:5001/api/v1/produtos/ID','Mensagem':'Visualizar um produto especifico.'},{'Metodo':'GET','endpoint':'http://localhost:5001/api/v1/produtos/NOME','Mensagem':'Visualizar todos os produtos com determinado nome.'}, {'Metodo':'POST','endpoint':'http://localhost:5001/api/v1/produtos','Mensagem':'Adicionar um novo produto.'}, "API DE PEDIDOS.", {'Metodo':'GET','endpoint':'http://localhost:5002/api/v1/pedidos/id','Mensagem':'Visualizar todos os produtos que um cliente adquiriu.'}, {'Metodo':'POST','endpoint':'http://localhost:5002/api/v1/pedidos','Mensagem':'Adicionar um novo pedido.'})

@app.route('/api/v1/shop/<int:id>', methods=['GET'])
@auth.login_required
def shop_consultorio(id):
	try:
		conn = mysql.connect() 
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute(SQL_GET_SHOP, id)
		linha = cursor.fetchall()

		clientes = [] 
		lista_clientes = []
		for i in (linha):
			if i not in lista_clientes:
				id_cliente = i['ID cliente']
				lista_clientes.append(id_cliente)
				request_cliente = requests.get(url = f'http://127.0.0.1:5003/api/v1/clientes/{id_cliente}', headers = {'Authorization':'Basic ZG91Z2xhczoxMjM='})
				clientes.append(request_cliente.json())

		catalogo = [] 
		produtos = []
		for i in (linha):
			if i not in produtos:
				id_produtos = i['ID produtos']
				produtos.append(id_produtos)
				request_produtos = requests.get(url = f'http://127.0.0.1:5001/api/v1/produtos/{id_produtos}', headers = {'Authorization':'Basic ZG91Z2xhczoxMjM='})
				catalogo.append(request_produtos.json())

		if catalogo and produtos:
			return jsonify(f'Pedido: {id}', clientes, catalogo), 200

		else:
			mensagem = {
				'status': 404,
				'mensagem': 'Nao possui pedido cadastrado!'
			}
			return jsonify(mensagem), 404
		
	except Exception as e:
		return jsonify({"error":f"{e}"})
	finally:
		cursor.close() 
		conn.close()

#Adicionando um registro 
@app.route('/api/v1/shop', methods=['POST'])
@auth.login_required
def cadastrar_pedido():
    try:
        json = request.json
        id_clientes_FK = json['ID cliente']
        id_produtos_FK = json['ID produto']
        if id_clientes_FK and id_produtos_FK and request.method == 'POST':
            dados = (id_clientes_FK, id_produtos_FK)
            conn = mysql.connect()
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            request_cliente = requests.get(url = f'http://127.0.0.1:5003/api/v1/clientes/{id_clientes_FK}', headers = {'Authorization':'Basic ZG91Z2xhczoxMjM='})
            request_produto = requests.get(url = f'http://127.0.0.1:5001/api/v1/produtos/{id_produtos_FK}', headers = {'Authorization':'Basic ZG91Z2xhczoxMjM='})

            if request_cliente.status_code == 404:
                return jsonify({'status':'404', 'descricao':'Cliente inexistente.',}), 404
            elif request_produto.status_code == 404:
                return jsonify({'status':'404','descricao':'Produto inexistente.'}), 404

            cursor.execute(SQL_POST_PEDIDOS, dados)
            conn.commit()
            resposta = jsonify({'status':'404','descricao':'Compra cadastrada com sucesso!'})
            resposta.status_code = 200
            return resposta
        else:
            return not_found
    except Exception as e:
        return jsonify({"error":f"{e}"})
    finally:
        cursor.close()
        conn.close()

SQL_POST_PEDIDOS = "insert into pedidos values(default, %s, %s)"
SQL_GET_SHOP = "select id_pedidos_PK as ID,id_clientes_FK as 'ID cliente',id_produtos_FK as 'ID produtos' from pedidos where id_pedidos_PK = %s order by id_produtos_FK"

#Caso não encontre o caminho
@app.errorhandler(404)
def not_found(error=None):
    messagem = {
        'status': 404,
        'mensagem': 'Pagina nao encontrada: ' + request.url,
    }
    respone = jsonify(messagem)
    respone.status_code = 404
    return respone

#Método do Basic Authentication
@auth.verify_password
def verificacao(login, senha):
	usuarios= {
			'douglas':'123',
	}
	if not (login, senha):
		return False
	return usuarios.get(login) == senha

if __name__ == "__main__":
    app.run(debug=True, port=5000)