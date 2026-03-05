import sqlite3

# Verificar schema da tabela users
conn = sqlite3.connect('monitor_leiloes.db')
cursor = conn.cursor()

# Listar tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tabelas no banco:")
for table in tables:
    print(f"  - {table[0]}")

# Verificar schema da tabela users
if ('users',) in tables:
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("\nSchema da tabela 'users':")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()
