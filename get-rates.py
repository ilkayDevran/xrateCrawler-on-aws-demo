# -*- coding: UTF-8 -*-

import pymysql
import json

class Database():
    '''
    Class for interacting with sqlite3 database and basic methods.
    '''
    def __init__(self):
        self.set_connection()

    def set_connection(self):
        with open('config.json', 'r') as f:
            data=f.read()
        f.close()
        obj = json.loads(data)
        
        self.conn = pymysql.connect(
                host = obj['MySQL']['HOST']
                , user = obj['MySQL']['USERNAME']
                , passwd = obj['MySQL']['PASSWORD']
                , db = obj['MySQL']['DATABASE']
                , charset='utf8')
        self.cur = self.conn.cursor()

    def execute(self, command):
        self.cur.execute(command)
    
    def fetch_all(self):
        return self.cur.fetchall()
    
    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    
def lambda_handler(event, context):
    select_query = ("""SELECT USDolar, Euro FROM xratesCrawlerDB.TRYRATES WHERE Name = '{}' """).format(event['YourName'])
    db = Database()
    db.execute(select_query)
    results = {'results': db.fetch_all()}
    print results
    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
