import sqlite3 as sql
import os
from queue import Queue

class Database:
    def __init__(self, file_name):
        self.file_name = file_name
        self.to_write = Queue()
        #self.to_read = Queue()
        
        self.setup_db(file_name, force=False)
        
    def setup_db(self, file_name, force=False):
        
        #If force is true, remove the entire database
        if force:
            os.remove(file_name)
        
        self.conn = sql.connect(file_name, check_same_thread=False)
        
        #Setup the database
        self.conn.execute("CREATE TABLE IF NOT EXISTS timeouts (thread_id int, timeout_type varchar(4), ts int, PRIMARY KEY (thread_id, timeout_type));")
        self.conn.execute("CREATE TABLE IF NOT EXISTS custom_chads (virgin string PRIMARY KEY, chad string);")
    
    def get_timeout(self, thread_id, type):
        c = self.conn.cursor()
        c.execute("SELECT ts FROM timeouts WHERE thread_id=? and timeout_type=?", (thread_id, type))

        ts = c.fetchone()
        
        try:
            ts = ts[0]
        except TypeError:
            ts = 0
        
        return ts
    
    def get_chad(self, virgin):
        c = self.conn.cursor()       
        c.execute("SELECT chad FROM custom_chads WHERE virgin = ?", (virgin,))
        
        chad = c.fetchone()
        
        try:
            chad = chad[0]
        except TypeError:
            chad = None
        
        return chad
        
    def set_chad(self, virgin, chad):
        self.to_write.put(("INSERT OR REPLACE INTO custom_chads (virgin, chad) values (?,?)", (virgin, chad)))
    
    def set_timeout(self, thread_id, type, ts):
        self.to_write.put(("INSERT OR REPLACE INTO timeouts (thread_id, timeout_type, ts) values (?,?,?)", (thread_id, type, ts)))
        
    
    def loop(self):
        while True:
            to_write = self.to_write.get()
            
            try:
                self.conn.execute(to_write[0], to_write[1])
            
                self.conn.commit()
            except Exception as e:
                print(e)