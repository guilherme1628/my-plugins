"""
Document Generator
Sistema de geração de documentos finais a partir de templates e dados coletados.
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .google_drive_manager import GoogleDriveManager
from .data_collector import DataCollectionResult
from .template_parser import FieldDefinition
from .naming_config import NamingConfigManager

logger = logging.getLogger(__name__)


class DocumentGenerationResult:
    """Resultado da geração de documento."""
    
    def __init__(self, document_id: str, document_name: str, document_url: str, template_name: str):
        self.document_id = document_id
        self.document_name = document_name
        self.document_url = document_url
        self.template_name = template_name
        self.generated_at = datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return {
            "document_id": self.document_id,
            "document_name": self.document_name,
            "document_url": self.document_url,
            "template_name": self.template_name,
            "generated_at": self.generated_at
        }


class DocumentGenerator:
    """
    Gerador de documentos finais.
    
    Funcionalidades:
    - Substituição de marcadores {{campo}} por dados coletados
    - Nomenclatura automática: [CONTRATANTE]_[CONTRATADA]_[DATA]
    - Organização por tipo de template
    - Preservação da formatação original
    """
    
    def __init__(self, google_drive_manager: GoogleDriveManager):
        """
        Inicializa o DocumentGenerator.
        
        Args:
            google_drive_manager: Instância do GoogleDriveManager
        """
        self.drive_manager = google_drive_manager
        self._docs_service = None
        self.naming_config = NamingConfigManager()
        
        # Campos preferenciais para nomenclatura automática (fallback)
        self.NAMING_FIELDS = {
            'contratante': ['contratante_razaoSocial', 'contratante_nome', 'contratante', 'empresa_contratante', 'nome_contratante'],
            'contratada': ['contratada_razaoSocial', 'contratada_nome', 'contratada', 'empresa_contratada', 'nome_contratada', 'prestador', 'fornecedor']
        }
        
        logger.info("Inicializando DocumentGenerator...")
    
    @property
    def docs_service(self):
        """Lazy loading do serviço Google Docs."""
        if self._docs_service is None:
            self._docs_service = self.drive_manager.docs_service
        return self._docs_service
    
    def generate_document(self, template_id: str, collection_result: DataCollectionResult, 
                         custom_name: Optional[str] = None) -> DocumentGenerationResult:
        """
        Gera documento final a partir de template e dados coletados.
        
        Args:
            template_id: ID do template no Google Drive
            collection_result: Resultado da coleta de dados
            custom_name: Nome personalizado (opcional)
            
        Returns:
            DocumentGenerationResult com informações do documento gerado
        """
        logger.info(f"Gerando documento a partir do template {template_id}")
        
        try:
            # 1. Copiar template para pasta de destino
            target_folder_id = self.drive_manager.get_or_create_template_folder(collection_result.template_name)
            
            # 2. Gerar nome do documento
            document_name = custom_name or self._generate_document_name(collection_result)
            
            # 3. Copiar template
            copied_doc_id = self._copy_template_to_destination(template_id, target_folder_id, document_name)
            
            # 4. Substituir marcadores
            self._replace_placeholders(copied_doc_id, collection_result.data)
            
            # 5. Gerar URL do documento
            document_url = f"https://docs.google.com/document/d/{copied_doc_id}/edit"
            
            logger.info(f"Documento gerado com sucesso: {document_name}")
            
            return DocumentGenerationResult(
                document_id=copied_doc_id,
                document_name=document_name,
                document_url=document_url,
                template_name=collection_result.template_name
            )
            
        except Exception as e:
            logger.error(f"Erro ao gerar documento: {e}")
            raise
    
    def _generate_document_name(self, collection_result: DataCollectionResult) -> str:
        """
        Gera nome automático baseado na configuração salva ou padrão.
        
        Args:
            collection_result: Resultado da coleta com dados
            
        Returns:
            Nome do documento formatado
        """
        # Tentar carregar configuração salva
        config = self.naming_config.load_naming_config(collection_result.template_name)
        
        if config and config.get('naming_fields'):
            # Usar configuração personalizada
            logger.info(f"Usando configuração personalizada: {config['naming_fields']}")
            return self.naming_config.generate_filename(
                config['naming_fields'], 
                collection_result.data
            )
        else:
            # Usar lógica padrão (fallback)
            logger.info("Usando nomenclatura padrão")
            return self._generate_default_name(collection_result)
    
    def _generate_default_name(self, collection_result: DataCollectionResult) -> str:
        """
        Gera nome usando lógica padrão [CONTRATANTE]_[CONTRATADA]_[DATA].
        
        Args:
            collection_result: Resultado da coleta com dados
            
        Returns:
            Nome do documento formatado
        """
        data = collection_result.data
        
        # Encontrar contratante
        contratante = self._find_field_value(data, self.NAMING_FIELDS['contratante'])
        if not contratante:
            contratante = "CONTRATANTE"
        
        # Encontrar contratada
        contratada = self._find_field_value(data, self.NAMING_FIELDS['contratada'])
        if not contratada:
            contratada = "CONTRATADA"
        
        # Data atual
        data_atual = datetime.now().strftime("%Y-%m-%d")
        
        # Sanitizar nomes (remover caracteres especiais)
        contratante = self._sanitize_filename(contratante)
        contratada = self._sanitize_filename(contratada)
        
        # Limitar tamanho
        contratante = contratante[:30]
        contratada = contratada[:30]
        
        return f"{contratante}_{contratada}_{data_atual}"
    
    def _find_field_value(self, data: Dict[str, str], field_candidates: List[str]) -> Optional[str]:
        """
        Busca valor de campo usando lista de candidatos.
        
        Args:
            data: Dados coletados
            field_candidates: Lista de nomes de campos possíveis
            
        Returns:
            Valor encontrado ou None
        """
        for field_name in field_candidates:
            if field_name in data and data[field_name].strip():
                return data[field_name].strip()
        return None
    
    def _sanitize_filename(self, name: str) -> str:
        """
        Remove caracteres não permitidos em nomes de arquivo.
        
        Args:
            name: Nome original
            
        Returns:
            Nome sanitizado
        """
        # Remover caracteres especiais, manter apenas letras, números, espaços e hífens
        sanitized = re.sub(r'[^\w\s\-]', '', name)
        # Substituir espaços por underscores
        sanitized = re.sub(r'\s+', '_', sanitized)
        # Remover underscores múltiplos
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remover underscores no início e fim
        sanitized = sanitized.strip('_')
        
        return sanitized.upper()
    
    def _copy_template_to_destination(self, template_id: str, target_folder_id: str, document_name: str) -> str:
        """
        Copia template para pasta de destino com nome específico.
        
        Args:
            template_id: ID do template original
            target_folder_id: ID da pasta de destino
            document_name: Nome do novo documento
            
        Returns:
            ID do documento copiado
        """
        copy_metadata = {
            'name': document_name,
            'parents': [target_folder_id]
        }
        
        copied_file = self.drive_manager.drive_service.files().copy(
            fileId=template_id,
            body=copy_metadata,
            supportsAllDrives=True
        ).execute()
        
        logger.info(f"Template copiado para: {document_name}")
        return copied_file['id']
    
    def _replace_placeholders(self, document_id: str, data: Dict[str, str]):
        """
        Substitui marcadores {{campo}} pelos valores coletados.
        
        Args:
            document_id: ID do documento a ser modificado
            data: Dados para substituição
        """
        logger.info(f"Substituindo marcadores no documento {document_id}")
        logger.info(f"Dados recebidos: {list(data.keys())}")
        
        # Primeiro, vamos verificar o conteúdo do documento
        try:
            document = self.docs_service.documents().get(documentId=document_id).execute()
            content = self._extract_text_content(document)
            logger.info(f"Conteúdo do documento (primeiros 200 chars): {content[:200]}")
            
            # Encontrar placeholders no documento
            import re
            placeholder_pattern = re.compile(r'\{\{([^}]+)\}\}')
            found_placeholders_raw = placeholder_pattern.findall(content)
            logger.info(f"Placeholders brutos encontrados: {found_placeholders_raw}")
            
            # Extrair nomes de campos e mapear TODOS os placeholders únicos
            field_names_in_doc = set()
            placeholder_mapping = {}  # nome_campo -> [lista de placeholders_completos]
            all_unique_placeholders = set(found_placeholders_raw)  # Todos placeholders únicos
            
            for placeholder_raw in found_placeholders_raw:
                field_name = placeholder_raw.split(':')[0].strip()  # Pegar só o nome antes do ':'
                field_names_in_doc.add(field_name)
                
                # Armazenar TODOS os placeholders para o mesmo field_name
                if field_name not in placeholder_mapping:
                    placeholder_mapping[field_name] = []
                if placeholder_raw not in placeholder_mapping[field_name]:
                    placeholder_mapping[field_name].append(placeholder_raw)
            
            logger.info(f"Nomes de campos extraídos: {field_names_in_doc}")
            logger.info(f"Placeholders únicos totais: {len(all_unique_placeholders)}")
            logger.info(f"Mapeamento completo: {placeholder_mapping}")
            
            # Verificar correspondência
            available_fields = set(data.keys())
            matching_fields = field_names_in_doc.intersection(available_fields)
            missing_fields = field_names_in_doc - available_fields
            
            logger.info(f"Campos que coincidem: {matching_fields}")
            if missing_fields:
                logger.warning(f"Placeholders sem dados: {missing_fields}")
            
            if not matching_fields:
                logger.error("NENHUM placeholder corresponde aos dados!")
                return
                
        except Exception as e:
            logger.error(f"Erro ao verificar conteúdo do documento: {e}")
            return
        
        # Fazer substituições para TODOS os placeholders únicos
        successful_replacements = 0
        total_occurrences = 0
        
        for field_name, field_value in data.items():
            if field_name not in matching_fields:
                continue  # Só processar campos que existem no documento
                
            # Substituir TODOS os placeholders deste campo
            placeholders_for_field = placeholder_mapping[field_name]
            logger.info(f"Campo '{field_name}' tem {len(placeholders_for_field)} placeholder(s): {placeholders_for_field}")
            
            for placeholder_raw in placeholders_for_field:
                placeholder = f"{{{{{placeholder_raw}}}}}"
                logger.info(f"Substituindo: '{placeholder}' -> '{field_value}'")
                
                try:
                    # Fazer uma substituição por vez para cada placeholder único
                    request = {
                        'replaceAllText': {
                            'containsText': {
                                'text': placeholder,
                                'matchCase': True  # Usar match exato
                            },
                            'replaceText': str(field_value) if field_value else ""
                        }
                    }
                    
                    result = self.docs_service.documents().batchUpdate(
                        documentId=document_id,
                        body={'requests': [request]}
                    ).execute()
                    
                    # Verificar se a substituição teve sucesso
                    if 'replies' in result and result['replies']:
                        reply = result['replies'][0]
                        if 'replaceAllText' in reply:
                            occurrences = reply['replaceAllText'].get('occurrencesChanged', 0)
                            if occurrences > 0:
                                logger.info(f"✅ Substituído {occurrences} ocorrência(s) de '{placeholder}'")
                                successful_replacements += 1
                                total_occurrences += occurrences
                            else:
                                logger.warning(f"⚠️ Placeholder '{placeholder}' não encontrado no documento")
                        else:
                            logger.warning(f"⚠️ Resposta inesperada para '{placeholder}': {reply}")
                    else:
                        logger.warning(f"⚠️ Sem resposta para '{placeholder}'")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao substituir '{placeholder}': {e}")
        
        logger.info(f"🎉 Concluído: {successful_replacements} placeholders substituídos, {total_occurrences} ocorrências totais alteradas")
        
        # Verificação final
        try:
            final_document = self.docs_service.documents().get(documentId=document_id).execute()
            final_content = self._extract_text_content(final_document)
            remaining_placeholders = set(placeholder_pattern.findall(final_content))
            
            if remaining_placeholders:
                logger.warning(f"⚠️ Placeholders ainda presentes: {remaining_placeholders}")
            else:
                logger.info("✅ Todos os placeholders foram substituídos!")
                
        except Exception as e:
            logger.error(f"Erro na verificação final: {e}")
    
    def get_document_preview_url(self, document_id: str) -> str:
        """
        Retorna URL de visualização do documento.
        
        Args:
            document_id: ID do documento
            
        Returns:
            URL de visualização
        """
        return f"https://docs.google.com/document/d/{document_id}/preview"
    
    def validate_template_placeholders(self, template_id: str, expected_fields: List[str]) -> Dict[str, Any]:
        """
        Valida se template contém todos os marcadores necessários.
        
        Args:
            template_id: ID do template
            expected_fields: Lista de campos esperados
            
        Returns:
            Dict com resultado da validação
        """
        logger.info(f"Validando marcadores do template {template_id}")
        
        try:
            # Obter conteúdo do documento
            document = self.docs_service.documents().get(documentId=template_id).execute()
            content = self._extract_text_content(document)
            
            # Encontrar marcadores existentes
            placeholder_pattern = re.compile(r'\{\{([^}]+)\}\}')
            found_placeholders = set(placeholder_pattern.findall(content))
            
            # Verificar correspondência
            expected_set = set(expected_fields)
            missing_fields = expected_set - found_placeholders
            extra_placeholders = found_placeholders - expected_set
            
            result = {
                "valid": len(missing_fields) == 0,
                "found_placeholders": list(found_placeholders),
                "missing_fields": list(missing_fields),
                "extra_placeholders": list(extra_placeholders),
                "total_placeholders": len(found_placeholders)
            }
            
            logger.info(f"Validação concluída: {result['total_placeholders']} marcadores encontrados")
            return result
            
        except Exception as e:
            logger.error(f"Erro na validação: {e}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    def _extract_text_content(self, document: Dict[str, Any]) -> str:
        """
        Extrai conteúdo textual do documento Google Docs incluindo tabelas.
        
        Args:
            document: Objeto documento da API
            
        Returns:
            Conteúdo textual completo
        """
        content = ""
        body = document.get('body', {})
        
        def extract_text_from_element(element):
            """Extrai texto de qualquer elemento recursivamente."""
            text = ""
            
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for text_element in paragraph.get('elements', []):
                    if 'textRun' in text_element:
                        text += text_element['textRun'].get('content', '')
                        
            elif 'table' in element:
                # Processar tabelas recursivamente
                table = element['table']
                for row in table.get('tableRows', []):
                    for cell in row.get('tableCells', []):
                        for cell_element in cell.get('content', []):
                            text += extract_text_from_element(cell_element)
            
            return text
        
        for element in body.get('content', []):
            content += extract_text_from_element(element)
        
        return content