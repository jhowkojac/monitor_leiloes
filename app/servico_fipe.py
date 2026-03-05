"""
Serviço de integração com a BrasilAPI para consulta de valores FIPE
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ServicoFIPE:
    """Serviço para consulta de valores FIPE via BrasilAPI"""
    
    def __init__(self):
        self.base_url = "https://brasilapi.com.br/api/fipe"
        self.timeout = 10.0
    
    async def buscar_valor_fipe(self, marca: str, modelo: str, ano: str, combustivel: str = "Gasolina") -> Optional[Dict[str, Any]]:
        """
        Busca valor FIPE usando BrasilAPI
        
        Args:
            marca: Marca do veículo (ex: "Volkswagen")
            modelo: Modelo do veículo (ex: "Gol")
            ano: Ano do modelo (ex: "2020")
            combustivel: Tipo de combustível (padrão: "Gasolina")
            
        Returns:
            Dict com dados FIPE ou None se não encontrar
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Primeiro, busca a marca
                marca_codigo = await self._buscar_marca_codigo(marca)
                if not marca_codigo:
                    logger.warning(f"Marca não encontrada: {marca}")
                    return None
                
                # Depois, busca o modelo
                modelo_codigo = await self._buscar_modelo_codigo(marca_codigo, modelo)
                if not modelo_codigo:
                    logger.warning(f"Modelo não encontrado: {modelo}")
                    return None
                
                # Por fim, busca o ano específico
                ano_info = await self._buscar_ano_info(marca_codigo, modelo_codigo, ano)
                if not ano_info:
                    logger.warning(f"Ano não encontrado: {ano}")
                    return None
                
                # Busca o valor final
                valor_fipe = await self._buscar_valor_final(marca_codigo, modelo_codigo, ano_info["codigo"])
                
                return valor_fipe
                
        except Exception as e:
            logger.error(f"Erro ao buscar valor FIPE: {e}")
            return None
    
    async def _buscar_marca_codigo(self, marca: str) -> Optional[str]:
        """Busca código da marca pelo nome"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/marcas/v1")
                response.raise_for_status()
                
                marcas = response.json()
                for marca_info in marcas:
                    if marca.lower() in marca_info["nome"].lower():
                        return marca_info["codigo"]
                
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar marcas: {e}")
            return None
    
    async def _buscar_modelo_codigo(self, marca_codigo: str, modelo: str) -> Optional[str]:
        """Busca código do modelo pelo nome"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/modelos/v1/{marca_codigo}")
                response.raise_for_status()
                
                data = response.json()
                for modelo_info in data["modelos"]:
                    if modelo.lower() in modelo_info["nome"].lower():
                        return modelo_info["codigo"]
                
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar modelos: {e}")
            return None
    
    async def _buscar_ano_info(self, marca_codigo: str, modelo_codigo: str, ano: str) -> Optional[Dict[str, str]]:
        """Busca informações do ano"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/anos/v1/{marca_codigo}/{modelo_codigo}")
                response.raise_for_status()
                
                anos = response.json()
                for ano_info in anos:
                    if ano in ano_info["nome"]:
                        return {
                            "codigo": ano_info["codigo"],
                            "nome": ano_info["nome"]
                        }
                
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar anos: {e}")
            return None
    
    async def _buscar_valor_final(self, marca_codigo: str, modelo_codigo: str, ano_codigo: str) -> Optional[Dict[str, Any]]:
        """Busca valor final do veículo"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/preco/v1/{marca_codigo}/{modelo_codigo}/{ano_codigo}")
                response.raise_for_status()
                
                data = response.json()
                return {
                    "valor": data["valor"],
                    "marca": data["marca"],
                    "modelo": data["modelo"],
                    "ano_modelo": data["ano_modelo"],
                    "combustivel": data["combustivel"],
                    "codigo_fipe": data["codigo_fipe"],
                    "mes_referencia": data["mes_referencia"],
                    "tipo_veiculo": data["tipo_veiculo"],
                    "sigla_combustivel": data["sigla_combustivel"],
                    "data_consulta": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erro ao buscar valor final: {e}")
            return None
    
    async def get_mock_fipe_value(self, marca: str, modelo: str, ano: str) -> Optional[Dict[str, Any]]:
        """
        Mock para valores FIPE quando a API falhar
        Retorna valores estimados baseados em regras simples
        """
        try:
            # Valores base por categoria
            valores_base = {
                "popular": {"min": 15000, "max": 35000},
                "sedan": {"min": 30000, "max": 80000},
                "suv": {"min": 40000, "max": 120000},
                "luxo": {"min": 80000, "max": 300000}
            }
            
            # Determina categoria baseado no modelo
            categoria = "popular"
            modelo_lower = modelo.lower()
            
            if any(palavra in modelo_lower for palavra in ["gol", "palio", "uno", "celta", "fox"]):
                categoria = "popular"
            elif any(palavra in modelo_lower for palavra in ["corolla", "civic", "jetta", "siena", "logan"]):
                categoria = "sedan"
            elif any(palavra in modelo_lower for palavra in ["t-cross", "hr-v", "creta", "duster", "compass"]):
                categoria = "suv"
            elif any(palavra in modelo_lower for palavra in ["bmw", "mercedes", "audi", "lexus"]):
                categoria = "luxo"
            
            # Calcula valor baseado no ano
            ano_int = int(ano) if ano.isdigit() else 2020
            ano_base = 2020
            fator_ano = 1 - ((ano_base - ano_int) * 0.08)  # 8% de depreciação por ano
            fator_ano = max(0.3, min(1.2, fator_ano))  # Limita entre 30% e 120%
            
            # Gera valor aleatório dentro da faixa
            import random
            faixa = valores_base[categoria]
            valor_base = random.uniform(faixa["min"], faixa["max"])
            valor_final = valor_base * fator_ano
            
            return {
                "valor": f"R$ {valor_final:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."),
                "marca": marca,
                "modelo": modelo,
                "ano_modelo": ano,
                "combustivel": "Gasolina",
                "codigo_fipe": f"MOCK{random.randint(100000, 999999)}",
                "mes_referencia": f"{datetime.now().strftime('%m/%Y')}",
                "tipo_veiculo": "Automóvel",
                "sigla_combustivel": "G",
                "data_consulta": datetime.now().isoformat(),
                "mock": True
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar mock FIPE: {e}")
            return None

# Instância global do serviço
servico_fipe = ServicoFIPE()
