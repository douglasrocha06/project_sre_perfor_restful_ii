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
    return jsonify("API de Produtos.", {'Metodo':'GET','endpoint':'http://localhost:5001/api/v1/produtos','Mensagem':'Visualizar todos os produtos.'},{'Metodo':'GET','endpoint':'http://localhost:5001/api/v1/produtos/ID','Mensagem':'Visualizar um produto especifico.'},{'Metodo':'GET','endpoint':'http://localhost:5001/api/v1/produtos/NOME','Mensagem':'Visualizar todos os produtos com determinado nome.'}, {'Metodo':'POST','endpoint':'http://localhost:5001/api/v1/produtos','Mensagem':'Adicionar um novo produto.'})

@app.route('/api/v1/produtos', methods=['GET'])
@auth.login_required
def produtos_consultorio():
	try:
		conn = mysql.connect() 
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute(SQL_GET_PRODUTOS)
		linha = cursor.fetchall()
		
		if not linha:
			mensagem = {
				'status': 404,
				'mensagem': 'Nao possui produtos cadastrado!'
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

@app.route('/api/v1/produtos/<int:id>', methods=['GET'])
@auth.login_required
def produto_especifico(id):
	try:
		conn = mysql.connect() 
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute(SQL_GET_PRODUTO, id)
		linha = cursor.fetchone()

		if not linha:
			mensagem = {
				'status': 404,
				'mensagem': 'Produto nao cadastrado!'
			}
			return jsonify(mensagem), 404

		resposta = jsonify(linha)
		return resposta
		
	except Exception as e:
		return jsonify({"error":f"{e}"})
	finally:
		cursor.close() 
		conn.close()

@app.route('/api/v1/produtos/<string:nome>')
@auth.login_required
def visualizar_produtos(nome):
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute(SQL_GET_PRODUTOS_ESPECIFICO, (nome, "%"))
		linhas = cursor.fetchall()

		if not linhas:
			mensagem = {
				'status': 404,
				'mensagem': 'Produto nao cadastrado!'
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

@app.route('/api/v1/produtos', methods=['POST'])
@auth.login_required
def cadastro_produtos():
	try:
		json = request.json
		produto = json['Produto']
		if produto and request.method == 'POST':
			dados = (produto)
			conn = mysql.connect()
			cursor = conn.cursor(pymysql.cursors.DictCursor)
			cursor.execute(SQL_POST_PRODUTOS, dados)
			conn.commit()
			mensagem = {
				'status': 200,
				'mensagem': 'Produto adicionado com sucesso!'
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

SQL_GET_PRODUTOS = "select id_produtos_PK as ID,descricao as Produto from produtos"
SQL_GET_PRODUTO = "select id_produtos_PK as ID,descricao as Produto from produtos where id_produtos_PK = %s order by id_produtos_PK"
SQL_GET_PRODUTOS_ESPECIFICO = "select id_produtos_PK as ID,descricao as Produto from produtos where descricao like %s %s"
SQL_POST_PRODUTOS = "insert into produtos values (default, %s)"

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
    app.run(debug=True, port=5001)