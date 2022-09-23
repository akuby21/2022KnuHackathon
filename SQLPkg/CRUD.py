from pprint import pprint
import psycopg2

class Landmark_CRUD():
    # This is PostgreSQL CRUD (create, update, update, delete) for only localhost
    def __init__(self, dbname):
        self.connect = psycopg2.connect(host='localhost', port=5432, dbname= dbname)
        self.cursor = self.connect.cursor()
    
    def __del__(self):
        self.connect.close()
        self.cursor.close()
    
    def execute(self, query):
        self.cursor.execute(query)
        pprint(self.cursor.fetchall())
        self.commit()

    def commit(self):
        self.connect.commit()
    
    def insert(self, schema, table, *args):
        # args: id name contents homepage tel hour address coordinate
        if len(args) != 8 :
            print("Invalid Arguments")
        else:
            value = "'" + "','".join(args[:-1]) + "', array" + args[-1]

            query = f'insert into {schema}.{table} (id, name, contents, homepage, tel, hour, address, coordinate) values({value}) on conflict(id) do nothing'
            try:
                self.execute(query)
            except psycopg2.DatabaseError as error:
                print(error)
    
    def read(self, schema, table, *columns):
        col = ', '.join(columns)
        query = f'select {col} from {schema}.{table}'
        try:
            self.execute(query)
        except psycopg2.DatabaseError as error:
            print(error)

    def delete(self, schema, table, target_id):
        query = f'delete from {schema}.{table} where id = {target_id}'
        try:
            self.execute(query)
        except psycopg2.DatabaseError as error:
            print(error)
    