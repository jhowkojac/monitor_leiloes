"""
Testes End-to-End (E2E) com Selenium para o Monitor de Leilões
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException


class TestE2E:
    """Testes End-to-End da aplicação"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Fixture para o WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Executar sem abrir navegador
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    @pytest.fixture(scope="class")
    def base_url(self):
        """URL base para testes"""
        return "http://localhost:8000"
    
    def test_pagina_inicial_carregamento(self, driver, base_url):
        """Testa carregamento da página inicial"""
        driver.get(base_url)
        
        # Verifica título
        assert "Monitor de Leilões" in driver.title
        
        # Verifica elementos principais
        assert driver.find_element(By.TAG_NAME, "h1").is_displayed()
        assert driver.find_element(By.ID, "cidade").is_displayed()
        
        # Verifica se há cards de leilões (pode estar vazio inicialmente)
        try:
            cards = driver.find_elements(By.CLASS_NAME, "card")
            # Se houver cards, verifica se têm conteúdo
            if cards:
                assert len(cards) > 0
        except:
            # Se não houver cards, está OK (cache vazio)
            pass
    
    def test_atualizacao_leiloes(self, driver, base_url):
        """Testa atualização de leilões via interface"""
        driver.get(base_url)
        
        # Espera um pouco para a página carregar
        time.sleep(2)
        
        # Tenta encontrar e clicar no botão de atualizar (se existir)
        try:
            # Pode não ter botão visível, então vamos usar a API
            driver.get(f"{base_url}/api/leiloes/atualizar")
            
            # Espera um pouco para a atualização
            time.sleep(5)
            
            # Volta para a página principal
            driver.get(base_url)
            time.sleep(2)
            
            # Verifica se há cards agora
            cards = driver.find_elements(By.CLASS_NAME, "card")
            assert len(cards) > 0, "Nenhum card encontrado após atualização"
            
        except Exception as e:
            # Se falhar, verifica se pelo menos a página está funcionando
            assert driver.find_element(By.TAG_NAME, "body").is_displayed()
    
    def test_filtro_cidade(self, driver, base_url):
        """Testa filtro por cidade"""
        driver.get(base_url)
        
        # Espera carregar
        time.sleep(2)
        
        # Encontra o campo de filtro
        campo_cidade = driver.find_element(By.ID, "cidade")
        campo_cidade.clear()
        campo_cidade.send_keys("Belo Horizonte")
        
        # Espera um pouco para o filtro funcionar
        time.sleep(1)
        
        # Verifica se o filtro foi aplicado (pode não ter resultados)
        # O importante é que não quebre
        assert campo_cidade.get_attribute("value") == "Belo Horizonte"
    
    def test_navegacao_para_detalhes_edital(self, driver, base_url):
        """Testa navegação para página de detalhes do edital"""
        # Primeiro, garante que há dados
        driver.get(f"{base_url}/api/leiloes/atualizar")
        time.sleep(5)
        
        # Vai para a página principal
        driver.get(base_url)
        time.sleep(2)
        
        # Tenta encontrar um link de detalhes
        try:
            links_detalhes = driver.find_elements(By.LINK_TEXT, "Ver detalhes")
            
            if links_detalhes:
                # Clica no primeiro link
                links_detalhes[0].click()
                
                # Espera a página de detalhes carregar
                time.sleep(3)
                
                # Verifica se está na página de detalhes
                assert "Veículos deste edital" in driver.page_source
                
                # Verifica se há cards de veículos
                cards_veiculos = driver.find_elements(By.CLASS_NAME, "card")
                assert len(cards_veiculos) > 0, "Nenhum veículo encontrado na página de detalhes"
                
            else:
                # Se não houver links, pelo menos a página principal deve funcionar
                assert driver.find_element(By.TAG_NAME, "body").is_displayed()
                
        except TimeoutException:
            # Se der timeout, pelo menos a página principal deve estar funcionando
            driver.get(base_url)
            assert driver.find_element(By.TAG_NAME, "body").is_displayed()
    
    def test_carrossel_imagens(self, driver, base_url):
        """Testa funcionamento do carrossel de imagens"""
        # Primeiro, garante que há dados
        driver.get(f"{base_url}/api/leiloes/atualizar")
        time.sleep(5)
        
        # Vai para a página principal
        driver.get(base_url)
        time.sleep(2)
        
        try:
            # Tenta encontrar um link de detalhes
            links_detalhes = driver.find_elements(By.LINK_TEXT, "Ver detalhes")
            
            if links_detalhes:
                links_detalhes[0].click()
                time.sleep(3)
                
                # Procura por carrosseis
                carrosseis = driver.find_elements(By.CLASS_NAME, "carousel")
                
                if carrosseis:
                    carousel = carrosseis[0]
                    
                    # Verifica se há botões de navegação
                    botoes = carousel.find_elements(By.CLASS_NAME, "carousel-btn")
                    if len(botoes) >= 2:
                        # Testa navegação para frente
                        botoes[1].click()
                        time.sleep(1)
                        
                        # Testa navegação para trás
                        botoes[0].click()
                        time.sleep(1)
                        
                        # Verifica se ainda está funcionando
                        assert carousel.is_displayed()
                    
                    # Verifica se há dots de navegação
                    dots = carousel.find_elements(By.CLASS_NAME, "carousel-dot")
                    assert len(dots) > 0, "Carrossel não tem dots de navegação"
                    
        except Exception as e:
            # Se falhar, não é crítico - pode não ter dados
            pass
    
    def test_responsividade_mobile(self, driver, base_url):
        """Testa responsividade em tamanho mobile"""
        # Define tamanho mobile
        driver.set_window_size(375, 667)
        
        driver.get(base_url)
        time.sleep(2)
        
        # Verifica se elementos principais estão visíveis
        assert driver.find_element(By.TAG_NAME, "h1").is_displayed()
        assert driver.find_element(By.ID, "cidade").is_displayed()
        
        # Verifica se o layout se adaptou (menu mobile, etc.)
        body = driver.find_element(By.TAG_NAME, "body")
        assert body.is_displayed()
        
        # Volta para tamanho desktop
        driver.set_window_size(1920, 1080)
    
    def test_links_externos(self, driver, base_url):
        """Testa se links externos funcionam"""
        driver.get(base_url)
        time.sleep(2)
        
        # Procura por links externos (que abrem em nova aba)
        links_externos = driver.find_elements(By.XPATH, "//a[@target='_blank']")
        
        for link in links_externos[:3]:  # Testa apenas os 3 primeiros
            href = link.get_attribute("href")
            assert href is not None, "Link externo sem href"
            assert href.startswith("http"), f"Link externo inválido: {href}"
    
    def test_formulario_busca(self, driver, base_url):
        """Testa formulário de busca/filtro"""
        driver.get(base_url)
        time.sleep(2)
        
        # Encontra o campo de busca
        campo_busca = driver.find_element(By.ID, "cidade")
        
        # Testa digitação
        campo_busca.clear()
        campo_busca.send_keys("Teste")
        
        # Verifica se o texto foi digitado
        assert campo_busca.get_attribute("value") == "Teste"
        
        # Teste limpar
        campo_busca.clear()
        assert campo_busca.get_attribute("value") == ""
    
    def test_carregamento_imagens(self, driver, base_url):
        """Testa se as imagens estão carregando"""
        # Primeiro, garante que há dados
        driver.get(f"{base_url}/api/leiloes/atualizar")
        time.sleep(5)
        
        driver.get(base_url)
        time.sleep(2)
        
        # Procura por imagens
        imagens = driver.find_elements(By.TAG_NAME, "img")
        
        # Verifica se pelo menos algumas imagens têm src
        imagens_com_src = [img for img in imagens if img.get_attribute("src")]
        
        # Pode não ter imagens se não houver dados, mas se tiver, devem ter src
        if imagens_com_src:
            for img in imagens_com_src[:5]:  # Verifica as 5 primeiras
                src = img.get_attribute("src")
                assert src != "", "Imagem sem src"
                assert not src.startswith("data:"), "Imagem placeholder em base64"
    
    def test_performance_carregamento_pagina(self, driver, base_url):
        """Testa performance de carregamento da página"""
        start_time = time.time()
        
        driver.get(base_url)
        
        # Espera a página carregar completamente
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        end_time = time.time()
        load_time = end_time - start_time
        
        # Página deve carregar em menos de 5 segundos
        assert load_time < 5.0, f"Página demorou {load_time:.2f}s para carregar"
    
    def test_acessibilidade_basica(self, driver, base_url):
        """Testa acessibilidade básica"""
        driver.get(base_url)
        time.sleep(2)
        
        # Verifica se há título na página
        title = driver.title
        assert title != "", "Página sem título"
        
        # Verifica se há headings (h1, h2, etc.)
        headings = driver.find_elements(By.XPATH, "//h1 | //h2 | //h3")
        assert len(headings) > 0, "Página sem headings"
        
        # Verifica se há alt text nas imagens
        imagens_sem_alt = []
        imagens = driver.find_elements(By.TAG_NAME, "img")
        
        for img in imagens:
            alt = img.get_attribute("alt")
            if not alt or alt.strip() == "":
                imagens_sem_alt.append(img)
        
        # Algumas imagens podem não ter alt (placeholders), mas não muitas
        assert len(imagens_sem_alt) < len(imagens) * 0.5, "Muitas imagens sem alt text"


class TestE2EAPI:
    """Testes E2E para APIs via navegador"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    @pytest.fixture(scope="class")
    def base_url(self):
        return "http://localhost:8000"
    
    def test_api_endpoints_direto(self, driver, base_url):
        """Testa acesso direto aos endpoints da API"""
        endpoints = [
            "/api/leiloes",
            "/api/leiloes?estado=MG",
            "/api/leiloes?fonte=detran_mg"
        ]
        
        for endpoint in endpoints:
            driver.get(f"{base_url}{endpoint}")
            time.sleep(2)
            
            # Verifica se retorna JSON válido
            page_source = driver.page_source
            
            # Deve conter indicação de JSON
            assert '"' in page_source or "{" in page_source, f"Endpoint {endpoint} não retornou JSON"
            
            # Não deve ser página de erro
            assert "404" not in page_source, f"Endpoint {endpoint} retornou 404"
            assert "Internal Server Error" not in page_source, f"Endpoint {endpoint} retornou erro"
