"""
Criar usuário admin manualmente via SQL direto
"""
import sqlite3


def create_admin_direct():
    """Criar usuário admin diretamente no banco"""
    db_path = "monitor_leiloes.db"
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Hash simples sem bcrypt (temporário)
        import hashlib
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        
        # Inserir usuário admin diretamente
        cursor.execute("""
            INSERT INTO users (email, password_hash, is_active, is_admin, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            "admin@monitorleiloes.com",
            password_hash,
            1,  # is_active
            1   # is_admin
        ))
        
        conn.commit()
        conn.close()
        
        print("Usuario admin criado com sucesso!")
        print("Email: admin@monitorleiloes.com")
        print("Senha: admin123")
        print("Mude a senha em producao!")
        
    except Exception as e:
        print(f"Erro ao criar usuario admin: {e}")


if __name__ == "__main__":
    create_admin_direct()
