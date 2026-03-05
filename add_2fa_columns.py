"""Migration para adicionar colunas 2FA na tabela users."""
import sqlite3
from app.database import Base
from app.models.user import User


def add_2fa_columns():
    """Adiciona colunas 2FA à tabela users existente."""
    db_path = "monitor_leiloes.db"
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se as colunas já existem
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Adicionar coluna totp_secret se não existir
        if 'totp_secret' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN totp_secret VARCHAR(32)")
            print("Coluna 'totp_secret' adicionada")
        
        # Adicionar coluna backup_codes se não existir
        if 'backup_codes' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN backup_codes TEXT")
            print("Coluna 'backup_codes' adicionada")
        
        # Adicionar coluna is_2fa_enabled se não existir
        if 'is_2fa_enabled' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN is_2fa_enabled BOOLEAN DEFAULT 0")
            print("Coluna 'is_2fa_enabled' adicionada")
        
        conn.commit()
        conn.close()
        
        print("Migration 2FA concluida com sucesso!")
        
    except Exception as e:
        print(f"Erro na migration 2FA: {e}")
        if conn:
            conn.close()


if __name__ == "__main__":
    add_2fa_columns()
