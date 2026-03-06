"""
Template Parser
Analisador de templates do Google Docs para extração e tipagem de campos.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class FieldDefinition:
    """Definição de um campo extraído do template."""
    
    def __init__(self, name: str, field_type: str = "text", format_spec: str = "", optional: bool = False):
        self.name = name
        self.field_type = field_type
        self.type = field_type  # Alias para compatibilidade
        self.format_spec = format_spec
        self.format = format_spec  # Alias para compatibilidade
        self.optional = optional
        self.required = not optional  # Alias para compatibilidade
        self.description = ""  # Para compatibilidade com MCP
        self.example = ""  # Para compatibilidade com MCP
    
    def __repr__(self):
        return f"FieldDefinition(name='{self.name}', type='{self.field_type}', format='{self.format_spec}', optional={self.optional})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return {
            "name": self.name,
            "type": self.field_type,
            "format": self.format_spec,
            "optional": self.optional
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FieldDefinition':
        """Cria instância a partir de dicionário."""
        return cls(
            name=data["name"],
            field_type=data["type"],
            format_spec=data.get("format", ""),
            optional=data.get("optional", False)
        )


class TemplateParser:
    """
    Parser de templates do Google Docs.
    
    Funcionalidades:
    - Extração de marcadores {{campo}} ou {{campo:tipo:formato}}
    - Sistema híbrido: tipos explícitos + fallback interativo
    - Cache de configuração por template
    - Validação de integridade dos marcadores
    """
    
    # Regex para detectar marcadores
    FIELD_PATTERN = re.compile(r'\{\{([^}]+)\}\}')
    
    # Tipos de campo suportados
    SUPPORTED_TYPES = {
        'text': 'Texto simples',
        'text_uppercase': 'Texto em maiúsculas',
        'date': 'Data formatada',
        'currency': 'Valor monetário',
        'currency_number': 'Número formatado (###.###,##)',
        'currency_text': 'Valor por extenso',
        'email': 'Email válido',
        'phone': 'Telefone',
        'number': 'Número'
    }
    
    # Formatos padrão por tipo
    DEFAULT_FORMATS = {
        'date': 'dd/mm/yyyy',
        'currency': 'R$ #.###,##',
        'currency_number': '#.###,##',
        'currency_text': 'full',
        'phone': '(##) #####-####'
    }
    
    def __init__(self, google_drive_manager):
        """
        Inicializa o TemplateParser.
        
        Args:
            google_drive_manager: Instância do GoogleDriveManager
        """
        self.drive_manager = google_drive_manager
        self._docs_service = None
        self._template_cache = {}
        
        logger.info("Inicializando TemplateParser...")
    
    @property
    def docs_service(self):
        """Lazy loading do serviço Google Docs."""
        if self._docs_service is None:
            self._docs_service = self.drive_manager.docs_service
        return self._docs_service
    
    def extract_fields(self, template_id: str, interactive: bool = True) -> List[FieldDefinition]:
        """
        Extrai campos de um template.
        
        Args:
            template_id: ID do template no Google Drive
            interactive: Se deve perguntar tipos não especificados
            
        Returns:
            Lista de FieldDefinition com campos encontrados
        """
        logger.info(f"Extraindo campos do template {template_id}")
        
        # Verificar cache primeiro
        if template_id in self._template_cache:
            logger.info("Usando configuração em cache")
            cached_fields = self._template_cache[template_id]
            return [FieldDefinition.from_dict(field) for field in cached_fields]
        
        try:
            # Obter conteúdo do documento
            content = self._get_document_content(template_id)
            
            # Extrair marcadores
            raw_fields = self._extract_raw_fields(content)
            
            # Processar campos
            field_definitions = []
            for raw_field in raw_fields:
                field_def = self._parse_field_definition(raw_field, interactive)
                if field_def:
                    field_definitions.append(field_def)
            
            # Remover duplicatas
            unique_fields = self._remove_duplicate_fields(field_definitions)
            
            # Cachear resultado
            self._cache_template_config(template_id, unique_fields)
            
            logger.info(f"Extraídos {len(unique_fields)} campos únicos")
            return unique_fields
            
        except Exception as e:
            logger.error(f"Erro ao extrair campos: {e}")
            raise
    
    def _get_document_content(self, template_id: str) -> str:
        """Obtém conteúdo textual do documento."""
        try:
            # Obter documento
            document = self.docs_service.documents().get(
                documentId=template_id,
                fields='body'
            ).execute()
            
            # Extrair texto de parágrafos e tabelas
            content = ""
            body = document.get('body', {})
            
            def extract_text_from_element(element):
                """Extrai texto recursivamente de qualquer elemento."""
                text = ""
                
                # Processar parágrafo
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    for text_element in paragraph.get('elements', []):
                        if 'textRun' in text_element:
                            text += text_element['textRun'].get('content', '')
                
                # Processar tabela
                elif 'table' in element:
                    table = element['table']
                    for row in table.get('tableRows', []):
                        for cell in row.get('tableCells', []):
                            # Processar conteúdo da célula recursivamente
                            for cell_element in cell.get('content', []):
                                text += extract_text_from_element(cell_element)
                
                # Processar outros tipos de elemento se necessário
                return text
            
            for element in body.get('content', []):
                content += extract_text_from_element(element)
            
            return content
            
        except HttpError as e:
            logger.error(f"Erro ao acessar documento: {e}")
            raise
    
    def _extract_raw_fields(self, content: str) -> List[str]:
        """Extrai marcadores brutos do conteúdo."""
        matches = self.FIELD_PATTERN.findall(content)
        logger.info(f"Encontrados {len(matches)} marcadores brutos")
        return matches
    
    def _parse_field_definition(self, raw_field: str, interactive: bool = True) -> Optional[FieldDefinition]:
        """
        Processa definição de campo bruto.
        
        Formato esperado: campo:tipo:formato:optional
        Exemplo: data_inicio:date:dd/mm/yyyy
        """
        parts = raw_field.split(':')
        field_name = parts[0].strip()
        
        # Verificar se campo está vazio
        if not field_name:
            return None
        
        # Valores padrão
        field_type = "text"
        format_spec = ""
        optional = False
        
        # Processar partes adicionais
        if len(parts) > 1:
            for part in parts[1:]:
                part = part.strip()
                if part == "optional":
                    optional = True
                elif part in self.SUPPORTED_TYPES:
                    field_type = part
                else:
                    # Assumir que é especificação de formato
                    format_spec = part
        
        # Se não foi especificado tipo e modo interativo, perguntar
        if field_type == "text" and len(parts) == 1 and interactive:
            field_type = self._ask_field_type(field_name)
        
        # Aplicar formato padrão se não especificado
        if not format_spec and field_type in self.DEFAULT_FORMATS:
            format_spec = self.DEFAULT_FORMATS[field_type]
        
        return FieldDefinition(
            name=field_name,
            field_type=field_type,
            format_spec=format_spec,
            optional=optional
        )
    
    def _ask_field_type(self, field_name: str) -> str:
        """
        Pergunta interativamente o tipo do campo.
        
        Args:
            field_name: Nome do campo
            
        Returns:
            Tipo escolhido pelo usuário
        """
        print(f"\n🔍 Campo encontrado: '{field_name}'")
        print("Tipos disponíveis:")
        
        types_list = list(self.SUPPORTED_TYPES.items())
        for i, (type_key, description) in enumerate(types_list, 1):
            print(f"  {i}. {type_key} - {description}")
        
        while True:
            try:
                choice = input(f"\nEscolha o tipo para '{field_name}' (1-{len(types_list)}) ou Enter para 'text': ").strip()
                
                if not choice:
                    return "text"
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(types_list):
                    return types_list[choice_num - 1][0]
                else:
                    print("❌ Opção inválida. Tente novamente.")
                    
            except ValueError:
                print("❌ Digite um número válido.")
    
    def _remove_duplicate_fields(self, fields: List[FieldDefinition]) -> List[FieldDefinition]:
        """Remove campos duplicados mantendo o primeiro."""
        seen = set()
        unique_fields = []
        
        for field in fields:
            if field.name not in seen:
                seen.add(field.name)
                unique_fields.append(field)
        
        return unique_fields
    
    def _cache_template_config(self, template_id: str, fields: List[FieldDefinition]):
        """Cacheia configuração do template."""
        self._template_cache[template_id] = [field.to_dict() for field in fields]
        logger.info(f"Configuração cacheada para template {template_id}")
    
    def validate_template(self, template_id: str) -> Dict[str, Any]:
        """
        Valida integridade do template.
        
        Returns:
            Dict com resultado da validação
        """
        logger.info(f"Validando template {template_id}")
        
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "field_count": 0,
            "fields": []
        }
        
        try:
            fields = self.extract_fields(template_id, interactive=False)
            result["field_count"] = len(fields)
            result["fields"] = [field.to_dict() for field in fields]
            
            # Validações
            field_names = [f.name for f in fields]
            
            # Verificar campos obrigatórios sem tipo definido
            for field in fields:
                if field.field_type == "text" and not field.optional:
                    result["warnings"].append(
                        f"Campo '{field.name}' sem tipo específico (usando 'text' padrão)"
                    )
            
            # Verificar nomes de campos vazios ou inválidos
            for field in fields:
                if not field.name or not field.name.replace('_', '').isalnum():
                    result["errors"].append(
                        f"Nome de campo inválido: '{field.name}'"
                    )
            
            if result["errors"]:
                result["valid"] = False
                
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Erro ao processar template: {str(e)}")
        
        return result
    
    def get_template_summary(self, template_id: str) -> Dict[str, Any]:
        """
        Retorna resumo do template com campos e estatísticas.
        
        Returns:
            Dict com informações do template
        """
        try:
            fields = self.extract_fields(template_id, interactive=False)
            
            # Estatísticas por tipo
            type_counts = {}
            for field in fields:
                type_counts[field.field_type] = type_counts.get(field.field_type, 0) + 1
            
            # Campos obrigatórios vs opcionais
            required_fields = [f for f in fields if not f.optional]
            optional_fields = [f for f in fields if f.optional]
            
            return {
                "template_id": template_id,
                "total_fields": len(fields),
                "required_fields": len(required_fields),
                "optional_fields": len(optional_fields),
                "types_distribution": type_counts,
                "fields": [field.to_dict() for field in fields],
                "validation": self.validate_template(template_id)
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {e}")
            return {
                "template_id": template_id,
                "error": str(e)
            }
    
    def clear_cache(self, template_id: Optional[str] = None):
        """
        Limpa cache de templates.
        
        Args:
            template_id: ID específico ou None para limpar tudo
        """
        if template_id:
            self._template_cache.pop(template_id, None)
            logger.info(f"Cache limpo para template {template_id}")
        else:
            self._template_cache.clear()
            logger.info("Cache completo limpo")