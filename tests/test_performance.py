"""
Testes de performance para o Monitor de Leilões
"""
import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from main import app


class TestPerformance:
    """Testes de performance e carga"""
    
    @pytest.fixture
    def client(self):
        """Fixture para cliente de teste"""
        return TestClient(app)
    
    def test_tempo_resposta_pagina_inicial(self, client):
        """Testa tempo de resposta da página inicial (< 2s)"""
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 2.0, f"Página inicial demorou {response_time:.2f}s (limite: 2s)"
    
    def test_tempo_resposta_api_leiloes(self, client):
        """Testa tempo de resposta da API de leilões (< 1s)"""
        start_time = time.time()
        response = client.get("/api/leiloes")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0, f"API de leilões demorou {response_time:.2f}s (limite: 1s)"
    
    def test_tempo_resposta_api_atualizar(self, client):
        """Testa tempo de resposta da API de atualização (< 30s)"""
        start_time = time.time()
        response = client.post("/api/leiloes/atualizar")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 30.0, f"API de atualização demorou {response_time:.2f}s (limite: 30s)"
    
    def test_tamanho_resposta_pagina_inicial(self, client):
        """Testa tamanho da resposta da página inicial (< 50KB)"""
        response = client.get("/")
        assert response.status_code == 200
        
        content_size = len(response.content)
        assert content_size < 50000, f"Página inicial tem {content_size/1024:.1f}KB (limite: 50KB)"
    
    def test_tamanho_resposta_api_leiloes(self, client):
        """Testa tamanho da resposta da API (< 100KB)"""
        response = client.get("/api/leiloes")
        assert response.status_code == 200
        
        content_size = len(response.content)
        assert content_size < 100000, f"API de leilões tem {content_size/1024:.1f}KB (limite: 100KB)"
    
    def test_concorrencia_multiplas_requisicoes(self, client):
        """Testa múltiplas requisições concorrentes"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            start_time = time.time()
            response = client.get("/api/leiloes")
            end_time = time.time()
            results.put({
                'status': response.status_code,
                'time': end_time - start_time
            })
        
        # Dispara 10 requisições concorrentes
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Espera todas terminarem
        for thread in threads:
            thread.join()
        
        # Verifica resultados
        success_count = 0
        avg_time = 0
        
        while not results.empty():
            result = results.get()
            if result['status'] == 200:
                success_count += 1
                avg_time += result['time']
        
        assert success_count >= 8, f"Apenas {success_count}/10 requisições tiveram sucesso"
        avg_time = avg_time / success_count if success_count > 0 else 0
        assert avg_time < 2.0, f"Tempo médio de {avg_time:.2f}s muito alto"
    
    @pytest.mark.asyncio
    async def test_performance_async_fonte_detran(self):
        """Testa performance da fonte Detran MG"""
        from app.fontes.detran_mg_oficial import FonteDetranMGOficial
        
        fonte = FonteDetranMGOficial()
        
        start_time = time.time()
        leiloes = await fonte.listar_leiloes()
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 20.0, f"Listagem de leilões demorou {response_time:.2f}s (limite: 20s)"
        assert len(leiloes) > 0, "Nenhum leilão encontrado"
    
    def test_memory_usage_pagina_inicial(self, client):
        """Testa uso de memória da página inicial"""
        import psutil
        import os
        
        # Pega processo atual
        process = psutil.Process(os.getpid())
        
        # Mede memória antes
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Faz várias requisições
        for _ in range(10):
            response = client.get("/")
            assert response.status_code == 200
        
        # Mede memória depois
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_increase = mem_after - mem_before
        
        assert mem_increase < 50, f"Uso de memória aumentou {mem_increase:.1f}MB (limite: 50MB)"
    
    def test_cache_eficiencia(self, client):
        """Testa eficiência do cache"""
        # Primeira requisição (sem cache)
        start_time = time.time()
        response1 = client.get("/api/leiloes")
        first_time = time.time() - start_time
        
        # Segunda requisição (com cache)
        start_time = time.time()
        response2 = client.get("/api/leiloes")
        second_time = time.time() - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Segunda deve ser mais rápida (cache)
        assert second_time < first_time, f"Cache não funcionou: {second_time:.3f}s vs {first_time:.3f}s"
        assert second_time < 0.5, f"Cache muito lento: {second_time:.3f}s"


class TestLoad:
    """Testes de carga"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_carga_requisicoes_simultaneas(self, client):
        """Testa carga com 50 requisições simultâneas"""
        import concurrent.futures
        import threading
        
        results = []
        errors = []
        
        def make_request():
            try:
                start_time = time.time()
                response = client.get("/api/leiloes")
                end_time = time.time()
                results.append({
                    'status': response.status_code,
                    'time': end_time - start_time
                })
            except Exception as e:
                errors.append(str(e))
        
        # Dispara 50 requisições
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            concurrent.futures.wait(futures)
        
        # Verifica resultados
        success_count = len([r for r in results if r['status'] == 200])
        avg_time = sum(r['time'] for r in results) / len(results) if results else 0
        
        assert success_count >= 45, f"Apenas {success_count}/50 requisições tiveram sucesso"
        assert avg_time < 3.0, f"Tempo médio muito alto: {avg_time:.2f}s"
        assert len(errors) == 0, f"Erros encontrados: {errors}"
    
    def test_stress_atualizacao_cache(self, client):
        """Testa stress na atualização do cache"""
        import threading
        
        results = []
        lock = threading.Lock()
        
        def update_cache():
            try:
                start_time = time.time()
                response = client.post("/api/leiloes/atualizar")
                end_time = time.time()
                
                with lock:
                    results.append({
                        'status': response.status_code,
                        'time': end_time - start_time
                    })
            except Exception as e:
                with lock:
                    results.append({'error': str(e)})
        
        # Dispara 5 atualizações simultâneas
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=update_cache)
            threads.append(thread)
            thread.start()
        
        # Espera todas terminarem
        for thread in threads:
            thread.join()
        
        # Verifica se pelo menos 3 tiveram sucesso
        success_count = len([r for r in results if r.get('status') == 200])
        assert success_count >= 3, f"Apenas {success_count}/5 atualizações tiveram sucesso"
        
        # Verifica se não há erros críticos
        critical_errors = [r for r in results if 'error' in r and 'timeout' in r['error'].lower()]
        assert len(critical_errors) == 0, f"Erros críticos: {critical_errors}"


class TestScalability:
    """Testes de escalabilidade"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_escalabilidade_volume_dados(self, client):
        """Testa escalabilidade com volume de dados"""
        # Primeiro, atualiza o cache
        client.post("/api/leiloes/atualizar")
        
        # Testa diferentes volumes de dados
        for filtro in [None, "estado=MG", "fonte=detran_mg"]:
            url = "/api/leiloes"
            if filtro:
                url += f"?{filtro}"
            
            start_time = time.time()
            response = client.get(url)
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            
            # Tempo não deve aumentar muito com filtros
            assert response_time < 2.0, f"Requisição com {filtro or 'sem filtro'} demorou {response_time:.2f}s"
    
    def test_escalabilidade_concorrencia_crescente(self, client):
        """Testa escalabilidade com concorrência crescente"""
        import concurrent.futures
        
        for num_requests in [1, 5, 10, 20]:
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
                futures = [executor.submit(client.get, "/api/leiloes") for _ in range(num_requests)]
                responses = [f.result() for f in futures]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            success_count = len([r for r in responses if r.status_code == 200])
            avg_per_request = total_time / num_requests
            
            assert success_count >= num_requests * 0.8, f"Com {num_requests} requisições, apenas {success_count} tiveram sucesso"
            assert avg_per_request < 1.0, f"Tempo médio por requisição: {avg_per_request:.3f}s (limite: 1s)"
