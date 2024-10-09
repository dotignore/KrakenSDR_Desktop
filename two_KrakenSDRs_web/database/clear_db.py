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
