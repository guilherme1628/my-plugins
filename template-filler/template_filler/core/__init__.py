"""
Template_Filler Core Module
Módulos principais para gestão de templates e geração de documentos.
"""

from .google_drive_manager import GoogleDriveManager
from .template_parser import TemplateParser, FieldDefinition
from .data_collector import DataCollector, DataCollectionResult
from .document_generator import DocumentGenerator, DocumentGenerationResult
from .naming_config import NamingConfigManager

__all__ = ["GoogleDriveManager", "TemplateParser", "FieldDefinition", "DataCollector", "DataCollectionResult", "DocumentGenerator", "DocumentGenerationResult", "NamingConfigManager"]