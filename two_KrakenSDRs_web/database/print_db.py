import sqlite3

# Connect to the database
conn = sqlite3.connect('database/krakensdr_data.db')

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Execute SQL query to select all data from the krakensdr_data table
cursor.execute('SELECT * FROM krakensdr_data')

# Fetch all the data
rows = cursor.fetchall()

# Check if there is any data
if rows:
    print("Session, Time, Freq (MHz), KrakenSDR ID, Latitude, Longitude, Bearing, Direction")
    for row in rows:
        print(row)
else:
    print("No data found in the database.")

# Close the connection to the database
conn.close()
