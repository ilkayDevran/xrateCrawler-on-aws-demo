# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta, date
from bs4 import BeautifulSoup
import requests 
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
    
    def fetchall(self):
        return self.cur.fetchall()
    
    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

class xratesCrawler:
    def __init__(self):
        self.db = Database()

    def run(self, yourName):
        data = self.get_rates()
        insert_query = ("""INSERT INTO `xratesCrawlerDB`.`TRYRATES`
                            (`Name`, `USDolar`, `Euro`, `InsertDate`)
                            VALUES
                            ('{}', {}, {}, NOW());""").format(yourName, data[1][2], data[2][2])
        self.db.execute(insert_query)
        self.db.commit()
        self.db.close()

    def send_request(self, url):
        s = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        } 
        try:  
            return s.get(url, headers=headers)
        except Exception:
            print ('ERROR:(SEND REQUEST METHOD)\n' + url)
            return None
    
    def get_rates(self):
        baseURL = "http://x-rates.com/historical/?from=TRY&amount=1&date="  # Add date in format 2019-08-05
        url = baseURL + date.today().strftime("%Y-%m-%d") 
        
        response = self.send_request(url)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', attrs={'class':'ratesTable'})    # Get Rate Table from HTML
        rows = table.find_all('tr')
        
        data = []
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])

        return data

def lambda_handler(event, context):
    yourName = '' # Edit here as your name with lowercase and english characters
    crawler = xratesCrawler()
    crawler.run(yourName)
