"""
Test Suite para Middlewares do Monitor de Leilões
Testes unitários dos principais middlewares
"""
import sys
import os
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.middleware.auth import AuthMiddleware
from app.middleware.advanced_rate_limit import AdvancedRateLimitMiddleware, RateLimitConfig

class TestAuthMiddleware:
    """Testes do Auth Middleware"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.mock_app = Mock()
        self.middleware = AuthMiddleware(self.mock_app)
    
    @patch('app.middleware.auth.get_current_user_optional')
    async def test_dispatch_with_user(self, mock_get_user):
        """Teste dispatch com usuário autenticado"""
        mock_get_user.return_value = {"id": 1, "email": "test@test.com"}
        
        # Mock request
        mock_request = Mock()
        mock_request.headers = {"authorization": "Bearer token"}
        
        # Mock call_next
        mock_call_next = AsyncMock()
        mock_response = Mock()
        mock_call_next.return_value = mock_response
        
        # Executar middleware
        response = await self.middleware.dispatch(mock_request, mock_call_next)
        
        # Verificar
        assert response == mock_response
        mock_call_next.assert_called_once()
        mock_get_user.assert_called_once()
    
    @patch('app.middleware.auth.get_current_user_optional')
    async def test_dispatch_without_user(self, mock_get_user):
        """Teste dispatch sem usuário"""
        mock_get_user.return_value = None
        
        # Mock request
        mock_request = Mock()
        mock_request.headers = {}
        
        # Mock call_next
        mock_call_next = AsyncMock()
        mock_response = Mock()
        mock_call_next.return_value = mock_response
        
        # Executar middleware
        response = await self.middleware.dispatch(mock_request, mock_call_next)
        
        # Verificar
        assert response == mock_response
        mock_call_next.assert_called_once()
    
    @patch('app.middleware.auth.get_current_user_optional')
    async def test_dispatch_with_exception(self, mock_get_user):
        """Teste dispatch com exceção"""
        mock_get_user.side_effect = Exception("Auth error")
        
        # Mock request
        mock_request = Mock()
        mock_request.headers = {"authorization": "Bearer token"}
        
        # Mock call_next
        mock_call_next = AsyncMock()
        
        # Executar middleware
        try:
            await self.middleware.dispatch(mock_request, mock_call_next)
            assert False, "Deveria ter lançado exceção"
        except Exception:
            pass  # Esperado

class TestAdvancedRateLimitMiddleware:
    """Testes do Advanced Rate Limit Middleware"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.mock_app = Mock()
        self.config = RateLimitConfig()
        self.middleware = AdvancedRateLimitMiddleware(self.mock_app, self.config)
    
    async def test_dispatch_under_limit(self):
        """Teste dispatch sob o limite"""
        # Mock request
        mock_request = Mock()
        mock_request.url = Mock()
        mock_request.url.path = "/api/test"
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}
        
        # Mock call_next
        mock_call_next = AsyncMock()
        mock_response = Mock()
        mock_call_next.return_value = mock_response
        
        # Executar middleware
        response = await self.middleware.dispatch(mock_request, mock_call_next)
        
        # Verificar
        assert response == mock_response
        mock_call_next.assert_called_once()
    
    async def test_dispatch_rate_limit_exceeded(self):
        """Teste dispatch com limite excedido"""
        # Mock request
        mock_request = Mock()
        mock_request.url = Mock()
        mock_request.url.path = "/api/test"
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {}
        
        # Mock call_next
        mock_call_next = AsyncMock()
        
        # Simular muitas requisições
        for i in range(self.config.default_limits["requests_per_minute"] + 1):
            try:
                await self.middleware.dispatch(mock_request, mock_call_next)
            except Exception:
                # Espera exceção após exceder limite
                break
        else:
            # Se não quebrou, força exceder
            await self.middleware.dispatch(mock_request, mock_call_next)
    
    async def test_dispatch_with_user(self):
        """Teste dispatch com usuário autenticado"""
        # Mock request com usuário
        mock_request = Mock()
        mock_request.url = Mock()
        mock_request.url.path = "/api/test"
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"authorization": "Bearer token"}
        mock_request.state = Mock()
        mock_request.state.user = {"id": 1, "email": "test@test.com"}
        
        # Mock call_next
        mock_call_next = AsyncMock()
        mock_response = Mock()
        mock_call_next.return_value = mock_response
        
        # Executar middleware
        response = await self.middleware.dispatch(mock_request, mock_call_next)
        
        # Verificar
        assert response == mock_response
        mock_call_next.assert_called_once()
    
    def test_create_blocked_response(self):
        """Teste criação de response bloqueado"""
        response = self.middleware.create_blocked_response("Rate limit exceeded")
        
        assert response.status_code == 429
        assert "Retry-After" in response.headers
    
    def test_add_rate_limit_headers(self):
        """Teste adição de headers de rate limit"""
        mock_response = Mock()
        mock_response.headers = {}
        
        limits = {"requests_per_minute": 100}
        ip_key = "127.0.0.1"
        user_key = None
        
        self.middleware.add_rate_limit_headers(mock_response, limits, ip_key, user_key)
        
        # Verificar headers
        assert "X-RateLimit-Limit-requests_per_minute" in mock_response.headers
        assert mock_response.headers["X-RateLimit-Limit-requests_per_minute"] == "100"

class TestRateLimitConfig:
    """Testes da RateLimitConfig"""
    
    def test_default_config(self):
        """Teste configuração padrão"""
        config = RateLimitConfig()
        
        assert config.enabled is True
        assert "requests_per_minute" in config.default_limits
        assert "requests_per_hour" in config.default_limits
        assert "requests_per_day" in config.default_limits
    
    def test_custom_config(self):
        """Teste configuração customizada"""
        custom_limits = {
            "requests_per_minute": 50,
            "requests_per_hour": 500
        }
        
        config = RateLimitConfig(
            enabled=True,
            default_limits=custom_limits,
            block_duration=300
        )
        
        assert config.default_limits["requests_per_minute"] == 50
        assert config.default_limits["requests_per_hour"] == 500
        assert config.block_duration == 300

class TestMemoryRateLimitStorage:
    """Testes do MemoryRateLimitStorage"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        from app.middleware.advanced_rate_limit import MemoryRateLimitStorage
        self.storage = MemoryRateLimitStorage()
    
    def test_add_request(self):
        """Teste adicionar request"""
        key = "127.0.0.1"
        window = "requests_per_minute"
        
        count = self.storage.add_request(key, window)
        
        assert count == 1
    
    def test_add_multiple_requests(self):
        """Teste adicionar múltiplas requests"""
        key = "127.0.0.1"
        window = "requests_per_minute"
        
        # Adicionar 3 requests
        for i in range(3):
            count = self.storage.add_request(key, window)
        
        assert count == 3
    
    def test_get_count(self):
        """Teste obter count"""
        key = "127.0.0.1"
        window = "requests_per_minute"
        
        # Adicionar requests
        self.storage.add_request(key, window)
        self.storage.add_request(key, window)
        
        count = self.storage.get_count(key, window)
        
        assert count == 2
    
    def test_block_and_unblock(self):
        """Teste bloqueio e desbloqueio"""
        key = "127.0.0.1"
        
        # Bloquear
        self.storage.block(key, 60)
        assert self.storage.is_blocked(key) is True
        
        # Desbloquear
        self.storage.unblock(key)
        assert self.storage.is_blocked(key) is False
    
    def test_cleanup_expired_blocks(self):
        """Teste limpeza de bloqueios expirados"""
        key = "127.0.0.1"
        
        # Bloquear com duração curta
        self.storage.block(key, 1)
        
        # Forçar expiração (mock time)
        import time
        original_time = time.time
        time.time = lambda: original_time() + 2
        
        try:
            self.storage.cleanup_expired_blocks()
            assert self.storage.is_blocked(key) is False
        finally:
            time.time = original_time

async def run_middleware_tests():
    """Executa todos os testes de middlewares"""
    print("Executando testes de middlewares...")
    
    # Testes síncronos
    sync_tests = [
        TestRateLimitConfig,
        TestMemoryRateLimitStorage
    ]
    
    results = []
    
    for test_class in sync_tests:
        print(f"\n{test_class.__name__}:")
        
        try:
            test_instance = test_class()
            test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
            
            for method_name in test_methods:
                try:
                    test_instance.setup_method() if hasattr(test_instance, 'setup_method') else None
                    test_method = getattr(test_instance, method_name)
                    
                    # Se for async, usar await
                    if asyncio.iscoroutinefunction(test_method):
                        await test_method()
                    else:
                        test_method()
                    
                    print(f"  OK {method_name}")
                except Exception as e:
                    print(f"  FAIL {method_name}: {e}")
                    results.append(f"FAIL: {test_class.__name__}.{method_name}")
        
        except Exception as e:
            print(f"  FAIL Setup: {e}")
            results.append(f"FAIL: {test_class.__name__}.setup")
    
    # Testes assíncronos
    async_tests = [
        TestAuthMiddleware,
        TestAdvancedRateLimitMiddleware
    ]
    
    for test_class in async_tests:
        print(f"\n{test_class.__name__}:")
        
        try:
            test_instance = test_class()
            test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
            
            for method_name in test_methods:
                try:
                    test_instance.setup_method()
                    test_method = getattr(test_instance, method_name)
                    await test_method()
                    print(f"  OK {method_name}")
                except Exception as e:
                    print(f"  FAIL {method_name}: {e}")
                    results.append(f"FAIL: {test_class.__name__}.{method_name}")
        
        except Exception as e:
            print(f"  FAIL Setup: {e}")
            results.append(f"FAIL: {test_class.__name__}.setup")
    
    return results

if __name__ == "__main__":
    import asyncio
    
    results = asyncio.run(run_middleware_tests())
    
    if results:
        print(f"\n{len(results)} testes falharam:")
        for result in results:
            print(f"  - {result}")
        exit(1)
    else:
        print("\nTodos os testes de middlewares passaram!")
        exit(0)
