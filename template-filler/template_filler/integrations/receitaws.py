"""
ReceitaWS Integration
Cliente para busca automática de dados de CNPJ via API ReceitaWS.
"""

import logging
import requests
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ReceitaWSError(Exception):
    """Exceção específica para erros da ReceitaWS."""
    pass


class ReceitaWSClient:
    """
    Cliente para integração com ReceitaWS API.
    
    Funcionalidades:
    - Busca dados completos de empresa por CNPJ
    - Cache de resultados para evitar consultas duplicadas
    - Rate limiting automático
    - Retry logic para falhas temporárias
    """
    
    def __init__(self, cache_ttl_minutes: int = 60):
        """
        Inicializa cliente ReceitaWS.
        
        Args:
            cache_ttl_minutes: Tempo de vida do cache em minutos
        """
        self.base_url = "https://receitaws.com.br/v1/cnpj"
        self.cache = {}
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.last_request_time = None
        self.min_request_interval = 1.0  # Segundos entre requests
        
        logger.info("ReceitaWSClient inicializado")
    
    def _clean_cnpj(self, cnpj: str) -> str:
        """
        Remove formatação do CNPJ.
        
        Args:
            cnpj: CNPJ com ou sem formatação
            
        Returns:
            CNPJ apenas com dígitos
        """
        return ''.join(filter(str.isdigit, cnpj))
    
    def _is_cache_valid(self, cnpj: str) -> bool:
        """Verifica se o cache é válido para o CNPJ."""
        if cnpj not in self.cache:
            return False
        
        cache_entry = self.cache[cnpj]
        cache_time = cache_entry.get('cached_at')
        
        if not cache_time:
            return False
        
        return datetime.now() - cache_time < self.cache_ttl
    
    def _wait_rate_limit(self):
        """Implementa rate limiting."""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                wait_time = self.min_request_interval - elapsed
                logger.debug(f"Rate limiting: aguardando {wait_time:.2f}s")
                time.sleep(wait_time)
    
    def _make_request(self, cnpj: str, timeout: int = 10, retries: int = 3) -> Dict[str, Any]:
        """
        Faz requisição para ReceitaWS com retry logic.
        
        Args:
            cnpj: CNPJ limpo (apenas dígitos)
            timeout: Timeout da requisição em segundos
            retries: Número de tentativas
            
        Returns:
            Dados da empresa
            
        Raises:
            ReceitaWSError: Erro na consulta
        """
        url = f"{self.base_url}/{cnpj}"
        
        for attempt in range(retries + 1):
            try:
                self._wait_rate_limit()
                
                logger.info(f"Consultando CNPJ {cnpj} (tentativa {attempt + 1})")
                
                response = requests.get(
                    url,
                    timeout=timeout,
                    headers={
                        'User-Agent': 'Template_Filler/1.0',
                        'Accept': 'application/json'
                    }
                )
                
                self.last_request_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verificar se houve erro na API
                    if data.get('status') == 'ERROR':
                        raise ReceitaWSError(f"Erro da API: {data.get('message', 'Erro desconhecido')}")
                    
                    return data
                
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt  # Backoff exponencial
                    logger.warning(f"Rate limit atingido, aguardando {wait_time}s")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code == 404:
                    raise ReceitaWSError(f"CNPJ {cnpj} não encontrado")
                
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout na consulta CNPJ {cnpj} (tentativa {attempt + 1})")
                if attempt == retries:
                    raise ReceitaWSError(f"Timeout após {retries + 1} tentativas")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro na requisição para CNPJ {cnpj}: {e}")
                if attempt == retries:
                    raise ReceitaWSError(f"Erro de conexão: {str(e)}")
        
        raise ReceitaWSError("Número máximo de tentativas excedido")
    
    def get_company_data(self, cnpj: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Busca dados completos da empresa por CNPJ.
        
        Args:
            cnpj: CNPJ com ou sem formatação
            use_cache: Se deve usar cache
            
        Returns:
            Dicionário com dados da empresa
            
        Raises:
            ReceitaWSError: Erro na consulta
        """
        # Limpar e validar CNPJ
        clean_cnpj = self._clean_cnpj(cnpj)
        
        if len(clean_cnpj) != 14:
            raise ReceitaWSError(f"CNPJ inválido: {cnpj}")
        
        # Verificar cache
        if use_cache and self._is_cache_valid(clean_cnpj):
            logger.info(f"Usando dados do cache para CNPJ {clean_cnpj}")
            return self.cache[clean_cnpj]['data']
        
        # Fazer requisição
        try:
            data = self._make_request(clean_cnpj)
            
            # Armazenar no cache
            self.cache[clean_cnpj] = {
                'data': data,
                'cached_at': datetime.now()
            }
            
            logger.info(f"Dados obtidos com sucesso para CNPJ {clean_cnpj}")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do CNPJ {clean_cnpj}: {e}")
            raise
    
    def extract_template_fields(self, cnpj_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extrai campos no formato esperado pelos templates.
        
        Args:
            cnpj_data: Dados brutos da ReceitaWS
            
        Returns:
            Dicionário com campos formatados para templates
        """
        try:
            # Mapear campos da ReceitaWS para campos dos templates
            template_fields = {}
            
            # Dados básicos da empresa
            if cnpj_data.get('nome'):
                template_fields['razaoSocial'] = cnpj_data['nome']
                template_fields['contratante_razaoSocial'] = cnpj_data['nome']
                template_fields['contratada_razaoSocial'] = cnpj_data['nome']
            
            if cnpj_data.get('fantasia'):
                template_fields['nomeFantasia'] = cnpj_data['fantasia']
            
            # CNPJ formatado
            if cnpj_data.get('cnpj'):
                cnpj_formatted = cnpj_data['cnpj']
                template_fields['cnpj'] = cnpj_formatted
                template_fields['contratante_cnpj'] = cnpj_formatted
                template_fields['contratada_cnpj'] = cnpj_formatted
            
            # Endereço
            if cnpj_data.get('logradouro'):
                logradouro = cnpj_data['logradouro']
                numero = cnpj_data.get('numero', 'S/N')
                complemento = cnpj_data.get('complemento', '')
                bairro = cnpj_data.get('bairro', '')
                
                # Montar endereço completo
                endereco_parts = [logradouro]
                if numero and numero != 'S/N':
                    endereco_parts.append(numero)
                if complemento:
                    endereco_parts.append(complemento)
                if bairro:
                    endereco_parts.append(bairro)
                
                endereco_completo = ', '.join(endereco_parts)
                
                template_fields['logradouro'] = endereco_completo
                template_fields['contratante_logradouro'] = endereco_completo
                template_fields['contratada_logradouro'] = endereco_completo
            
            # Cidade e UF
            if cnpj_data.get('municipio'):
                template_fields['cidade'] = cnpj_data['municipio']
                template_fields['contratante_cidade'] = cnpj_data['municipio']
                template_fields['contratada_cidade'] = cnpj_data['municipio']
            
            if cnpj_data.get('uf'):
                template_fields['uf'] = cnpj_data['uf']
                template_fields['contratante_uf'] = cnpj_data['uf']
                template_fields['contratada_uf'] = cnpj_data['uf']
            
            # CEP
            if cnpj_data.get('cep'):
                cep = cnpj_data['cep']
                template_fields['cep'] = cep
                template_fields['contratante_cep'] = cep
                template_fields['contratada_cep'] = cep
            
            # Telefone
            if cnpj_data.get('telefone'):
                template_fields['telefone'] = cnpj_data['telefone']
            
            # Email
            if cnpj_data.get('email'):
                template_fields['email'] = cnpj_data['email']
            
            # Dados adicionais
            if cnpj_data.get('atividade_principal'):
                atividades = cnpj_data['atividade_principal']
                if atividades and len(atividades) > 0:
                    template_fields['atividade_principal'] = atividades[0].get('text', '')
            
            if cnpj_data.get('situacao'):
                template_fields['situacao'] = cnpj_data['situacao']
            
            logger.info(f"Extraídos {len(template_fields)} campos do CNPJ")
            return template_fields
            
        except Exception as e:
            logger.error(f"Erro ao extrair campos do template: {e}")
            return {}
    
    def search_and_extract(self, cnpj: str) -> Dict[str, str]:
        """
        Busca dados do CNPJ e extrai campos formatados para templates.
        
        Args:
            cnpj: CNPJ com ou sem formatação
            
        Returns:
            Dicionário com campos prontos para uso em templates
            
        Raises:
            ReceitaWSError: Erro na consulta
        """
        raw_data = self.get_company_data(cnpj)
        return self.extract_template_fields(raw_data)
    
    def clear_cache(self):
        """Limpa o cache de consultas."""
        self.cache.clear()
        logger.info("Cache ReceitaWS limpo")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache."""
        total_entries = len(self.cache)
        valid_entries = sum(1 for cnpj in self.cache.keys() if self._is_cache_valid(cnpj))
        
        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": total_entries - valid_entries,
            "cache_ttl_minutes": self.cache_ttl.total_seconds() / 60
        }