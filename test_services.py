"""
Test Suite para Services do Monitor de Leilões
Testes unitários dos principais services
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.dashboard import dashboard_service
from app.services.analytics import analytics_service
from app.services.theme import theme_service

class TestDashboardService:
    """Testes do Dashboard Service"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.mock_db = Mock()
    
    def test_get_overview_stats(self):
        """Teste get_overview_stats"""
        # Mock database queries
        mock_user_count = Mock()
        mock_user_count.scalar.return_value = 100
        self.mock_db.query.return_value.count.return_value = mock_user_count
        
        result = dashboard_service.get_overview_stats(self.mock_db)
        
        assert result is not None
        assert "total_users" in result
        assert isinstance(result["total_users"], int)
    
    def test_get_user_growth_data(self):
        """Teste get_user_growth_data"""
        result = dashboard_service.get_user_growth_data(self.mock_db, 30)
        
        assert result is not None
        assert isinstance(result, list)
    
    def test_get_2fa_stats(self):
        """Teste get_2fa_stats"""
        result = dashboard_service.get_2fa_stats(self.mock_db)
        
        assert result is not None
        assert "enabled_users" in result
        assert "disabled_users" in result
    
    def test_get_system_health(self):
        """Teste get_system_health"""
        result = dashboard_service.get_system_health(self.mock_db)
        
        assert result is not None
        assert "status" in result
        assert "overall_score" in result

class TestAnalyticsService:
    """Testes do Analytics Service"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.mock_db = Mock()
    
    def test_track_event(self):
        """Teste track_event"""
        event_data = {
            "event_type": "page_view",
            "user_id": 1,
            "page": "/dashboard",
            "metadata": {"referrer": "/login"}
        }
        
        result = analytics_service.track_event(self.mock_db, event_data)
        
        assert result is not None
    
    def test_get_dashboard_stats(self):
        """Teste get_dashboard_stats"""
        result = analytics_service.get_dashboard_stats(self.mock_db)
        
        assert result is not None
        assert "total_events" in result
        assert "unique_users" in result
    
    def test_get_user_analytics(self):
        """Teste get_user_analytics"""
        result = analytics_service.get_user_analytics(self.mock_db, 1)
        
        assert result is not None
        assert "events" in result
        assert "pages_visited" in result

class TestThemeService:
    """Testes do Theme Service"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.mock_db = Mock()
    
    def test_get_available_themes(self):
        """Teste get_available_themes"""
        result = theme_service.get_all_themes()
        
        assert result is not None
        assert isinstance(result, dict)
        assert "default" in result
        assert "dark" in result
    
    def test_get_theme_details(self):
        """Teste get_theme_details"""
        result = theme_service.get_theme("default")
        
        assert result is not None
        assert "name" in result
        assert "colors" in result
        assert "fonts" in result
    
    def test_validate_theme_data(self):
        """Teste validate_theme_data"""
        valid_theme = {
            "name": "test_theme",
            "colors": {"primary": "#000000"},
            "fonts": {"primary": "Arial"}
        }
        
        result = theme_service.validate_theme(valid_theme)
        
        assert result["valid"] is True
    
    def test_validate_theme_data_invalid(self):
        """Teste validate_theme_data com dados inválidos"""
        invalid_theme = {
            "name": "",  # Nome vazio
            "colors": {},  # Sem cores
        }
        
        result = theme_service.validate_theme(invalid_theme)
        
        assert result["valid"] is False
    
    def test_generate_css_variables(self):
        """Teste generate_css_variables"""
        theme_data = {
            "colors": {"primary": "#000000"},
            "fonts": {"primary": "Arial"},
            "border_radius": {"small": "4px"}
        }
        
        result = theme_service.get_css_variables(theme_data)
        
        assert result is not None
        assert "--color-primary: #000000" in result
        assert "--font-primary: Arial" in result

class TestServiceIntegration:
    """Testes de integração entre services"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.mock_db = Mock()
    
    @patch('app.services.dashboard.get_db')
    @patch('app.services.analytics.get_db')
    def test_dashboard_analytics_integration(self, mock_analytics_db, mock_dashboard_db):
        """Teste integração dashboard + analytics"""
        mock_dashboard_db.return_value = self.mock_db
        mock_analytics_db.return_value = self.mock_db
        
        # Obter stats do dashboard
        dashboard_stats = dashboard_service.get_overview_stats(self.mock_db)
        
        # Obter stats do analytics
        analytics_stats = analytics_service.get_dashboard_stats(self.mock_db)
        
        assert dashboard_stats is not None
        assert analytics_stats is not None
        
        # Verificar consistência
        assert "total_users" in dashboard_stats
        assert "unique_users" in analytics_stats

def run_service_tests():
    """Executa todos os testes de services"""
    print("Executando testes de services...")
    
    test_classes = [
        TestDashboardService,
        TestAnalyticsService,
        TestThemeService,
        TestServiceIntegration
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
    results = run_service_tests()
    
    if results:
        print(f"\n{len(results)} testes falharam:")
        for result in results:
            print(f"  - {result}")
        exit(1)
    else:
        print("\nTodos os testes de services passaram!")
        exit(0)
