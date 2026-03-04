"""
Testes de integração para as APIs do Monitor de Leilões
"""
import pytest
from fastapi.testclient import TestClient
from main import app


class TestAPIIntegration:
    """Testes de integração para as APIs"""
    
    @pytest.fixture
    def client(self):
        """Fixture para cliente de teste"""
        return TestClient(app)
    
    def test_pagina_inicial(self, client):
        """Testa página inicial"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Monitor de Leilões" in response.text
        assert "text/html" in response.headers["content-type"]
    
    def test_api_leiloes_empty(self, client):
        """Testa API de leilões com cache vazio"""
        response = client.get("/api/leiloes")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "leiloes" in data
        assert isinstance(data["leiloes"], list)
    
    def test_api_leiloes_after_update(self, client):
        """Testa API de leilões após atualização"""
        # Primeiro atualiza
        response = client.post("/api/leiloes/atualizar")
        assert response.status_code == 200
        
        # Depois lista
        response = client.get("/api/leiloes")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] > 0
        assert len(data["leiloes"]) > 0
    
    def test_api_leilao_por_id(self, client):
        """Testa API de leilão por ID"""
        # Primeiro atualiza para ter dados
        client.post("/api/leiloes/atualizar")
        
        # Pega o primeiro ID
        response = client.get("/api/leiloes")
        data = response.json()
        
        if data["leiloes"]:
            first_id = data["leiloes"][0]["id"]
            
            # Testa obter por ID
            response = client.get(f"/api/leiloes/{first_id}")
            assert response.status_code == 200
            leilao = response.json()
            assert leilao["id"] == first_id
    
    def test_api_leilao_inexistente(self, client):
        """Testa API de leilão com ID inexistente"""
        response = client.get("/api/leiloes/id_inexistente")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"].lower()
    
    def test_pagina_edital_inexistente(self, client):
        """Testa página de edital inexistente"""
        response = client.get("/editais/id_inexistente")
        assert response.status_code == 404
    
    def test_api_filtro_estado(self, client):
        """Testa API com filtro de estado"""
        # Primeiro atualiza
        client.post("/api/leiloes/atualizar")
        
        # Testa filtro MG
        response = client.get("/api/leiloes?estado=MG")
        assert response.status_code == 200
        data = response.json()
        
        # Verifica se todos são MG
        for leilao in data["leiloes"]:
            assert leilao["estado"] == "MG"
    
    def test_api_filtro_fonte(self, client):
        """Testa API com filtro de fonte"""
        # Primeiro atualiza
        client.post("/api/leiloes/atualizar")
        
        # Testa filtro Detran MG
        response = client.get("/api/leiloes?fonte=detran_mg")
        assert response.status_code == 200
        data = response.json()
        
        # Verifica se todos são Detran MG
        for leilao in data["leiloes"]:
            assert leilao["fonte"] == "detran_mg"
    
    def test_api_filtro_cidade(self, client):
        """Testa API com filtro de cidade"""
        # Primeiro atualiza
        client.post("/api/leiloes/atualizar")
        
        # Testa filtro por cidade (se existir)
        response = client.get("/api/leiloes")
        data = response.json()
        
        if data["leiloes"]:
            # Pega uma cidade existente
            cidade = data["leiloes"][0].get("cidade")
            if cidade:
                response = client.get(f"/api/leiloes?cidade={cidade}")
                assert response.status_code == 200
                filtered_data = response.json()
                
                # Verifica se todos são da cidade
                for leilao in filtered_data["leiloes"]:
                    assert cidade.lower() in leilao.get("cidade", "").lower()


class TestPaginaEdital:
    """Testes para página de detalhes do edital"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_pagina_edital_sucesso(self, client):
        """Testa página de edital com sucesso"""
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
            assert "text/html" in response.headers["content-type"]
            assert "Veículos deste edital" in response.text
    
    def test_pagina_veiculo_detalhes(self, client):
        """Testa página de detalhes do veículo"""
        # Primeiro atualiza
        client.post("/api/leiloes/atualizar")
        
        # Pega um ID de edital
        response = client.get("/api/leiloes")
        data = response.json()
        
        if data["leiloes"]:
            # Testa página de detalhes (pode não funcionar sem ID real)
            response = client.get("/veiculos/test_id")
            # Pode retornar 404, mas não deve quebrar
            assert response.status_code in [200, 404]


class TestPerformance:
    """Testes básicos de performance"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_tempo_resposta_pagina_inicial(self, client):
        """Testa tempo de resposta da página inicial"""
        import time
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Menos de 2 segundos
    
    def test_tempo_resposta_api_leiloes(self, client):
        """Testa tempo de resposta da API"""
        import time
        start_time = time.time()
        response = client.get("/api/leiloes")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Menos de 1 segundo
