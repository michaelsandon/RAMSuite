# Import
import sqlite3

# Create the database and connection
connection = sqlite3.connect("my_database")

# Create a table for storing data
connection.execute("CREATE TABLE IF NOT EXISTS My_library (id INTEGER PRIMARY KEY, author STRING, book STRING);")

# Perform CRUD operations

# Create
connection.execute("INSERT INTO My_library (id,author,book) "
             "VALUES (1, 'Steve Biko','I write what I like.')")

# Read
cursor_object = connection.execute("SELECT * FROM My_library")
print(cursor_object.fetchall())