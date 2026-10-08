"""
Script para mudar a senha do usuário admin
Use este script para atualizar a senha padrão após o primeiro login
"""
import sqlite3
import os
import sys
import bcrypt


def change_admin_password(new_password: str):
    """Mudar senha do usuário admin"""
    db_path = "monitor_leiloes.db"
    
    # Verificar se o banco existe
    if not os.path.exists(db_path):
        print(f"ERRO: Banco de dados '{db_path}' nao encontrado.")
        sys.exit(1)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se admin existe
        cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@monitorleiloes.com",))
        existing = cursor.fetchone()
        
        if not existing:
            print("ERRO: Usuario admin nao encontrado. Execute create_admin_direct.py primeiro.")
            sys.exit(1)
        
        # Hash da nova senha usando bcrypt
        new_password_bytes = new_password.encode('utf-8')
        if len(new_password_bytes) > 72:
            new_password_bytes = new_password_bytes[:72]
            new_password = new_password_bytes.decode('utf-8', errors='ignore')
            print(f"AVISO: Senha truncada para {len(new_password)} caracteres devido ao limite do bcrypt")
        
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        password_hash = password_hash.decode('utf-8')
        
        # Atualizar senha
        cursor.execute("""
            UPDATE users
            SET password_hash = ?, updated_at = datetime('now')
            WHERE email = ?
        """, (password_hash, "admin@monitorleiloes.com"))
        
        conn.commit()
        conn.close()
        
        print("SUCESSO: Senha do admin atualizada com sucesso!")
        print(f"Email: admin@monitorleiloes.com")
        print(f"Nova senha: {new_password}")
        
    except Exception as e:
        print(f"ERRO ao atualizar senha: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Script de Mudanca de Senha - Admin")
    print("=" * 60)
    print()
    
    if len(sys.argv) > 1:
        new_password = sys.argv[1]
    else:
        new_password = input("Digite a nova senha: ")
    
    if len(new_password) < 8:
        print("ERRO: A senha deve ter pelo menos 8 caracteres.")
        sys.exit(1)
    
    change_admin_password(new_password)
