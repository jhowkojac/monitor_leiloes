"""
Criar usuário admin manualmente via SQL direto
⚠️  ATENÇÃO: Este script deve ser usado apenas em desenvolvimento!
⚠️  Em produção, use a API de criação de usuários com autenticação adequada.
"""
import sqlite3
import os
import sys
import secrets
from passlib.context import CryptContext


def create_admin_direct():
    """Criar usuário admin diretamente no banco"""
    db_path = "monitor_leiloes.db"
    
    # Verificar se o banco existe
    if not os.path.exists(db_path):
        print(f"❌ Erro: Banco de dados '{db_path}' não encontrado.")
        print("Execute o script de migração primeiro.")
        sys.exit(1)
    
    # Obter senha da variável de ambiente ou gerar uma aleatória
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_password:
        admin_password = secrets.token_urlsafe(16)
        print("⚠️  Nenhuma senha definida via ADMIN_PASSWORD.")
        print(f"⚠️  Senha aleatória gerada: {admin_password}")
        print("⚠️  Salve esta senha! Você precisará dela para fazer login.")
    
    # Verificar ambiente
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        print("❌ ERRO: Este script não deve ser executado em produção!")
        print("❌ Use a API de criação de usuários com autenticação adequada.")
        sys.exit(1)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Hash da senha usando bcrypt (consistente com UserService)
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Truncar senha para evitar erro do bcrypt (máximo 72 caracteres)
        if len(admin_password) > 72:
            admin_password = admin_password[:72]
        
        password_hash = pwd_context.hash(admin_password)
        
        # Verificar se admin já existe
        cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@monitorleiloes.com",))
        existing = cursor.fetchone()
        
        if existing:
            print("⚠️  Usuário admin já existe. Atualizando senha...")
            cursor.execute("""
                UPDATE users
                SET password_hash = ?, updated_at = datetime('now')
                WHERE email = ?
            """, (password_hash, "admin@monitorleiloes.com"))
        else:
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
        
        print("✅ Usuário admin criado/atualizado com sucesso!")
        print(f"📧 Email: admin@monitorleiloes.com")
        print(f"🔑 Senha: {admin_password}")
        print("⚠️  Mude a senha após o primeiro login!")
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Script de Criação de Admin - Monitor de Leilões")
    print("=" * 60)
    print()
    
    # Aviso de segurança
    print("⚠️  AVISO DE SEGURANÇA:")
    print("Este script cria um usuário admin com permissões completas.")
    print("Use apenas em desenvolvimento. Em produção, use a API.")
    print()
    
    create_admin_direct()
