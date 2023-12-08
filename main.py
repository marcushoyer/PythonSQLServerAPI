'''
    Rio, 08/12/2023 Código 100% funcional.
'''

from flask import Flask, request, jsonify
import pymssql
import pyodbc
from datetime import datetime

app = Flask(__name__)


# Substitua as informações de conexão com as suas
server_name = 'NOTECOREI5\SQLEXPRESS'
database_name = 'Cadastro'

## Configurações do banco de dados
dsn = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_name};DATABASE={database_name};Trusted_Connection=yes;'
db_config_odbc = {
    'dsn': dsn,
}

# Classe para gerenciar a conexão ao banco de dados
class DBManager:
    def __init__(self):
        #self.conn = pymssql.connect(**db_config)
        # Conectar ao banco de dados usando autenticação do Windows
        self.conn = pyodbc.connect(dsn)

    def execute_query(self, query, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

# Classe base para recursos (tabelas)
class Resource:
    def __init__(self, table_name, id_column='ID'):
        self.table_name = table_name
        self.id_column = id_column

    def get_all(self):
        try:
            db_manager = DBManager()
            cursor = db_manager.execute_query(f'SELECT * FROM {self.table_name}')
            rows = cursor.fetchall()

            resources = []
            for row in rows:
                resource = {self.id_column: row[0]}
                for i in range(1, len(row)):
                    resource[cursor.description[i][0]] = row[i]
                resources.append(resource)

            db_manager.close()
            return jsonify({f'{self.table_name.lower()}': resources})

        except Exception as e:
            return jsonify({'error': str(e)})

    def add(self, data):
        try:

            db_manager = DBManager()

            # Garanta que a ordem das colunas na consulta corresponda à ordem dos dados
            columns = ', '.join(data.keys())
            values = ', '.join(['?' for _ in range(len(data))])  # Use ? como marcador de parâmetro

            query = f'INSERT INTO {self.table_name} ({columns}) VALUES ({values})'

            # Passe os valores diretamente como uma lista
            db_manager.execute_query(query, list(data.values()))
            db_manager.commit()
            db_manager.close()

            return jsonify({'message': f'{self.table_name} adicionado com sucesso'})

        except Exception as e:
            return jsonify({'error': str(e)})

    '''

    Exemplo de requisição para teste no Power Shell do Windows.

    $data = @{
        'Nome' = 'Caneta Vermelha'
        'DataAlteracao' = '20231208'
    }

    Invoke-RestMethod -Uri http://localhost:5000/api/produtos -Method Post -Headers @{"Content-Type"="application/json"} -Body ($data | ConvertTo-Json)

    '''



# Classe específica para a tabela Produtos
class ProdutosResource(Resource):
    def __init__(self):
        super().__init__('Produtos')

    '''
    # Dados a serem atualizados
    $data = @{
        'Nome' = 'NovoNome'
        'DataAlteracao' = '20231209'
    }

    # ID do registro a ser atualizado
    $id = 4

    # URL da API para a atualização do produto com ID=4
    $url = "http://localhost:5000/api/produtos/$id"

    # Faz a chamada para a atualização usando o método PUT
    Invoke-RestMethod -Uri $url -Method Put -Headers @{"Content-Type"="application/json"} -Body ($data | ConvertTo-Json)

    '''

    def update(self, id, data):
        try:
            db_manager = DBManager()

            # Crie a parte SET da consulta de atualização
            update_values = ', '.join([f"{key} = ?" for key in data.keys()])

            query = f'UPDATE {self.table_name} SET {update_values} WHERE {self.id_column} = ?'

            # Passe os valores diretamente como uma lista, incluindo o valor da condição WHERE (ID)
            db_manager.execute_query(query, list(data.values()) + [id])
            db_manager.commit()
            db_manager.close()

            return jsonify({'message': f'{self.table_name} atualizado com sucesso'})

        except Exception as e:
            return jsonify({'error': str(e)})



    def delete(self, id):
        try:
            db_manager = DBManager()

            query = f'DELETE FROM {self.table_name} WHERE {self.id_column} = ?'

            # Passe o valor da condição WHERE (ID)
            db_manager.execute_query(query, [id])
            db_manager.commit()
            db_manager.close()

            return jsonify({'message': f'{self.table_name} excluído com sucesso'})

        except Exception as e:
            return jsonify({'error': str(e)})

'''
# ID do registro a ser excluído
$id = 5

# URL da API para a exclusão do produto com ID=5
$url = "http://localhost:5000/api/produtos/$id"

# Faz a chamada para a exclusão usando o método DELETE
Invoke-RestMethod -Uri $url -Method Delete

'''
# Rota para obter todos os produtos
@app.route('/api/produtos', methods=['GET'])
def get_produtos():
    produtos_resource = ProdutosResource()
    return produtos_resource.get_all()

# Rota para adicionar um novo produto
@app.route('/api/produtos', methods=['POST'])
def add_produto():
    data = request.get_json()
    produtos_resource = ProdutosResource()
    return produtos_resource.add(data)

# Rota para atualizar um produto existente
@app.route('/api/produtos/<int:id>', methods=['PUT'])
def update_produto(id):
    data = request.get_json()
    produtos_resource = ProdutosResource()
    return produtos_resource.update(id, data)


# Rota para excluir um produto
@app.route('/api/produtos/<int:id>', methods=['DELETE'])
def delete_produto(id):
    produtos_resource = ProdutosResource()
    return produtos_resource.delete(id)


# Execute o servidor Flask
if __name__ == '__main__':
    app.run(debug=True)
