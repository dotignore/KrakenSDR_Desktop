import sqlite3

# Connect to the database (path: database/krakensdr_data.db)
conn = sqlite3.connect('database/krakensdr_data.db')

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Delete all records from the table
cursor.execute('DELETE FROM krakensdr_data')

# Save changes
conn.commit()

# Optionally, reset the auto-increment ID (if needed)
cursor.execute('VACUUM')

# Close the connection
conn.close()

print("Table 'krakensdr_data' cleared successfully!")
