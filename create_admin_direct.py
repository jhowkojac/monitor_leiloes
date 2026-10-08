"""
Criar usuário admin manualmente via SQL direto
ATENÇÃO: Este script deve ser usado apenas em desenvolvimento!
Em produção, use a API de criação de usuários com autenticação adequada.
"""
import sqlite3
import os
import sys
import bcrypt


def create_admin_direct():
    """Criar usuário admin diretamente no banco"""
    db_path = "monitor_leiloes.db"
    
    # Verificar se o banco existe
    if not os.path.exists(db_path):
        print(f"ERRO: Banco de dados '{db_path}' nao encontrado.")
        print("Execute o script de migracao primeiro.")
        sys.exit(1)
    
    # Obter senha da variável de ambiente ou usar uma padrão
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_password:
        # Senha padrão para desenvolvimento (mude depois!)
        admin_password = "admin123"
        print("AVISO: Nenhuma senha definida via ADMIN_PASSWORD.")
        print("AVISO: Usando senha padrao: admin123")
        print("AVISO: Mude a senha apos o primeiro login!")
        print("DICA: Defina ADMIN_PASSWORD=senha_sua via variavel de ambiente")
    
    # Verificar ambiente
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        print("ERRO: Este script nao deve ser executado em producao!")
        print("ERRO: Use a API de criacao de usuarios com autenticacao adequada.")
        sys.exit(1)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Hash da senha usando bcrypt diretamente
        # bcrypt tem limite de 72 bytes
        admin_password_bytes = admin_password.encode('utf-8')
        if len(admin_password_bytes) > 72:
            admin_password_bytes = admin_password_bytes[:72]
            admin_password = admin_password_bytes.decode('utf-8', errors='ignore')
            print(f"AVISO: Senha truncada para {len(admin_password)} caracteres devido ao limite do bcrypt")
        
        # Gerar salt e hash
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), salt)
        # Converter para string para armazenar no banco
        password_hash = password_hash.decode('utf-8')
        
        # Verificar se admin já existe
        cursor.execute("SELECT id FROM users WHERE email = ?", ("admin@monitorleiloes.com",))
        existing = cursor.fetchone()
        
        if existing:
            print("AVISO: Usuario admin ja existe. Atualizando senha...")
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
        
        print("SUCESSO: Usuario admin criado/atualizado com sucesso!")
        print(f"Email: admin@monitorleiloes.com")
        print(f"Senha: {admin_password}")
        print("AVISO: Mude a senha apos o primeiro login!")
        
    except Exception as e:
        print(f"ERRO ao criar usuario admin: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Script de Criação de Admin - Monitor de Leiloes")
    print("=" * 60)
    print()
    
    # Aviso de segurança
    print("AVISO DE SEGURANCA:")
    print("Este script cria um usuario admin com permissoes completas.")
    print("Use apenas em desenvolvimento. Em producao, use a API.")
    print()
    
    create_admin_direct()
