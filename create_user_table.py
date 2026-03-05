"""
Migration para criar tabela de usuários
"""
from app.database import engine
from app.models.user import User
from sqlalchemy import text


def create_user_table():
    """Criar tabela de usuários"""
    User.metadata.create_all(bind=engine)
    print("Tabela 'users' criada com sucesso!")


def create_admin_user():
    """Criar usuário admin padrão"""
    from app.services.user import user_service
    from app.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Verificar se já existe admin
        existing_admin = db.query(User).filter(User.email == "admin@monitorleiloes.com").first()
        
        if not existing_admin:
            # Criar admin padrão com senha muito curta
            admin_user = user_service.create_user(
                db=db,
                email="admin@monitorleiloes.com",
                password="admin123",  # Apenas 8 caracteres
                is_admin=True
            )
            print(f"Usuario admin criado: {admin_user.email}")
        else:
            print("Usuario admin já existe")
    
    except Exception as e:
        print(f"Erro ao criar usuario admin: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Criando tabela de usuarios...")
    create_user_table()
    
    print("Criando usuario admin padrao...")
    create_admin_user()
    
    print("Migration concluida!")
