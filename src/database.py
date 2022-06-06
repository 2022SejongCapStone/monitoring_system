import sqlite3
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from src import directory as dt

class URLDataBase():

    def __init__(self, url):
        if url.startswith("http://"):
            url = url[7:]
        elif url.startswith("https://"):
            url = url[8:]
        self.url_ = url
        self.db_path_ = 'stock/'+ self.url_ +'db'
        self.sql_path_ = 'stock/'+ self.url_ +'db/dump.sql'
        dt.makeDir(self.db_path_)
        self.conn_ = sqlite3.connect(self.db_path_+'/cumulusdb.db')
        self.c_ = self.conn_.cursor()
        self.c_.execute("CREATE TABLE IF NOT EXISTS crawlinglist (url varchar)")
        self.conn_.commit()


    def close(self):
        self.dump()
        self.c_.close()
        self.conn_.close()


    def dump(self):
        with self.conn_:
            with open(self.sql_path_, 'w') as f:
                for line in self.conn_.iterdump():
                    f.write('%s\n' % line)
                print('Completed.')


    def insert(self, url):
        url_list = []
        url_list.append(url)
        self.c_.execute("INSERT INTO crawlinglist(url) VALUES(?)", url_list)
        self.conn_.commit()


    def select(self, url):
        url_list = []
        url_list.append(url)
        self.c_.execute("SELECT * FROM crawlinglist WHERE url = ?", url_list)
        return self.c_.fetchall()


    def isDataExist(self, url):
        result = self.select(url)
        if len(result) != 0:
            return True
        else:
            return False
