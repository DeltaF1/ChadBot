import sqlite3 as sql
import os
from queue import Queue

class Database:
    def __init__(self, file_name):
        self.file_name = file_name
        self.to_write = Queue()
        self.to_read = Queue()
        
        self.setup_db(file_name, force=False)
        
    def setup_db(self, file_name, force=False):
        #If the database already exists, don't do anything unless force = True
        
        if os.path.isfile(file_name) and not force:
            self.conn = sql.connect(self.file_name, check_same_thread=False)
            return
        
        if force:
            os.remove(file_name)
        
        self.conn = sql.connect(file_name, check_same_thread=False)
        
        #Setup the database
        self.conn.execute("CREATE TABLE timeouts (thread_id int, timeout_type varchar(4), ts int);")
    
    def get_timeout(self, thread_id, type):
        c = self.conn.cursor()
        c.execute("SELECT ts FROM timeouts WHERE thread_id=? and timeout_type=?", (thread_id, type))
        return c.fetchone() or 0
    
    def set_timeout(self, thread_id, type, ts):
        c = self.conn.cursor()
        c.execute("INSERT OR REPLACE INTO timeouts ()WHERE thread_id=? and timeout_type=?", (ts, thread_id, type))
        self.conn.commit()
        