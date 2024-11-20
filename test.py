import psycopg2

try:
    conn = psycopg2.connect(
        host='localhost',
        port=5433,
        database='leaderboard',
        user='leaderboard-user',
        password='beelabs24',
        sslmode='disable'
    )
    print("Connection successful")
    cursor = conn.cursor()
    cursor.execute('SELECT 1')
    print(cursor.fetchone())
    conn.close()
except Exception as e:
    print(f"Error: {e}")