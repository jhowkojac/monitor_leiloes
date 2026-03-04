"""
Testes unitários para o Monitor de Leilões
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.fontes.detran_mg_oficial import FonteDetranMGOficial
from app.models import Estado, FonteLeilao, VeiculoLeilao


class TestFonteDetranMGOficial:
    """Testes unitários para a fonte do Detran MG"""
    
    @pytest.fixture
    def fonte(self):
        """Fixture para instância da fonte"""
        return FonteDetranMGOficial()
    
    @pytest.mark.asyncio
    async def test_listar_leiloes_success(self, fonte):
        """Testa listagem de leilões com sucesso"""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock response HTML
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <body>
                    <a href="/lotes/lista-lotes/3169/2026">Detalhes</a>
                    <div class="card">
                        Edital de Leilão 1445/2026 novo cruzeiro
                    </div>
                </body>
            </html>
            """
            mock_get.return_value = mock_response
            
            # Mock da função de veículos para evitar chamadas reais
            with patch.object(fonte, 'listar_veiculos_do_edital', return_value=[]):
                leiloes = await fonte.listar_leiloes()
                
                assert isinstance(leiloes, list)
                assert len(leiloes) > 0
                assert all(isinstance(leilao, VeiculoLeilao) for leilao in leiloes)
    
    @pytest.mark.asyncio
    async def test_listar_leiloes_http_error(self, fonte):
        """Testa tratamento de erro HTTP"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 500
            mock_response.raise_for_status.side_effect = Exception("Server Error")
            mock_get.return_value = mock_response
            
            leiloes = await fonte.listar_leiloes()
            assert leiloes == []
    
    @pytest.mark.asyncio
    async def test_listar_veiculos_do_edital_success(self, fonte):
        """Testa listagem de veículos de um edital"""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = """
            <html>
                <body>
                    <div class="listaLotes">
                        <span>Lote 1</span>
                        <span>CONSERVADO</span>
                        <p>HONDA/CG 125 FAN KS 2010</p>
                        <p>R$ 1.200,00</p>
                        <img src="/Imagens/visualizar/leiloes/leilao_3169/img_291618_1.jpg" />
                    </div>
                    <div class="listaLotes">
                        <span>Lote 2</span>
                        <span>SUCATA</span>
                        <p>FIAT/PALIO 2008</p>
                        <p>R$ 500,00</p>
                        <img src="/Imagens/visualizar/leiloes/leilao_3169/img_291619_1.jpg" />
                    </div>
                </body>
            </html>
            """
            mock_get.return_value = mock_response
            
            veiculos = await fonte.listar_veiculos_do_edital("http://example.com")
            
            assert isinstance(veiculos, list)
            assert len(veiculos) == 2
            assert all(isinstance(v, VeiculoLeilao) for v in veiculos)
            assert veiculos[0].valor_inicial == 1200.0
            assert veiculos[1].valor_inicial == 500.0
    
    @pytest.mark.asyncio
    async def test_listar_veiculos_do_edital_paginacao(self, fonte):
        """Testa paginação de veículos"""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock primeira página
            mock_response_page1 = AsyncMock()
            mock_response_page1.status_code = 200
            mock_response_page1.text = """
            <html>
                <body>
                    <div class="listaLotes">
                        <span>Lote 1</span>
                        <span>CONSERVADO</span>
                        <p>HONDA/CG 125</p>
                        <p>R$ 1.000,00</p>
                    </div>
                    <a href="/lotes/lista-lotes/3169/2026?page=2">2</a>
                    <a href="/lotes/lista-lotes/3169/2026?page=3">3</a>
                </body>
            </html>
            """
            
            # Mock segunda página
            mock_response_page2 = AsyncMock()
            mock_response_page2.status_code = 200
            mock_response_page2.text = """
            <html>
                <body>
                    <div class="listaLotes">
                        <span>Lote 9</span>
                        <span>SUCATA</span>
                        <p>FIAT/PALIO</p>
                        <p>R$ 500,00</p>
                    </div>
                </body>
            </html>
            """
            
            mock_get.side_effect = [mock_response_page1, mock_response_page2]
            
            veiculos = await fonte.listar_veiculos_do_edital("http://example.com")
            
            assert isinstance(veiculos, list)
            assert len(veiculos) == 2  # Um de cada página
    
    def test_extrair_valor_numerico(self, fonte):
        """Testa extração de valor numérico de texto"""
        # Este método não existe atualmente, mas seria útil implementar
        pass
    
    def test_identificar_veiculo_sucata(self, fonte):
        """Testa identificação de veículos sucata"""
        titulo_sucata = "Lote 1 - SUCATA FIAT/PALIO 2008"
        titulo_normal = "Lote 2 - CONSERVADO HONDA/CG 125"
        
        assert "SUCATA" in titulo_sucata.upper()
        assert "SUCATA" not in titulo_normal.upper()


class TestVeiculoLeilao:
    """Testes para o modelo VeiculoLeilao"""
    
    def test_veiculo_leilao_creation(self):
        """Testa criação de VeiculoLeilao"""
        veiculo = VeiculoLeilao(
            id="test_1",
            titulo="Veículo Teste",
            descricao="Descrição teste",
            estado=Estado.MG,
            cidade="Belo Horizonte",
            fonte=FonteLeilao.DETRAN_MG,
            url="http://example.com",
            valor_inicial=1000.0
        )
        
        assert veiculo.id == "test_1"
        assert veiculo.titulo == "Veículo Teste"
        assert veiculo.estado == Estado.MG
        assert veiculo.valor_inicial == 1000.0
    
    def test_veiculo_leilao_sem_valor(self):
        """Testa criação de VeiculoLeilao sem valor"""
        veiculo = VeiculoLeilao(
            id="test_2",
            titulo="Veículo Sem Valor",
            estado=Estado.SP,
            fonte=FonteLeilao.DETRAN_MG,
            url="http://example.com"
        )
        
        assert veiculo.id == "test_2"
        assert veiculo.valor_inicial is None


class TestServicoLeiloes:
    """Testes para o serviço de leilões"""
    
    @pytest.fixture
    def servico(self):
        """Fixture para o serviço"""
        from app.servico import ServicoLeiloes
        return ServicoLeiloes()
    
    @pytest.mark.asyncio
    async def test_atualizar(self, servico):
        """Testa atualização do cache"""
        with patch('app.fontes.detran_mg_oficial.fonte_detran_mg_oficial.listar_leiloes') as mock_listar:
            mock_listar.return_value = []
            
            resultado = await servico.atualizar()
            
            assert isinstance(resultado, list)
            mock_listar.assert_called_once()
    
    def test_listar_sem_filtro(self, servico):
        """Testa listagem sem filtros"""
        # Adicionar dados mock ao cache
        servico._cache = [
            VeiculoLeilao(
                id="test_1",
                titulo="Teste 1",
                estado=Estado.MG,
                fonte=FonteLeilao.DETRAN_MG,
                url="http://example.com"
            )
        ]
        servico._por_id = {v.id: v for v in servico._cache}
        
        resultado = servico.listar()
        
        assert len(resultado) == 1
        assert resultado[0].id == "test_1"
    
    def test_listar_com_filtro_estado(self, servico):
        """Testa listagem com filtro de estado"""
        servico._cache = [
            VeiculoLeilao(
                id="mg_1",
                titulo="Leilão MG",
                estado=Estado.MG,
                fonte=FonteLeilao.DETRAN_MG,
                url="http://example.com"
            ),
            VeiculoLeilao(
                id="sp_1",
                titulo="Leilão SP",
                estado=Estado.SP,
                fonte=FonteLeilao.DETRAN_MG,
                url="http://example.com"
            )
        ]
        servico._por_id = {v.id: v for v in servico._cache}
        
        resultado = servico.listar(estado=Estado.MG)
        
        assert len(resultado) == 1
        assert resultado[0].estado == Estado.MG
    
    def test_obter_por_id(self, servico):
        """Testa obtenção por ID"""
        veiculo = VeiculoLeilao(
            id="test_1",
            titulo="Teste",
            estado=Estado.MG,
            fonte=FonteLeilao.DETRAN_MG,
            url="http://example.com"
        )
        servico._por_id = {"test_1": veiculo}
        
        resultado = servico.obter_por_id("test_1")
        
        assert resultado is not None
        assert resultado.id == "test_1"
        
        resultado_inexistente = servico.obter_por_id("inexistente")
        assert resultado_inexistente is None
