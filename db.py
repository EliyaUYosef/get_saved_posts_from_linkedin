import MySQLdb
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Convert DB_PORT to an integer
db_port = int(os.getenv("DB_PORT"))

# Connect to MySQL using mysqlclient
mysql_config = MySQLdb.connect(
    host=os.getenv("DB_HOST"),
    port=db_port,  # Pass the integer value
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
)
cursor = mysql_config.cursor()

# Execute an INSERT query
add_post = (
    "INSERT INTO posts "
    "(post_writer_profile_url, writer_details, post_text, post_title, post_link) "
    "VALUES (%s, %s, %s, %s, %s)"
)
post_data = (
    "Eliya",
    "Eliya",
    "Eliya",
    "Eliya",
    "Eliya",
)
cursor.execute(add_post, post_data)

# Commit the changes to the database
mysql_config.commit()

# Fetch all rows
query = "SELECT * FROM posts"
cursor.execute(query)
rows = cursor.fetchall()

# Print the rows
for row in rows:
    print(row)

# Close the cursor and MySQL connection
cursor.close()
mysql_config.close()
