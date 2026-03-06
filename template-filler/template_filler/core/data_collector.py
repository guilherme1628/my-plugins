"""
Data Collector
Sistema de coleta interativa de dados para preenchimento de templates.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from .template_parser import FieldDefinition
from ..utils.validators import validate_field, ValidationError
from ..utils.formatters import format_field

logger = logging.getLogger(__name__)


class DataCollectionResult:
    """Resultado da coleta de dados."""
    
    def __init__(self, template_id: str, template_name: str, data: Dict[str, str], collected_at: str = None, metadata: Dict[str, Any] = None):
        self.template_id = template_id
        self.template_name = template_name
        self.data = data
        self.collected_at = collected_at or datetime.now().isoformat()
        self.metadata = metadata or {
            "total_fields": len(self.data),
            "collector_version": "1.0"
        }
        
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização."""
        return {
            "template_id": self.template_id,
            "template_name": self.template_name,
            "collected_at": self.collected_at,
            "data": self.data,
            "metadata": self.metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Converte para JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class DataCollector:
    """
    Coletor de dados interativo para templates.
    
    Funcionalidades:
    - Coleta interativa de dados baseada em campos do template
    - Validação em tempo real por tipo de campo
    - Formatação automática de dados
    - Sistema de retry para campos inválidos
    - Campos derivados automáticos
    - Salvar/carregar rascunhos
    """
    
    # Mapeamento de campos derivados
    DERIVED_FIELDS = {
        'valor_extenso': 'valor',
        'multa_extenso': 'multa'
    }
    
    def __init__(self, data_dir: str = "data", auto_format: bool = True):
        """
        Inicializa o DataCollector.
        
        Args:
            data_dir: Diretório para salvar dados coletados
            auto_format: Se deve formatar automaticamente os dados
        """
        # Usar caminho absoluto se não for absoluto
        if not os.path.isabs(data_dir):
            # Obter diretório do projeto (3 níveis acima)
            project_root = Path(__file__).parent.parent.parent
            self.data_dir = project_root / data_dir
        else:
            self.data_dir = Path(data_dir)
        
        self.auto_format = auto_format
        
        # Criar diretório se não existir
        self.data_dir.mkdir(exist_ok=True)
        
        logger.info("Inicializando DataCollector...")
    
    def collect_data(self, template_id: str, template_name: str, fields: List[FieldDefinition], 
                    interactive: bool = True, draft_data: Optional[Dict[str, str]] = None) -> DataCollectionResult:
        """
        Coleta dados para um template.
        
        Args:
            template_id: ID do template
            template_name: Nome do template
            fields: Lista de campos do template
            interactive: Se deve coletar interativamente
            draft_data: Dados parciais de rascunho
            
        Returns:
            DataCollectionResult com dados coletados
        """
        logger.info(f"Iniciando coleta de dados para template {template_name}")
        
        collected_data = draft_data.copy() if draft_data else {}
        
        if interactive:
            # Separar campos em coletáveis e derivados
            collectable_fields, derived_fields = self._separate_fields(fields)
            
            print(f"\n📋 Coletando dados para: {template_name}")
            print(f"📄 {len(collectable_fields)} campo(s) a preencher")
            if derived_fields:
                print(f"🔄 {len(derived_fields)} campo(s) serão calculados automaticamente")
            print()
            
            i = 0
            while i < len(collectable_fields):
                field = collectable_fields[i]
                try:
                    result = self._collect_field_interactive(field, i + 1, len(collectable_fields), collected_data.get(field.name, ""))
                    
                    if result == "BACK":
                        # Voltar para campo anterior se não for o primeiro
                        if i > 0:
                            i -= 1
                        continue
                    elif result == "SKIP":
                        # Pular campo atual
                        i += 1
                        continue
                    elif result is not None:
                        collected_data[field.name] = result
                        
                        # Calcular campos derivados relacionados
                        self._calculate_derived_fields(field.name, result, collected_data, derived_fields)
                        
                    i += 1
                        
                except KeyboardInterrupt:
                    print("\n\n⏸️  Coleta interrompida. Salvando rascunho...")
                    self._save_draft(template_id, template_name, collected_data)
                    raise
        else:
            # Modo não-interativo - usar dados fornecidos
            for field in fields:
                if field.name in collected_data:
                    # Validar dados existentes
                    try:
                        validate_field(collected_data[field.name], field.field_type, field.format_spec, field.optional)
                        if self.auto_format:
                            collected_data[field.name] = format_field(
                                collected_data[field.name], 
                                field.field_type, 
                                field.format_spec
                            )
                    except ValidationError as e:
                        logger.warning(f"Campo {field.name} inválido: {e}")
                        if not field.optional:
                            raise ValidationError(f"Campo obrigatório '{field.name}' inválido: {e}")
        
        # Verificar campos obrigatórios (excluindo derivados)
        missing_required = [f.name for f in fields if not f.optional and f.name not in collected_data and f.name not in self.DERIVED_FIELDS]
        if missing_required:
            raise ValidationError(f"Campos obrigatórios não preenchidos: {', '.join(missing_required)}")
        
        # Calcular campos derivados que ainda não foram calculados
        if not interactive:
            collectable_fields, derived_fields = self._separate_fields(fields)
            for field in derived_fields:
                source_field = self.DERIVED_FIELDS.get(field.name)
                if source_field and source_field in collected_data and field.name not in collected_data:
                    derived_value = self._calculate_derived_value(source_field, collected_data[source_field], field)
                    collected_data[field.name] = derived_value
        
        result = DataCollectionResult(template_id, template_name, collected_data)
        
        if interactive:
            print(f"\n✅ Coleta concluída! {len(collected_data)} campo(s) preenchido(s)")
        
        return result
    
    def _collect_field_interactive(self, field: FieldDefinition, current: int, total: int, 
                                 current_value: str = "") -> Optional[str]:
        """
        Coleta um campo de forma interativa.
        
        Args:
            field: Definição do campo
            current: Número do campo atual
            total: Total de campos
            current_value: Valor atual (se houver)
            
        Returns:
            Valor coletado ou None se pulado
        """
        status_icon = "🔸" if field.optional else "🔹"
        field_status = "Opcional" if field.optional else "Obrigatório"
        format_hint = f" (formato: {field.format_spec})" if field.format_spec else ""
        
        print(f"[{current}/{total}] {status_icon} {field_status}")
        print(f"Campo: {field.name}")
        print(f"Tipo: {field.field_type}{format_hint}")
        
        if current_value:
            print(f"Valor atual: {current_value}")
        
        # Adicionar dicas específicas por tipo
        hints = self._get_field_hints(field)
        if hints:
            self._print_info(hints)
        
        # Adicionar instruções de navegação
        navigation_hint = ""
        if current > 1:
            navigation_hint += "Digite 'voltar' para retornar ao campo anterior. "
        if field.optional:
            navigation_hint += "Digite 'pular' para pular este campo opcional."
        
        if navigation_hint:
            self._print_info(navigation_hint)
        
        while True:  # Loop infinito até valor válido ou comando de navegação
            try:
                if current_value:
                    prompt = f"Novo valor (Enter para manter '{current_value}'): "
                else:
                    prompt = f"Valor: "
                
                value = input(prompt).strip()
                
                # Verificar comandos de navegação
                if value.lower() in ['voltar', 'back', 'b']:
                    if current > 1:
                        print("⬅️  Voltando para o campo anterior...")
                        print()
                        return "BACK"
                    else:
                        self._print_warning("Você já está no primeiro campo!")
                        continue
                
                if value.lower() in ['pular', 'skip', 's']:
                    if field.optional:
                        print("⏭️  Pulando campo opcional...")
                        print()
                        return "SKIP"
                    else:
                        self._print_warning("Não é possível pular campos obrigatórios!")
                        continue
                
                # Se Enter e tem valor atual, manter
                if not value and current_value:
                    value = current_value
                
                # Se campo opcional e vazio, aceitar
                if not value and field.optional:
                    print("⏭️  Campo opcional deixado vazio")
                    print()
                    return ""
                
                # Validar
                if value:
                    validate_field(value, field.field_type, field.format_spec, field.optional)
                    
                    # Formatar se habilitado
                    if self.auto_format:
                        formatted_value = format_field(value, field.field_type, field.format_spec)
                        if formatted_value != value:
                            value = formatted_value
                    
                    # Feedback visual melhorado - verde inline
                    self._print_success_field(field.name, value)
                    print()
                    return value
                elif not field.optional:
                    raise ValidationError("Campo obrigatório não pode ficar vazio")
                    
            except ValidationError as e:
                self._print_error(str(e))
                self._print_info("Tente novamente ou use 'voltar' para retornar ao campo anterior.")
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self._print_error(f"Erro inesperado: {e}")
                self._print_info("Tente novamente ou use 'voltar' para retornar ao campo anterior.")
    
    def _separate_fields(self, fields: List[FieldDefinition]) -> Tuple[List[FieldDefinition], List[FieldDefinition]]:
        """
        Separa campos em coletáveis e derivados.
        
        Returns:
            Tupla (campos_coletaveis, campos_derivados)
        """
        collectable = []
        derived = []
        
        for field in fields:
            if field.name in self.DERIVED_FIELDS:
                derived.append(field)
            else:
                collectable.append(field)
        
        return collectable, derived
    
    def _calculate_derived_fields(self, source_field: str, source_value: str, 
                                collected_data: Dict[str, str], derived_fields: List[FieldDefinition]):
        """
        Calcula campos derivados baseados no campo fonte.
        
        Args:
            source_field: Nome do campo que foi preenchido
            source_value: Valor do campo fonte
            collected_data: Dados coletados até agora
            derived_fields: Lista de campos derivados
        """
        for derived_field in derived_fields:
            if self.DERIVED_FIELDS.get(derived_field.name) == source_field:
                try:
                    # Calcular valor derivado
                    derived_value = self._calculate_derived_value(source_field, source_value, derived_field)
                    collected_data[derived_field.name] = derived_value
                    
                    print(f"🔄 {derived_field.name} calculado automaticamente: {derived_value}")
                    
                except Exception as e:
                    logger.warning(f"Erro ao calcular campo derivado {derived_field.name}: {e}")
    
    def _calculate_derived_value(self, source_field: str, source_value: str, derived_field: FieldDefinition) -> str:
        """
        Calcula o valor de um campo derivado.
        
        Args:
            source_field: Nome do campo fonte
            source_value: Valor do campo fonte  
            derived_field: Definição do campo derivado
            
        Returns:
            Valor calculado para o campo derivado
        """
        if derived_field.field_type == 'currency_text':
            # Para campos currency_text, converter o valor monetário para extenso
            return format_field(source_value, 'currency_text', derived_field.format_spec)
        
        # Para outros tipos, retornar o valor fonte formatado conforme o tipo derivado
        return format_field(source_value, derived_field.field_type, derived_field.format_spec)
    
    def _print_success_field(self, field_name: str, value: str):
        """Imprime feedback de sucesso com formatação colorida."""
        # Cores ANSI
        GREEN = '\033[92m'
        RESET = '\033[0m'
        BOLD = '\033[1m'
        
        print(f"{GREEN}{BOLD}{field_name}:{RESET}{GREEN} {value} ✓{RESET}")
    
    def _print_error(self, message: str):
        """Imprime mensagem de erro com formatação colorida."""
        RED = '\033[91m'
        RESET = '\033[0m'
        print(f"{RED}❌ {message}{RESET}")
    
    def _print_warning(self, message: str):
        """Imprime mensagem de aviso com formatação colorida."""
        YELLOW = '\033[93m'
        RESET = '\033[0m'
        print(f"{YELLOW}⚠️  {message}{RESET}")
    
    def _print_info(self, message: str):
        """Imprime mensagem informativa com formatação colorida."""
        BLUE = '\033[94m'
        RESET = '\033[0m'
        print(f"{BLUE}💡 {message}{RESET}")
    
    def _get_field_hints(self, field: FieldDefinition) -> str:
        """Retorna dicas específicas para o tipo de campo."""
        hints = {
            'text_uppercase': 'Será convertido automaticamente para MAIÚSCULAS',
            'date': 'Exemplo: 15/01/2025 ou 15 de janeiro de 2025',
            'currency': 'Exemplo: R$ 1.234,56 ou 1234.56',
            'currency_text': 'Será convertido automaticamente para extenso',
            'email': 'Exemplo: usuario@empresa.com',
            'phone': 'Exemplo: (11) 99999-9999',
            'number': 'Apenas números'
        }
        
        hint = hints.get(field.field_type, "")
        
        # Adicionar dica de formato específico
        if field.format_spec and field.field_type == 'date':
            hint = f"Formato: {field.format_spec}"
        
        return hint
    
    def save_to_file(self, result: DataCollectionResult, filename: Optional[str] = None) -> Path:
        """
        Salva resultado em arquivo JSON.
        
        Args:
            result: Resultado da coleta
            filename: Nome do arquivo (opcional, será gerado automaticamente)
            
        Returns:
            Path do arquivo salvo
        """
        if not filename:
            # Gerar nome usando a mesma configuração do template
            from .naming_config import NamingConfigManager
            naming_config = NamingConfigManager()
            
            # Preparar prefixo do template (sempre incluir)
            clean_template_name = result.template_name.replace("TEMPLATE_", "").replace("-", "_")
            
            # Tentar usar configuração personalizada
            config = naming_config.load_naming_config(result.template_name)
            if config and config.get('naming_fields'):
                try:
                    base_name = naming_config.generate_filename(config['naming_fields'], result.data)
                    filename = f"{clean_template_name}_{base_name}.json"
                except Exception as e:
                    logger.warning(f"Erro ao usar configuração personalizada: {e}")
                    # Fallback para método antigo com prefixo do template
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{clean_template_name}_{timestamp}.json"
            else:
                # Método antigo como fallback com prefixo do template
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{clean_template_name}_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result.to_json())
        
        logger.info(f"Dados salvos em: {filepath}")
        return filepath
    
    def load_from_file(self, filepath: Path) -> DataCollectionResult:
        """
        Carrega dados de arquivo JSON.
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            DataCollectionResult reconstruído
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        result = DataCollectionResult(
            template_id=data['template_id'],
            template_name=data['template_name'],
            data=data['data']
        )
        result.collected_at = data['collected_at']
        
        return result
    
    def _save_draft(self, template_id: str, template_name: str, data: Dict[str, str]):
        """Salva rascunho da coleta."""
        draft_filename = f"DRAFT_{template_name.replace('TEMPLATE_', '')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        draft_data = {
            "template_id": template_id,
            "template_name": template_name,
            "draft": True,
            "saved_at": datetime.now().isoformat(),
            "data": data
        }
        
        draft_path = self.data_dir / draft_filename
        with open(draft_path, 'w', encoding='utf-8') as f:
            json.dump(draft_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Rascunho salvo: {draft_path}")
    
    def list_drafts(self) -> List[Path]:
        """Lista arquivos de rascunho disponíveis."""
        return list(self.data_dir.glob("DRAFT_*.json"))
    
    def load_draft(self, draft_path: Path) -> Tuple[str, str, Dict[str, str]]:
        """
        Carrega dados de um rascunho.
        
        Returns:
            Tupla (template_id, template_name, data)
        """
        with open(draft_path, 'r', encoding='utf-8') as f:
            draft = json.load(f)
        
        return draft['template_id'], draft['template_name'], draft['data']
    
    def list_collected_data(self) -> List[Path]:
        """Lista arquivos de dados coletados (não rascunhos)."""
        all_files = list(self.data_dir.glob("*.json"))
        return [f for f in all_files if not f.name.startswith("DRAFT_")]
    
    def validate_collected_data(self, result: DataCollectionResult, fields: List[FieldDefinition]) -> Dict[str, Any]:
        """
        Valida dados coletados contra definições de campos.
        
        Returns:
            Dict com resultado da validação
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "field_count": len(result.data),
            "validated_fields": []
        }
        
        # Verificar cada campo
        for field in fields:
            field_validation = {
                "name": field.name,
                "type": field.field_type,
                "optional": field.optional,
                "present": field.name in result.data,
                "valid": True,
                "value": result.data.get(field.name, ""),
                "errors": []
            }
            
            if field.name in result.data:
                try:
                    validate_field(result.data[field.name], field.field_type, field.format_spec, field.optional)
                except ValidationError as e:
                    field_validation["valid"] = False
                    field_validation["errors"].append(str(e))
                    validation_result["errors"].append(f"Campo '{field.name}': {e}")
            else:
                if not field.optional:
                    field_validation["valid"] = False
                    field_validation["errors"].append("Campo obrigatório ausente")
                    validation_result["errors"].append(f"Campo obrigatório '{field.name}' ausente")
            
            validation_result["validated_fields"].append(field_validation)
        
        # Verificar campos extras
        field_names = {f.name for f in fields}
        extra_fields = set(result.data.keys()) - field_names
        if extra_fields:
            validation_result["warnings"].append(f"Campos extras encontrados: {', '.join(extra_fields)}")
        
        if validation_result["errors"]:
            validation_result["valid"] = False
        
        return validation_result