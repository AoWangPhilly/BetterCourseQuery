import sqlite3

conn = sqlite3.connect('classes.db')

c = conn.cursor()

c.execute('''CREATE TABLE classes (
    
    )''')