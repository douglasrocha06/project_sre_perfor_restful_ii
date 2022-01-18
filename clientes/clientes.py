from flask import Flask
from flask_httpauth import HTTPBasicAuth
from pymysql import cursors
from config import mysql
from flask import jsonify
from flask import request
import pymysql

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.route("/")
@auth.login_required
def index():
    return jsonify("API de Clientes.", {'Metodo':'GET','endpoint':'http://localhost:5003/api/v1/clientes','Mensagem':'Visualizar todos os clientes.'},{'Metodo':'GET','endpoint':'http://localhost:5003/api/v1/clientes/ID','Mensagem':'Visualizar um cliente especifico.'},{'Metodo':'GET','endpoint':'http://localhost:5003/api/v1/clientes/NOME','Mensagem':'Visualizar todos os clientes por determinado nome informado.'}, {'Metodo':'POST','endpoint':'http://localhost:5003/api/v1/clientes','Mensagem':'Adicionar um novo cliente.'})

@app.route('/api/v1/clientes', methods=['GET'])
@auth.login_required
def clientes_consultorio():
	try:
		conn = mysql.connect() 
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute(SQL_GET_CLIENTES)
		linha = cursor.fetchall()

		if not linha:
			mensagem = {
				'status': 404,
				'mensagem': 'Nao possui cliente cadastrado!'
			}
			return jsonify(mensagem), 404

		resposta = jsonify(linha)
		resposta.status_code = 200
		return resposta
	except Exception as e:
		return jsonify({"error":f"{e}"})
	finally:
		cursor.close() 
		conn.close()

@app.route('/api/v1/clientes/<int:id>', methods=['GET'])
@auth.login_required
def cliente_especifico(id):
	try:
		conn = mysql.connect() 
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute(SQL_GET_CLIENTE, id)
		linha = cursor.fetchone()

		if not linha:
			mensagem = {
				'status': 404,
				'mensagem': 'Cliente nao cadastrado!'
			}
			return jsonify(mensagem), 404

		resposta = jsonify(linha)
		return resposta
		
	except Exception as e:
		return jsonify({"error":f"{e}"})
	finally:
		cursor.close() 
		conn.close()

@app.route('/api/v1/clientes/<string:nome>')
@auth.login_required
def visualizar_clientes(nome):
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute(SQL_GET_CLIENTES_ESPECIFICO, (nome, "%"))
		linhas = cursor.fetchall()

		if not linhas:
			mensagem = {
				'status': 404,
				'mensagem': 'Cliente nao cadastrado!'
			}
			return jsonify(mensagem), 404
		
		resposta = jsonify(linhas)
		resposta.status_code = 200
		return resposta
	except Exception as e:
		return jsonify({"error":f"{e}"})
	finally:
		cursor.close()
		conn.close()

@app.route('/api/v1/clientes', methods=['POST'])
@auth.login_required
def cadastro_clientes():
	try:
		json = request.json
		nome = json['Nome']
		if nome and request.method == 'POST':
			dados = (nome)
			conn = mysql.connect()
			cursor = conn.cursor(pymysql.cursors.DictCursor)
			cursor.execute(SQL_POST_CLIENTES, dados)
			conn.commit()
			mensagem = {
				'status': 200,
				'mensagem': 'Cliente adicionado com sucesso!'
			}
			resposta = jsonify(mensagem)
			resposta.status_code = 200
			return resposta
		else:
			return not_found()
	except Exception as e:
		return jsonify({'error':f'{e}'})
	finally:
		cursor.close() 
		conn.close()

SQL_GET_CLIENTES = "select id_clientes_PK as ID, nome as Nome from clientes"
SQL_GET_CLIENTE = "select id_clientes_PK as ID, nome as Nome from clientes where id_clientes_PK = %s"
SQL_GET_CLIENTES_ESPECIFICO = "select  id_clientes_PK as ID, nome as Nome from clientes where nome like %s %s"
SQL_POST_CLIENTES = "insert into clientes values (default, %s)"

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
    app.run(debug=True, port=5003)