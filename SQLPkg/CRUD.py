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
    
    def execute(self, query, isFetch):
        self.cursor.execute(query)
        if isFetch:
            return self.cursor.fetchall()
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
                self.execute(query, False)
            except psycopg2.DatabaseError as error:
                print(error)

    
    def read(self, schema, table, *columns):
        col = ', '.join(columns)
        query = f'select {col} from {schema}.{table}'

        try:
            return self.execute(query, True)
        except psycopg2.DatabaseError as error:
            print(error)

    def delete_byID(self, schema, table, target_id):
        query = f'delete from {schema}.{table} where id = {target_id}'
        query = f'WITH to_delete AS ( select id from {schema}.{table} where id = {target_id} ) delete from {schema}.{table} using to_delete where {schema}.{table}.id = to_delete.id and not to_delete.id is null'
        print(query)
        try:
            self.execute(query, False)
        except psycopg2.DatabaseError as error:
            print(error)
    