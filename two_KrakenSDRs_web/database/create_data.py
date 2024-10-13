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

# Connect to the database (if the database doesn't exist, it will be created)
conn = sqlite3.connect('database/krakensdr_data.db')

# Create a cursor to execute SQL commands
cursor = conn.cursor()

# Create a table if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS krakensdr_data (
    session INTEGER,
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
