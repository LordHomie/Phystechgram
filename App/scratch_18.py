import sqlite3

conn = sqlite3.connect("clientdatabase.db")
conn.execute("PRAGMA foreign_keys = 1")
cur = conn.cursor()

# Create 2 tables if they don't exist: Clients and Work_Done
cur.execute('''CREATE TABLE IF NOT EXISTS Clients
(CID INTEGER PRIMARY KEY,
First_Name  TEXT    NOT NULL,
Active_Status   TEXT    NOT NULL)''')

cur.execute('''CREATE TABLE IF NOT EXISTS Work_Done
(ID INTEGER PRIMARY KEY,
Work_Done       TEXT    NOT NULL,
CID             INT,
FOREIGN KEY (CID) REFERENCES CLIENTS (CID))''')
conn.commit()
