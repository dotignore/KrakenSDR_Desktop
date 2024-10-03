import sqlite3

# Connect to the database (if the database doesn't exist, it will be created)
conn = sqlite3.connect('database/krakensdr_data.db')

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Create a table if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS krakensdr_data (
    time TEXT,
    frequency REAL,
    krakensdr_id INTEGER,
    latitude REAL,
    longitude REAL,
    bearing REAL,
    direction REAL
)
''')

# Save changes
conn.commit()

# Close the connection
conn.close()

print("Database and table created successfully!")
