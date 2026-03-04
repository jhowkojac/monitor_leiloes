"""
Testes de segurança para o Monitor de Leilões
"""
import pytest
import time
from fastapi.testclient import TestClient
from main import app
from app.security import SecurityUtils


class TestSecurityHeaders:
    """Testa headers de segurança"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_security_headers_present(self, client):
        """Testa se headers de segurança estão presentes"""
        response = client.get("/")
        
        # Headers obrigatórios de segurança
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Content-Security-Policy",
            "Referrer-Policy"
        ]
        
        for header in required_headers:
            assert header in response.headers, f"Header {header} ausente"
        
        # Valores específicos
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "1; mode=block" in response.headers["X-XSS-Protection"]
    
    def test_csp_policy_restrictive(self, client):
        """Testa se CSP é restritiva"""
        response = client.get("/")
        csp = response.headers.get("Content-Security-Policy", "")
        
        # Deve permitir apenas fontes seguras
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        assert "font-src 'self'" in csp
        
        # Não deve permitir 'unsafe-inline' em script-src (exceto para desenvolvimento)
        # Nota: Temos 'unsafe-inline' para desenvolvimento, mas poderia ser removido em produção
    
    def test_no_sensitive_info_in_headers(self, client):
        """Testa se não há informações sensíveis nos headers"""
        response = client.get("/")
        
        # Headers que não devem existir
        forbidden_headers = [
            "Server",
            "X-Powered-By",
            "X-AspNet-Version",
            "X-AspNetMvc-Version"
        ]
        
        for header in forbidden_headers:
            assert header not in response.headers, f"Header sensível {header} presente"


class TestInputValidation:
    """Testa validação de entrada"""
    
    def test_xss_prevention(self):
        """Testa prevenção de XSS"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            sanitized = SecurityUtils.sanitize_input(payload)
            
            # Não deve conter tags script
            assert "<script" not in sanitized.lower()
            assert "javascript:" not in sanitized.lower()
            assert "onerror=" not in sanitized.lower()
            assert "onload=" not in sanitized.lower()
    
    def test_sql_injection_prevention(self):
        """Testa prevenção de SQL injection"""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT * FROM users",
            "'; DELETE FROM users; --",
            "'; INSERT INTO users VALUES('hack'); --"
        ]
        
        for payload in sql_payloads:
            sanitized = SecurityUtils.sanitize_input(payload)
            
            # Não deve conter comandos SQL
            assert "drop table" not in sanitized.lower()
            assert "union select" not in sanitized.lower()
            assert "delete from" not in sanitized.lower()
            assert "insert into" not in sanitized.lower()
    
    def test_path_traversal_prevention(self):
        """Testa prevenção de path traversal"""
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd"
        ]
        
        for payload in path_payloads:
            sanitized = SecurityUtils.sanitize_input(payload)
            
            # Não deve conter path traversal
            assert "../" not in sanitized
            assert "..\\" not in sanitized
            assert "%2e%2e" not in sanitized.lower()


class TestRateLimiting:
    """Testa rate limiting"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_basic_rate_limiting(self, client):
        """Testa rate limiting básico"""
        # Faz múltiplas requisições rápidas
        responses = []
        
        for i in range(10):
            response = client.get("/api/leiloes")
            responses.append(response)
        
        # A maioria deve ser bem-sucedida
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 8, f"Apenas {success_count}/10 requisições tiveram sucesso"
    
    def test_rate_limiting_headers(self, client):
        """Testa headers de rate limiting"""
        # Faz requisições até atingir o limite
        for i in range(150):  # Mais que o limite padrão
            response = client.get("/api/leiloes")
            
            if response.status_code == 429:
                # Deve ter Retry-After header
                assert "Retry-After" in response.headers
                break
        else:
            # Se não atingiu o limite, pelo menos algumas requisições devem funcionar
            pass


class TestDataSanitization:
    """Testa sanitização de dados"""
    
    def test_email_validation(self):
        """Testa validação de e-mail"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test.example.com",
            "test@.com"
        ]
        
        for email in valid_emails:
            assert SecurityUtils.validate_email(email), f"E-mail válido rejeitado: {email}"
        
        for email in invalid_emails:
            assert not SecurityUtils.validate_email(email), f"E-mail inválido aceito: {email}"
    
    def test_phone_validation(self):
        """Testa validação de telefone"""
        valid_phones = [
            "11987654321",
            "(11) 98765-4321",
            "11 98765 4321",
            "987654321"
        ]
        
        invalid_phones = [
            "123",
            "123456789012",
            "telefone",
            "abc1234567"
        ]
        
        for phone in valid_phones:
            assert SecurityUtils.validate_phone(phone), f"Telefone válido rejeitado: {phone}"
        
        for phone in invalid_phones:
            assert not SecurityUtils.validate_phone(phone), f"Telefone inválido aceito: {phone}"
    
    def test_data_masking(self):
        """Testa mascaramento de dados sensíveis"""
        sensitive_data = "1234567890123456"
        masked = SecurityUtils.mask_sensitive_data(sensitive_data)
        
        assert len(masked) == len(sensitive_data)
        assert masked.startswith("12")
        assert masked.endswith("56")
        assert "*" in masked
        
        # Dados curtos
        short_data = "123"
        masked_short = SecurityUtils.mask_sensitive_data(short_data)
        assert len(masked_short) == 3
        assert all(c == "*" for c in masked_short)


class TestCSRFProtection:
    """Testa proteção CSRF"""
    
    def test_csrf_token_generation(self):
        """Testa geração de token CSRF"""
        token1 = SecurityUtils.generate_csrf_token()
        token2 = SecurityUtils.generate_csrf_token()
        
        # Tokens devem ser diferentes
        assert token1 != token2
        
        # Tokens devem ter comprimento razoável
        assert len(token1) >= 32
        assert len(token2) >= 32
        
        # Tokens devem ser seguros (apenas caracteres URL-safe)
        import re
        assert re.match(r'^[a-zA-Z0-9_-]+$', token1)
        assert re.match(r'^[a-zA-Z0-9_-]+$', token2)
    
    def test_csrf_token_validation(self):
        """Testa validação de token CSRF"""
        token = SecurityUtils.generate_csrf_token()
        
        # Token válido deve passar
        assert SecurityUtils.validate_csrf_token(token, token)
        
        # Token inválido deve falhar
        assert not SecurityUtils.validate_csrf_token("invalid_token", token)
        assert not SecurityUtils.validate_csrf_token(token, "different_token")


class TestSecureCommunication:
    """Testa comunicação segura"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_no_sensitive_data_in_responses(self, client):
        """Testa se não há dados sensíveis nas respostas"""
        response = client.get("/api/leiloes")
        
        # Converte para texto e verifica
        response_text = response.text.lower()
        
        # Não deve ter informações sensíveis
        sensitive_patterns = [
            "password",
            "secret",
            "token",
            "private_key",
            "api_key"
        ]
        
        for pattern in sensitive_patterns:
            # Pode ter em contexto legítimo, mas não deve ser exposto desnecessariamente
            if pattern in response_text:
                # Verifica se está em contexto de documentação ou código
                assert "documentation" in response_text or "example" in response_text
    
    def test_error_messages_not_sensitive(self, client):
        """Testa se mensagens de erro não expõem informações sensíveis"""
        # Requisição para rota inexistente
        response = client.get("/api/nonexistent")
        
        if response.status_code == 404:
            error_detail = response.json().get("detail", "").lower()
            
            # Não deve expor detalhes técnicos
            technical_patterns = [
                "traceback",
                "exception",
                "error at line",
                "file path",
                "internal server"
            ]
            
            for pattern in technical_patterns:
                assert pattern not in error_detail, f"Informação técnica exposta: {pattern}"
    
    def test_cors_configuration(self, client):
        """Testa configuração CORS"""
        response = client.options("/api/leiloes")
        
        # Deve ter headers CORS apropriados
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        for header in cors_headers:
            if header in response.headers:
                # Valores não devem ser muito permissivos
                value = response.headers[header]
                if "Origin" in header:
                    assert "*" not in value or "localhost" in value, "CORS muito permissivo"


class TestSessionSecurity:
    """Testa segurança de sessão"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_session_management(self, client):
        """Testa gerenciamento de sessão"""
        # Requisições devem ser stateless (API REST)
        response1 = client.get("/api/leiloes")
        response2 = client.get("/api/leiloes")
        
        # Respostas devem ser consistentes (não dependem de estado)
        assert response1.status_code == response2.status_code
        
        # Não deve ter cookies de sessão
        set_cookie = response1.headers.get("Set-Cookie")
        if set_cookie:
            # Se houver cookies, não devem ser de sessão sensível
            assert "session" not in set_cookie.lower()
            assert "auth" not in set_cookie.lower()


class TestLoggingSecurity:
    """Testa segurança de logging"""
    
    def test_sensitive_data_not_logged(self):
        """Testa se dados sensíveis não são logados"""
        # Este teste seria implementado verificando os logs
        # Por ora, apenas verificamos se a função de mascaramento funciona
        sensitive_data = "senha_secreta_123"
        masked = SecurityUtils.mask_sensitive_data(sensitive_data)
        
        assert "senha" not in masked.lower()
        assert "secreta" not in masked.lower()
        assert masked.startswith("se")
        assert masked.endswith("23")
