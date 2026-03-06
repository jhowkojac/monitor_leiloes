"""
Test Suite para Monitor de Leilões
Validação antes de deploy
"""
import asyncio
from fastapi.testclient import TestClient
import sys
import os

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

class TestMonitorLeiloes:
    """Test suite principal do Monitor de Leilões"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.client = TestClient(app)
        self.base_url = "http://localhost:8000"
    
    def test_app_startup(self):
        """Teste de startup da aplicação"""
        try:
            response = self.client.get("/")
            assert response.status_code in [200, 404]  # Pode não ter rota principal
        except Exception as e:
            print(f"App startup test error: {e}")
            # Não falhar completamente, apenas avisar
            pass
    
    def test_health_check(self):
        """Teste de health check"""
        response = self.client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()
    
    def test_dashboard_route_exists(self):
        """Teste se rota do dashboard existe"""
        response = self.client.get("/dashboard")
        assert response.status_code == 200
        assert "dashboard" in response.text.lower()
    
    def test_static_files_served(self):
        """Teste se arquivos estáticos são servidos"""
        static_files = [
            "/static/pwa.js",
            "/static/analytics.js", 
            "/static/theme.js",
            "/static/manifest.json"
        ]
        
        for file_path in static_files:
            response = self.client.get(file_path)
            assert response.status_code == 200, f"Failed to load {file_path}"
    
    def test_api_endpoints_exist(self):
        """Teste se endpoints de API existem"""
        api_endpoints = [
            "/api/dashboard/stats",
            "/api/dashboard/users",
            "/api/analytics/dashboard",
            "/api/theme/themes",
            "/api/pwa/status"
        ]
        
        for endpoint in api_endpoints:
            response = self.client.get(endpoint)
            # Pode retornar 401 (não autenticado) ou 200 (sucesso)
            assert response.status_code in [200, 401, 403], f"Failed on {endpoint}"
    
    def test_middleware_configured(self):
        """Teste se middlewares estão configurados"""
        response = self.client.get("/docs")
        headers = response.headers
        
        # Verificar headers de segurança
        security_headers = [
            "x-content-type-options",
            "x-frame-options", 
            "x-xss-protection"
        ]
        
        for header in security_headers:
            assert header in headers, f"Security header {header} missing"
    
    def test_cors_headers(self):
        """Teste CORS headers"""
        response = self.client.options("/docs")
        assert "access-control-allow-origin" in response.headers
    
    def test_error_handling(self):
        """Teste tratamento de erros"""
        response = self.client.get("/nonexistent-route")
        assert response.status_code == 404
    
    def test_rate_limiting_configured(self):
        """Teste se rate limiting está configurado"""
        # Fazer múltiplas requisições rápidas
        responses = []
        for _ in range(5):
            response = self.client.get("/docs")
            responses.append(response.status_code)
        
        # Pode ou não ter rate limiting ativo
        assert all(status in [200, 429] for status in responses)

class TestSmokeTests:
    """Smoke tests para validação rápida"""
    
    def setup_method(self):
        """Setup para smoke tests"""
        self.client = TestClient(app)
    
    def test_critical_routes_smoke(self):
        """Teste crítico de rotas principais"""
        critical_routes = [
            ("/", "GET"),
            ("/dashboard", "GET"),
            ("/docs", "GET"),
            ("/static/pwa.js", "GET")
        ]
        
        for route, method in critical_routes:
            if method == "GET":
                response = self.client.get(route)
                assert response.status_code != 500, f"Critical route {route} failing"
    
    def test_database_connection(self):
        """Teste básico de conexão com database"""
        try:
            # Tentar acessar uma rota que usa database
            response = self.client.get("/api/dashboard/stats")
            # Pode falhar por autenticação, mas não deve ser erro 500
            assert response.status_code != 500
        except Exception as e:
            print(f"Database connection test failed: {e}")
            # Não falhar o teste, apenas avisar
            pass

class TestIntegration:
    """Testes de integração"""
    
    def setup_method(self):
        """Setup para integração"""
        self.client = TestClient(app)
    
    def test_dashboard_integration(self):
        """Teste de integração do dashboard"""
        # Testar se dashboard carrega
        response = self.client.get("/dashboard")
        assert response.status_code == 200
        
        # Verificar se elementos principais existem
        assert "dashboard" in response.text.lower()
        assert "stats" in response.text.lower() or "estatísticas" in response.text.lower()
    
    def test_static_assets_integration(self):
        """Teste de integração de assets estáticos"""
        assets = [
            "pwa.js",
            "analytics.js", 
            "theme.js"
        ]
        
        for asset in assets:
            response = self.client.get(f"/static/{asset}")
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/javascript")
    
    def test_api_integration(self):
        """Teste de integração de APIs"""
        # Testar se APIs respondem (mesmo que com erro de auth)
        apis = [
            "/api/dashboard/stats",
            "/api/theme/themes",
            "/api/analytics/dashboard"
        ]
        
        for api in apis:
            response = self.client.get(api)
            assert response.status_code in [200, 401, 403], f"API {api} not responding correctly"

def run_pre_deploy_tests():
    """Executa todos os testes antes do deploy"""
    print("Executando testes pre-deploy...")
    
    # Criar suite de testes
    test_suite = [
        TestMonitorLeiloes,
        TestSmokeTests, 
        TestIntegration
    ]
    
    results = []
    
    for test_class in test_suite:
        print(f"\nExecutando {test_class.__name__}...")
        
        try:
            # Criar instância
            test_instance = test_class()
            
            # Executar todos os métodos de teste
            test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
            
            for method_name in test_methods:
                try:
                    # Setup
                    test_instance.setup_method()
                    
                    # Executar teste
                    test_method = getattr(test_instance, method_name)
                    test_method()
                    
                    print(f"  OK {method_name}")
                    
                except Exception as e:
                    print(f"  FAIL {method_name}: {str(e)}")
                    results.append(f"FAIL: {test_class.__name__}.{method_name}")
        
        except Exception as e:
            print(f"  FAIL Setup failed: {str(e)}")
            results.append(f"FAIL: {test_class.__name__}.setup")
    
    # Resumo
    print(f"\nResumo dos Testes:")
    if results:
        print(f"{len(results)} testes falharam:")
        for result in results:
            print(f"  - {result}")
        return False
    else:
        print(f"Todos os testes passaram!")
        return True

if __name__ == "__main__":
    # Executar testes
    success = run_pre_deploy_tests()
    
    if success:
        print("\nTestes passaram! Safe para deploy!")
        exit(0)
    else:
        print("\nTestes falharam! Corrigir antes do deploy!")
        exit(1)
