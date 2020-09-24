import sqlite3

conn = sqlite3.connect("clientdatabase.db")
conn.execute("PRAGMA foreign_keys = 1")
cur = conn.cursor()

# cur.execute("DROP TABLE IF EXISTS Clients")
# cur.execute("DROP TABLE IF EXISTS Work_Done")

# Create 2 tables if they don't exist: Clients and Work_Done
# cur.execute('''CREATE TABLE IF NOT EXISTS Clients
# (CID INTEGER PRIMARY KEY,
# First_Name  TEXT    NOT NULL)''')
#
cur.execute('''CREATE TABLE IF NOT EXISTS Work_Done
(ID INTEGER PRIMARY KEY,
Work_Done       TEXT    NOT NULL,
CID             INT,
FOREIGN KEY (CID) REFERENCES CLIENTS (CID))''')
conn.commit()


cur.execute("""INSERT INTO Clients (CID, First_Name) VALUES (3, "ahmed")""")
cur.execute("""INSERT INTO Work_Done (ID, Work_Done, CID) VALUES (2, "yees", 3)""")

conn.commit()
