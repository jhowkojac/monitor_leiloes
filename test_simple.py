"""
Simple Pre-deploy Test Suite
Validação básica antes do deploy
"""
import sys
import os

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Testa imports críticos"""
    print("Testando imports...")
    
    try:
        from main import app
        print("OK Import main.py")
    except Exception as e:
        print(f"ERRO import main.py: {e}")
        return False
    
    try:
        from app.routers.main import router
        from app.routers.dashboard import router as dashboard_router
        from app.routers.auth import router as auth_router
        from app.routers.two_factor import router as two_factor_router
        print("OK Import routers")
    except Exception as e:
        print(f"ERRO import routers: {e}")
        return False
    
    try:
        from app.services.dashboard import dashboard_service
        print("OK Import services")
    except Exception as e:
        print(f"ERRO import services: {e}")
        return False
    
    return True

def test_critical_files():
    """Testa se arquivos críticos existem"""
    print("Testando arquivos críticos...")
    
    critical_files = [
        "main.py",
        "app/templates/dashboard.html",
        "app/routers/dashboard.py",
        "app/services/dashboard.py",
        "static/pwa.js",
        "static/analytics.js",
        "static/theme.js",
        "static/manifest.json"
    ]
    
    missing_files = []
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"OK {file_path}")
        else:
            print(f"ERRO {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_app_creation():
    """Testa criação do app FastAPI"""
    print("Testando criação do app...")
    
    try:
        from main import app
        assert app is not None
        print("OK FastAPI app criado")
        return True
    except Exception as e:
        print(f"ERRO criar app: {e}")
        return False

def test_routes_configured():
    """Testa se rotas estão configuradas"""
    print("Testando configuração de rotas...")
    
    try:
        from main import app
        
        # Verificar se há rotas configuradas
        routes = [route.path for route in app.routes]
        
        critical_routes = ["/", "/docs", "/dashboard"]
        found_routes = [route for route in critical_routes if route in routes]
        
        if len(found_routes) > 0:
            print(f"OK Rotas encontradas: {found_routes}")
            return True
        else:
            print("ERRO Nenhuma rota crítica encontrada")
            return False
            
    except Exception as e:
        print(f"ERRO verificar rotas: {e}")
        return False

def test_templates():
    """Testa se templates existem e são válidos"""
    print("Testando templates...")
    
    try:
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory="app/templates")
        
        # Tentar carregar template do dashboard
        template = templates.get_template("dashboard.html")
        print("OK Template dashboard.html")
        return True
        
    except Exception as e:
        print(f"ERRO templates: {e}")
        return False

def run_simple_tests():
    """Executa testes simples"""
    print("Executando testes pré-deploy simples...")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Arquivos Críticos", test_critical_files),
        ("Criação do App", test_app_creation),
        ("Configuração de Rotas", test_routes_configured),
        ("Templates", test_templates)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro executar teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("RESUMO DOS TESTES:")
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passaram, {failed} falharam")
    
    if failed == 0:
        print("\nTODOS OS TESTES PASSARAM! Safe para deploy!")
        return True
    else:
        print(f"\n{failed} testes falharam! Verificar antes do deploy!")
        return False

if __name__ == "__main__":
    success = run_simple_tests()
    exit(0 if success else 1)
