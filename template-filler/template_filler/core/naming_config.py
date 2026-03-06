"""
Naming Configuration Manager
Sistema de configuração para nomenclatura personalizada de arquivos.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class NamingConfigManager:
    """
    Gerenciador de configurações de nomenclatura de arquivos.
    
    Funcionalidades:
    - Salvar configurações por tipo de template
    - Carregar configurações existentes
    - Gerar nomes baseados em configurações
    - Validar configurações
    """
    
    def __init__(self, config_dir: str = "config"):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_dir: Diretório para salvar configurações
        """
        # Usar caminho absoluto se não for absoluto
        if not os.path.isabs(config_dir):
            # Obter diretório do projeto (3 níveis acima)
            project_root = Path(__file__).parent.parent.parent
            self.config_dir = project_root / config_dir
        else:
            self.config_dir = Path(config_dir)
            
        self.config_dir.mkdir(exist_ok=True)
        
        logger.info(f"Inicializando NamingConfigManager em: {self.config_dir}")
    
    def get_template_config_path(self, template_name: str) -> Path:
        """
        Retorna caminho do arquivo de configuração para um template.
        
        Args:
            template_name: Nome do template
            
        Returns:
            Path do arquivo de configuração
        """
        # Normalizar nome do template
        config_name = template_name.replace("TEMPLATE_", "").replace("-", "_").replace(" ", "_").upper()
        return self.config_dir / f"naming_{config_name}.json"
    
    def load_naming_config(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Carrega configuração de nomenclatura para um template.
        
        Args:
            template_name: Nome do template
            
        Returns:
            Configuração carregada ou None se não existir
        """
        config_path = self.get_template_config_path(template_name)
        
        if not config_path.exists():
            logger.info(f"Configuração não encontrada para {template_name}")
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Configuração carregada para {template_name}: {config['naming_fields']}")
            return config
            
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            return None
    
    def save_naming_config(self, template_name: str, naming_fields: List[str], 
                          sample_data: Optional[Dict[str, str]] = None) -> bool:
        """
        Salva configuração de nomenclatura para um template.
        
        Args:
            template_name: Nome do template
            naming_fields: Lista de campos para nomenclatura (em ordem)
            sample_data: Dados de exemplo para teste
            
        Returns:
            True se salvou com sucesso
        """
        config_path = self.get_template_config_path(template_name)
        
        config = {
            "template_name": template_name,
            "naming_fields": naming_fields,
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # Adicionar exemplo se fornecido
        if sample_data:
            sample_name = self.generate_filename(naming_fields, sample_data)
            config["sample_filename"] = sample_name
            config["sample_data"] = sample_data
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuração salva para {template_name}: {naming_fields}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
            return False
    
    def generate_filename(self, naming_fields: List[str], data: Dict[str, str], 
                         include_date: bool = True) -> str:
        """
        Gera nome de arquivo baseado na configuração.
        
        Args:
            naming_fields: Lista de campos para o nome
            data: Dados coletados
            include_date: Se deve incluir data no final
            
        Returns:
            Nome do arquivo gerado
        """
        name_parts = []
        
        # Processar cada campo configurado
        for field_name in naming_fields:
            if field_name in data and data[field_name].strip():
                value = self._sanitize_filename_part(data[field_name])
                if value:
                    name_parts.append(value)
        
        # Se não conseguiu nenhum campo, usar fallback
        if not name_parts:
            name_parts = ["DOCUMENTO"]
        
        # Adicionar data se solicitado
        if include_date:
            current_date = datetime.now().strftime("%Y-%m-%d")
            name_parts.append(current_date)
        
        return "_".join(name_parts)
    
    def _sanitize_filename_part(self, value: str) -> str:
        """
        Sanitiza uma parte do nome do arquivo.
        
        Args:
            value: Valor original
            
        Returns:
            Valor sanitizado
        """
        import re
        
        # Remover caracteres especiais, manter apenas letras, números, espaços e hífens
        sanitized = re.sub(r'[^\w\s\-]', '', str(value))
        # Substituir espaços por underscores
        sanitized = re.sub(r'\s+', '_', sanitized)
        # Remover underscores múltiplos
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remover underscores no início e fim
        sanitized = sanitized.strip('_')
        # Converter para maiúsculas
        sanitized = sanitized.upper()
        
        # Limitar tamanho
        return sanitized[:30] if sanitized else ""
    
    def get_field_suggestions(self, data: Dict[str, str]) -> List[str]:
        """
        Sugere campos mais adequados para nomenclatura.
        
        Args:
            data: Dados coletados
            
        Returns:
            Lista de campos sugeridos ordenados por relevância
        """
        suggestions = []
        
        # Campos prioritários para nomenclatura
        priority_patterns = [
            # Nomes e razões sociais
            r'.*razao.*social.*',
            r'.*nome.*',
            r'.*empresa.*',
            # Identificadores
            r'.*contratante.*',
            r'.*contratada.*',
            r'.*cliente.*',
            r'.*fornecedor.*',
            # Documentos importantes
            r'.*cpf.*',
            r'.*cnpj.*',
            # Valores e datas
            r'.*valor.*',
            r'.*data.*'
        ]
        
        import re
        
        # Ordenar campos por prioridade
        for pattern in priority_patterns:
            for field_name in data.keys():
                if re.match(pattern, field_name.lower()) and field_name not in suggestions:
                    suggestions.append(field_name)
        
        # Adicionar campos restantes
        for field_name in sorted(data.keys()):
            if field_name not in suggestions:
                suggestions.append(field_name)
        
        return suggestions
    
    def get_field_suggestions_from_template(self, field_names: List[str]) -> List[str]:
        """
        Sugere campos mais adequados para nomenclatura baseado nos campos do template.
        
        Args:
            field_names: Lista de nomes de campos do template
            
        Returns:
            Lista de campos sugeridos ordenados por relevância
        """
        suggestions = []
        
        # Campos prioritários para nomenclatura
        priority_patterns = [
            # Nomes e razões sociais
            r'.*razao.*social.*',
            r'.*nome.*',
            r'.*empresa.*',
            # Identificadores
            r'.*contratante.*',
            r'.*contratada.*',
            r'.*cliente.*',
            r'.*fornecedor.*',
            r'.*prestador.*',
            # Documentos importantes
            r'.*cpf.*',
            r'.*cnpj.*',
            # Valores e datas
            r'.*valor.*',
            r'.*data.*',
            # Outros campos úteis
            r'.*numero.*',
            r'.*codigo.*',
            r'.*tipo.*'
        ]
        
        import re
        
        # Ordenar campos por prioridade
        for pattern in priority_patterns:
            for field_name in field_names:
                if re.match(pattern, field_name.lower()) and field_name not in suggestions:
                    suggestions.append(field_name)
        
        # Adicionar campos restantes em ordem alfabética
        for field_name in sorted(field_names):
            if field_name not in suggestions:
                suggestions.append(field_name)
        
        return suggestions
    
    def list_saved_configs(self) -> List[Dict[str, Any]]:
        """
        Lista todas as configurações salvas.
        
        Returns:
            Lista de configurações com metadados
        """
        configs = []
        
        for config_file in self.config_dir.glob("naming_*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                configs.append({
                    "file": config_file.name,
                    "template_name": config.get("template_name", "Unknown"),
                    "naming_fields": config.get("naming_fields", []),
                    "created_at": config.get("created_at", "Unknown"),
                    "sample_filename": config.get("sample_filename", "")
                })
                
            except Exception as e:
                logger.warning(f"Erro ao ler {config_file}: {e}")
        
        return sorted(configs, key=lambda x: x["created_at"], reverse=True)
    
    def delete_config(self, template_name: str) -> bool:
        """
        Remove configuração de um template.
        
        Args:
            template_name: Nome do template
            
        Returns:
            True se removeu com sucesso
        """
        config_path = self.get_template_config_path(template_name)
        
        try:
            if config_path.exists():
                config_path.unlink()
                logger.info(f"Configuração removida para {template_name}")
                return True
            else:
                logger.warning(f"Configuração não encontrada para {template_name}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao remover configuração: {e}")
            return False