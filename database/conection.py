import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',       # usuario de MySQL
        password='',       # contraseña de MySQL
        database='listasprecios' # El nombre de la BD
    )
    return connection