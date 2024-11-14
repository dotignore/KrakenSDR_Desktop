# GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
#
# Copyright (C) 2024 Tarasenko Volodymyr hc158b@gmail.com https://github.com/dotignore/KrakenSDR_Desktop/
# This is the source code for KrakenSDR direction.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sqlite3

# Connect to the database
conn = sqlite3.connect('database/krakensdr_data.db')

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Execute SQL query to select all data from the krakensdr_data table
cursor.execute('SELECT * FROM krakensdr_data')

# Fetch all the data
rows = cursor.fetchall()

# Print and save data to a text file
with open('output.txt', 'w') as file:
    if rows:
        header = "Session, Time, Freq (MHz), KrakenSDR ID, Latitude, Longitude, Bearing, Direction"
        print(header)
        file.write(header + "\n")
        
        for row in rows:
            print(row)
            file.write(f"{row}\n")
    else:
        message = "No data found in the database."
        print(message)
        file.write(message + "\n")

# Close the connection to the database
conn.close()
