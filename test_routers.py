"""
Test Suite para Routers do Monitor de Leilões
Testes unitários dos principais routers
"""
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from app.routers.dashboard import router as dashboard_router
from app.routers.auth import router as auth_router
from app.routers.analytics import router as analytics_router
from app.routers.theme import router as theme_router

class TestDashboardRouter:
    """Testes do Dashboard Router"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.client = TestClient(app)
        self.mock_db = Mock()
        self.mock_user = {"id": 1, "is_admin": True, "email": "admin@test.com"}
    
    @patch('app.routers.dashboard.get_db')
    @patch('app.routers.dashboard.require_admin')
    def test_get_overview(self, mock_require_admin, mock_get_db):
        """Teste GET /api/dashboard/overview"""
        mock_require_admin.return_value = self.mock_user
        mock_get_db.return_value = self.mock_db
        
        # Mock dashboard service
        with patch('app.routers.dashboard.dashboard_service.get_overview_stats') as mock_stats:
            mock_stats.return_value = {"total_users": 100, "total_leiloes": 50}
            
            response = self.client.get("/api/dashboard/overview")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "data" in data
    
    @patch('app.routers.dashboard.get_db')
    @patch('app.routers.dashboard.require_admin')
    def test_get_user_growth(self, mock_require_admin, mock_get_db):
        """Teste GET /api/dashboard/user-growth"""
        mock_require_admin.return_value = self.mock_user
        mock_get_db.return_value = self.mock_db
        
        with patch('app.routers.dashboard.dashboard_service.get_user_growth_data') as mock_growth:
            mock_growth.return_value = [{"date": "2024-01-01", "count": 10}]
            
            response = self.client.get("/api/dashboard/user-growth?days=30")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    @patch('app.routers.dashboard.get_db')
    @patch('app.routers.dashboard.require_admin')
    def test_get_2fa_stats(self, mock_require_admin, mock_get_db):
        """Teste GET /api/dashboard/2fa-stats"""
        mock_require_admin.return_value = self.mock_user
        mock_get_db.return_value = self.mock_db
        
        with patch('app.routers.dashboard.dashboard_service.get_2fa_stats') as mock_stats:
            mock_stats.return_value = {"enabled_users": 50, "disabled_users": 50}
            
            response = self.client.get("/api/dashboard/2fa-stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    @patch('app.routers.dashboard.get_db')
    @patch('app.routers.dashboard.require_admin')
    def test_get_system_health(self, mock_require_admin, mock_get_db):
        """Teste GET /api/dashboard/system-health"""
        mock_require_admin.return_value = self.mock_user
        mock_get_db.return_value = self.mock_db
        
        with patch('app.routers.dashboard.dashboard_service.get_system_health') as mock_health:
            mock_health.return_value = {"status": "healthy", "overall_score": "95%"}
            
            response = self.client.get("/api/dashboard/system-health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    @patch('app.routers.dashboard.require_admin')
    def test_get_stats_unauthorized(self, mock_require_admin):
        """Teste acesso não autorizado"""
        mock_require_admin.side_effect = Exception("Not authorized")
        
        response = self.client.get("/api/dashboard/overview")
        
        assert response.status_code in [401, 403, 500]

class TestAuthRouter:
    """Testes do Auth Router"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.client = TestClient(app)
        self.mock_db = Mock()
    
    @patch('app.routers.auth.get_db')
    def test_login_success(self, mock_get_db):
        """Teste login com sucesso"""
        mock_get_db.return_value = self.mock_db
        
        with patch('app.routers.auth.user_service.authenticate_user') as mock_auth:
            mock_auth.return_value = {"id": 1, "email": "test@test.com", "is_admin": False}
            
            with patch('app.routers.auth.jwt_service.create_access_token') as mock_token:
                mock_token.return_value = "test_token"
                
                response = self.client.post("/api/auth/login", json={
                    "email": "test@test.com",
                    "password": "password123"
                })
                
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Teste login com credenciais inválidas"""
        with patch('app.routers.auth.user_service.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            response = self.client.post("/api/auth/login", json={
                "email": "test@test.com",
                "password": "wrong_password"
            })
            
            assert response.status_code == 401
    
    def test_login_missing_fields(self):
        """Teste login com campos faltando"""
        response = self.client.post("/api/auth/login", json={
            "email": "test@test.com"
            # password faltando
        })
        
        assert response.status_code == 422  # Validation error

class TestAnalyticsRouter:
    """Testes do Analytics Router"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.client = TestClient(app)
        self.mock_db = Mock()
        self.mock_user = {"id": 1, "is_admin": True}
    
    @patch('app.routers.analytics.get_db')
    @patch('app.routers.analytics.get_current_user')
    def test_track_event(self, mock_get_user, mock_get_db):
        """Teste POST /api/analytics/track"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = self.mock_db
        
        with patch('app.routers.analytics.analytics_service.track_event') as mock_track:
            mock_track.return_value = {"id": 1, "event_type": "page_view"}
            
            response = self.client.post("/api/analytics/track", json={
                "event_type": "page_view",
                "page": "/dashboard",
                "metadata": {"referrer": "/login"}
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    @patch('app.routers.analytics.get_db')
    @patch('app.routers.analytics.get_current_user')
    def test_get_dashboard_stats(self, mock_get_user, mock_get_db):
        """Teste GET /api/analytics/dashboard"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = self.mock_db
        
        with patch('app.routers.analytics.analytics_service.get_dashboard_stats') as mock_stats:
            mock_stats.return_value = {"total_events": 1000, "unique_users": 50}
            
            response = self.client.get("/api/analytics/dashboard")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    @patch('app.routers.analytics.get_db')
    @patch('app.routers.analytics.get_current_user')
    def test_get_user_analytics(self, mock_get_user, mock_get_db):
        """Teste GET /api/analytics/users/{user_id}"""
        mock_get_user.return_value = self.mock_user
        mock_get_db.return_value = self.mock_db
        
        with patch('app.routers.analytics.analytics_service.get_user_analytics') as mock_analytics:
            mock_analytics.return_value = {"events": 50, "pages_visited": 10}
            
            response = self.client.get("/api/analytics/users/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

class TestThemeRouter:
    """Testes do Theme Router"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.client = TestClient(app)
        self.mock_user = {"id": 1, "is_admin": False}
    
    @patch('app.routers.theme.get_current_user')
    def test_get_themes(self, mock_get_user):
        """Teste GET /api/theme/themes"""
        mock_get_user.return_value = self.mock_user
        
        response = self.client.get("/api/theme/themes")
        
        assert response.status_code == 200
        data = response.json()
        assert "default" in data
        assert "dark" in data
    
    @patch('app.routers.theme.get_current_user')
    def test_get_theme_details(self, mock_get_user):
        """Teste GET /api/theme/themes/{theme_name}"""
        mock_get_user.return_value = self.mock_user
        
        response = self.client.get("/api/theme/themes/default")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "colors" in data
    
    @patch('app.routers.theme.get_current_user')
    def test_validate_theme(self, mock_get_user):
        """Teste POST /api/theme/validate"""
        mock_get_user.return_value = self.mock_user
        
        valid_theme = {
            "name": "test_theme",
            "colors": {"primary": "#000000"},
            "fonts": {"primary": "Arial"}
        }
        
        response = self.client.post("/api/theme/validate", json=valid_theme)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
    
    @patch('app.routers.theme.get_current_user')
    def test_validate_theme_invalid(self, mock_get_user):
        """Teste POST /api/theme/validate com tema inválido"""
        mock_get_user.return_value = self.mock_user
        
        invalid_theme = {
            "name": "",  # Nome inválido
            "colors": {}  # Sem cores
        }
        
        response = self.client.post("/api/theme/validate", json=invalid_theme)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False

def run_router_tests():
    """Executa todos os testes de routers"""
    print("Executando testes de routers...")
    
    test_classes = [
        TestDashboardRouter,
        TestAuthRouter,
        TestAnalyticsRouter,
        TestThemeRouter
    ]
    
    results = []
    
    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        
        try:
            test_instance = test_class()
            test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
            
            for method_name in test_methods:
                try:
                    test_instance.setup_method()
                    test_method = getattr(test_instance, method_name)
                    test_method()
                    print(f"  OK {method_name}")
                except Exception as e:
                    print(f"  FAIL {method_name}: {e}")
                    results.append(f"FAIL: {test_class.__name__}.{method_name}")
        
        except Exception as e:
            print(f"  FAIL Setup: {e}")
            results.append(f"FAIL: {test_class.__name__}.setup")
    
    return results

if __name__ == "__main__":
    results = run_router_tests()
    
    if results:
        print(f"\n{len(results)} testes falharam:")
        for result in results:
            print(f"  - {result}")
        exit(1)
    else:
        print("\nTodos os testes de routers passaram!")
        exit(0)
