import sqlite3 as sql
import os
from queue import Queue

class Database:
    def __init__(self, file_name)
        self.file_name = file_name
        self.to_write = Queue()
        self.to_read = Queue()
        
        self.setup_db(file_name)
        
    def setup_db(self, force=False):
        #If the database already exists, don't do anything unless force = True
        
        if os.path.isfile(self.file_name) and not force:
            self.conn = self.conn or sql.connect(self.file_name)
            return
        
        if force:
            os.remove(file_name)
        
        self.conn = sql.connect(file_name)
        
        #Setup the database
        #self.conn.execute("CREATE TABLES")
        