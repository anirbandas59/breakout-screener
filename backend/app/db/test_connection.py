import psycopg2

conn = psycopg2.connect(
    dbname="trading_db",
    user="trading_user",
    password="tpassword",
    host="localhost",
    port=5432
)

print("Database connection successfully")
conn.close()
