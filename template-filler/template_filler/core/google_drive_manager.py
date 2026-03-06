"""
Google Drive Manager
Gestão completa de arquivos e pastas no Google Drive via Service Account.
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any
from functools import wraps
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_api_errors(func):
    """Decorator para tratamento de erros da Google API."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except HttpError as e:
                if e.resp.status == 403:
                    logger.error("Erro 403: Sem acesso ao arquivo/pasta")
                    raise PermissionError("Sem acesso ao arquivo/pasta")
                elif e.resp.status == 404:
                    logger.error("Erro 404: Arquivo/pasta não encontrado")
                    raise FileNotFoundError("Template não encontrado")
                elif e.resp.status == 429:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limit - aguardando {wait_time}s (tentativa {attempt + 1})")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception("Limite de API excedido")
                else:
                    logger.error(f"Erro da API: {e}")
                    raise Exception(f"Erro da API: {e}")
            except Exception as e:
                logger.error(f"Erro inesperado: {e}")
                raise
        return None
    return wrapper


class GoogleDriveManager:
    """
    Gerenciador completo do Google Drive para Template_Filler.
    
    Funcionalidades:
    - Autenticação Service Account
    - Listagem de templates
    - Cópia de documentos
    - Criação de estrutura de pastas
    - Rate limiting automático
    """
    
    def __init__(self, credentials_path: str, root_folder_id: Optional[str] = None):
        """
        Inicializa o GoogleDriveManager.
        
        Args:
            credentials_path: Caminho para arquivo JSON do Service Account
            root_folder_id: ID da pasta raiz Template_Filler (opcional)
        """
        self.credentials_path = credentials_path
        self.root_folder_id = root_folder_id
        self._drive_service = None
        self._docs_service = None
        
        # Cache para estrutura de pastas
        self._folder_cache = {}
        
        logger.info("Inicializando GoogleDriveManager...")
    
    @property
    def drive_service(self):
        """Lazy loading do serviço Google Drive."""
        if self._drive_service is None:
            self._drive_service = self._build_service('drive', 'v3')
        return self._drive_service
    
    @property 
    def docs_service(self):
        """Lazy loading do serviço Google Docs."""
        if self._docs_service is None:
            self._docs_service = self._build_service('docs', 'v1')
        return self._docs_service
    
    def _build_service(self, service_name: str, version: str):
        """Constrói serviço Google API com Service Account."""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {self.credentials_path}")
            
            # Scopes necessários para Drive e Docs
            scopes = [
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/documents'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scopes
            )
            
            service = build(service_name, version, credentials=credentials)
            logger.info(f"Serviço {service_name} v{version} autenticado com sucesso")
            return service
            
        except Exception as e:
            logger.error(f"Erro ao autenticar {service_name}: {e}")
            raise
    
    @handle_api_errors
    def test_connection(self) -> Dict[str, Any]:
        """
        Testa conectividade com Google Drive.
        
        Returns:
            Dict com informações da conta e status
        """
        logger.info("Testando conexão com Google Drive...")
        
        # Testar Drive API
        about = self.drive_service.about().get(fields="user,storageQuota").execute()
        
        result = {
            "status": "success",
            "user_email": about.get('user', {}).get('emailAddress'),
            "drive_usage": about.get('storageQuota', {}),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Conexão OK - Usuário: {result['user_email']}")
        return result
    
    @handle_api_errors
    def find_or_create_root_folder(self) -> str:
        """
        Encontra ou cria pasta raiz 'Template_Filler'.
        
        Returns:
            ID da pasta raiz
        """
        if self.root_folder_id:
            return self.root_folder_id
        
        logger.info("Procurando pasta raiz 'Template_Filler'...")
        
        # Buscar pasta existente
        query = "name='Template_Filler' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.drive_service.files().list(
            q=query, 
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        folders = results.get('files', [])
        
        if folders:
            folder_id = folders[0]['id']
            logger.info(f"Pasta raiz encontrada: {folder_id}")
            self.root_folder_id = folder_id
            return folder_id
        else:
            # Criar pasta raiz
            folder_metadata = {
                'name': 'Template_Filler',
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id',
                supportsAllDrives=True
            ).execute()
            
            folder_id = folder['id']
            logger.info(f"Pasta raiz criada: {folder_id}")
            self.root_folder_id = folder_id
            return folder_id
    
    @handle_api_errors
    def create_folder_structure(self) -> Dict[str, str]:
        """
        Cria estrutura completa de pastas do Template_Filler.
        
        Returns:
            Dict com IDs das pastas criadas
        """
        # Verificar se já temos a estrutura em cache
        if self._folder_cache.get("templates") and self._folder_cache.get("documentos_gerados"):
            logger.debug("Estrutura de pastas já existe em cache")
            return self._folder_cache
            
        logger.info("Criando estrutura de pastas...")
        
        root_id = self.find_or_create_root_folder()
        
        # Estrutura de pastas necessárias
        folders_to_create = [
            "Templates",
            "Documentos_Gerados", 
            "Config"
        ]
        
        folder_ids = {"root": root_id}
        
        for folder_name in folders_to_create:
            folder_id = self._create_subfolder(folder_name, root_id)
            folder_ids[folder_name.lower()] = folder_id
        
        # Pasta Documentos_Gerados criada - subpastas serão criadas dinamicamente por tipo
        
        logger.info(f"Estrutura verificada: {len(folder_ids)} pastas")
        self._folder_cache.update(folder_ids)
        
        return folder_ids
    
    @handle_api_errors
    def get_or_create_template_folder(self, template_name: str) -> str:
        """
        Obtém ou cria pasta específica para um tipo de template.
        
        Args:
            template_name: Nome do template (ex: "TEMPLATE_CONTRATO_PRESTACAO")
            
        Returns:
            ID da pasta do tipo de template
        """
        # Extrair tipo do template removendo prefixo TEMPLATE_
        folder_name = template_name.replace("TEMPLATE_", "").replace("_", " ").title()
        folder_name = folder_name.replace(" ", "_").upper()
        
        # Garantir que temos a estrutura base
        if not self._folder_cache.get("documentos_gerados"):
            self.create_folder_structure()
        
        docs_folder_id = self._folder_cache["documentos_gerados"]
        
        # Verificar se já existe no cache
        cache_key = f"template_folder_{folder_name.lower()}"
        if cache_key in self._folder_cache:
            return self._folder_cache[cache_key]
        
        # Criar ou encontrar pasta do tipo
        template_folder_id = self._create_subfolder(folder_name, docs_folder_id)
        self._folder_cache[cache_key] = template_folder_id
        
        logger.info(f"Pasta do tipo '{folder_name}' disponível: {template_folder_id}")
        return template_folder_id
    
    def _create_subfolder(self, name: str, parent_id: str) -> str:
        """Cria subpasta se não existir."""
        # Verificar se já existe
        query = f"name='{name}' and parents in '{parent_id}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = self.drive_service.files().list(
            q=query, 
            fields="files(id, name)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        folders = results.get('files', [])
        if folders:
            logger.debug(f"Pasta '{name}' já existe: {folders[0]['id']}")
            return folders[0]['id']
        
        # Criar nova pasta
        folder_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        
        folder = self.drive_service.files().create(
            body=folder_metadata,
            fields='id',
            supportsAllDrives=True
        ).execute()
        
        logger.info(f"Pasta '{name}' criada: {folder['id']}")
        return folder['id']
    
    @handle_api_errors
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        Lista todos os templates disponíveis na pasta Templates.
        
        Returns:
            Lista de dicts com informações dos templates
        """
        logger.info("Listando templates disponíveis...")
        
        # Garantir que estrutura existe
        if not self._folder_cache.get("templates"):
            self.create_folder_structure()
        
        templates_folder_id = self._folder_cache.get("templates")
        
        # Buscar arquivos que começam com TEMPLATE_
        query = f"parents in '{templates_folder_id}' and name contains 'TEMPLATE_' and trashed=false"
        results = self.drive_service.files().list(
            q=query,
            fields="files(id, name, createdTime, modifiedTime, size, mimeType)",
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        
        files = results.get('files', [])
        
        templates = []
        for file in files:
            # Extrair tipo do nome (TEMPLATE_Tipo_Descricao)
            name_parts = file['name'].split('_')
            template_type = name_parts[1] if len(name_parts) > 1 else "Unknown"
            
            template_info = {
                'id': file['id'],
                'name': file['name'],
                'type': template_type,
                'created': file.get('createdTime'),
                'modified': file.get('modifiedTime'),
                'size': file.get('size'),
                'mime_type': file.get('mimeType')
            }
            templates.append(template_info)
        
        logger.info(f"Encontrados {len(templates)} templates")
        return templates
    
    @handle_api_errors
    def copy_template(self, template_id: str, new_name: str, client_name: str) -> Dict[str, str]:
        """
        Copia template para pasta de documentos gerados.
        
        Args:
            template_id: ID do template no Google Drive
            new_name: Nome do novo documento
            client_name: Nome do cliente (para organização)
            
        Returns:
            Dict com informações do documento criado
        """
        logger.info(f"Copiando template {template_id} como '{new_name}'...")
        
        # Garantir estrutura de pastas
        if not self._folder_cache.get("current_month"):
            self.create_folder_structure()
        
        # Determinar pasta de destino (mês atual)
        dest_folder_id = self._folder_cache["current_month"]
        
        # Metadados da cópia
        copy_metadata = {
            'name': new_name,
            'parents': [dest_folder_id]
        }
        
        # Executar cópia
        copied_file = self.drive_service.files().copy(
            fileId=template_id,
            body=copy_metadata,
            fields='id, name, parents, webViewLink'
        ).execute()
        
        result = {
            'document_id': copied_file['id'],
            'name': copied_file['name'],
            'folder_id': dest_folder_id,
            'url': copied_file['webViewLink'],
            'client': client_name,
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"Documento criado: {result['document_id']}")
        return result
    
    @handle_api_errors
    def get_document_content(self, document_id: str) -> str:
        """
        Obtém conteúdo de um documento Google Docs.
        
        Args:
            document_id: ID do documento
            
        Returns:
            Texto do documento
        """
        logger.info(f"Obtendo conteúdo do documento {document_id}...")
        
        doc = self.docs_service.documents().get(documentId=document_id).execute()
        
        content = ""
        for element in doc.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        content += text_run['textRun'].get('content', '')
        
        return content
    
    def get_folder_structure(self) -> Dict[str, str]:
        """Retorna cache da estrutura de pastas."""
        if not self._folder_cache:
            self.create_folder_structure()
        return self._folder_cache.copy()
    
    def __repr__(self) -> str:
        """Representação string do objeto."""
        return f"GoogleDriveManager(credentials='{self.credentials_path}', root='{self.root_folder_id}')"