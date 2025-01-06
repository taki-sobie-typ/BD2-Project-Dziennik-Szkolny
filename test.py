import mysql.connector

# Establish a connection to the MySQL database
conn = mysql.connector.connect(
    host="localhost",  # XAMPP default localhost
    user="root",       # Default MySQL user for XAMPP
    password="",       # Default MySQL password for XAMPP (empty by default)
    database="szkola"  # Database name
)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Execute the query to select all data from 'lekcje' table
cursor.execute("SELECT * FROM lekcje")

# Fetch all the rows from the result of the query
rows = cursor.fetchall()

# Print the result
for row in rows:
    print(row)

# Close the cursor and the connection
cursor.close()
conn.close()