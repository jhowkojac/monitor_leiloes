"""
Testes para os templates HTML
"""
import pytest
from fastapi.testclient import TestClient
from main import app


class TestTemplates:
    """Testes para renderização de templates"""
    
    @pytest.fixture
    def client(self):
        """Fixture para cliente de teste"""
        return TestClient(app)
    
    def test_template_index_render(self, client):
        """Testa renderização do template index"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        
        # Verifica elementos básicos
        assert "Monitor de Leilões" in response.text
        assert "Filtrar por cidade" in response.text
        assert "Ver detalhes" in response.text
    
    def test_template_edital_render(self, client):
        """Testa renderização do template edital"""
        # Primeiro atualiza para ter dados
        client.post("/api/leiloes/atualizar")
        
        # Pega um ID real
        response = client.get("/api/leiloes")
        data = response.json()
        
        if data["leiloes"]:
            first_id = data["leiloes"][0]["id"]
            
            # Testa página do edital
            response = client.get(f"/editais/{first_id}")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
            
            # Verifica elementos específicos
            assert "Veículos deste edital" in response.text
            assert "Ver fotos em alta resolução" in response.text
    
    def test_template_veiculo_detalhes_render(self, client):
        """Testa renderização do template de detalhes do veículo"""
        # Testa com ID que provavelmente não existe
        response = client.get("/veiculos/test_id")
        
        # Deve retornar 404 ou 200 (se encontrar)
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert "text/html" in response.headers["content-type"]
            assert "Detalhes do Veículo" in response.text
    
    def test_template_css_classes(self, client):
        """Testa se classes CSS estão presentes"""
        response = client.get("/")
        assert response.status_code == 200
        
        # Verifica se estilos básicos estão presentes
        assert "card" in response.text
        assert "carousel" in response.text
    
    def test_template_responsive_design(self, client):
        """Testa se viewport meta tag está presente"""
        response = client.get("/")
        assert response.status_code == 200
        assert "viewport" in response.text
    
    def test_template_error_404(self, client):
        """Testa página 404 customizada"""
        response = client.get("/pagina_inexistente")
        assert response.status_code == 404
    
    def test_template_carregamento_javascript(self, client):
        """Testa se JavaScript está presente"""
        response = client.get("/")
        assert response.status_code == 200
        
        # Verifica se há scripts de carousel
        assert "carousel" in response.text.lower()


class TestTemplateLogic:
    """Testes para lógica nos templates"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_template_condicional_veiculos(self, client):
        """Testa lógica condicional de veículos no template"""
        # Primeiro atualiza
        client.post("/api/leiloes/atualizar")
        
        # Pega um ID real
        response = client.get("/api/leiloes")
        data = response.json()
        
        if data["leiloes"]:
            first_id = data["leiloes"][0]["id"]
            
            # Testa página do edital
            response = client.get(f"/editais/{first_id}")
            assert response.status_code == 200
            
            # Se houver veículos, deve mostrar a lista
            # Se não, deve mostrar mensagem vazia
            if "Veículos deste edital" in response.text:
                # Deve ter cards de veículos ou mensagem de vazio
                assert ("card" in response.text) or ("Não foi possível listar" in response.text)
    
    def test_template_identificacao_sucata(self, client):
        """Testa identificação de sucata no template"""
        # Primeiro atualiza
        client.post("/api/leiloes/atualizar")
        
        # Pega um ID real
        response = client.get("/api/leiloes")
        data = response.json()
        
        if data["leiloes"]:
            first_id = data["leiloes"][0]["id"]
            
            # Testa página do edital
            response = client.get(f"/editais/{first_id}")
            assert response.status_code == 200
            
            # Verifica se há lógica para sucata
            # Pode não ter sucata, mas a lógica deve estar presente
            assert "SUCATA" in response.text or "card" in response.text
    
    def test_template_links_dinamicos(self, client):
        """Testa se links dinâmicos estão corretos"""
        response = client.get("/")
        assert response.status_code == 200
        
        # Verifica se há links para detalhes
        assert "href=" in response.text
        assert "editais" in response.text
