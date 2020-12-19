import sqlite3
from prettytable import from_db_cursor

# Good for testing, so I don't have to keep on deleting db 
conn = sqlite3.connect(':memory:')

# Connect to database
# conn = sqlite3.connect('customer.db')

# Create a cursor
c = conn.cursor()

# Create a table
c.execute('''\
CREATE TABLE customers (
    first_name text,
    last_name text,
    email_address text
)
''')

'''
DATATYPES: 
    - NULL
    - INTEGER
    - REAL
    - TEXT
    - BLOB
'''

# Inserting one row
c.execute("INSERT INTO customers VALUES ('Mary', 'Brown', 'mary@gmail.com')")

# Inserting multiple rows
many_customers = [
    ('Wes', 'Brown', 'wes@brown.com'),
    ('Steph', 'Kuewa', 'septh@kuewa.com'),
    ('Dan', 'Pas', 'dan@pas.com')
]

c.executemany("INSERT INTO customers VALUES (?, ?, ?)", many_customers)

# Outputting database
c.execute('SELECT rowid, * FROM customers')

# Could also use fetchmany, fetchall, fetchone
mytable = from_db_cursor(c)
print(mytable)

# Commit our cmd
conn.commit()

# Close our connection
conn.close()
