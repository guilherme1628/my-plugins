"""
Template_Filler MCP Server
Servidor MCP que expõe funcionalidades do Template_Filler para assistentes AI.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..core.google_drive_manager import GoogleDriveManager
from ..core.template_parser import TemplateParser
from ..core.data_collector import DataCollector
from ..core.document_generator import DocumentGenerator
from ..core.contractor_manager import ContractorManager, Contractor
from ..integrations.receitaws import ReceitaWSClient, ReceitaWSError

logger = logging.getLogger(__name__)


def create_mcp_server() -> FastMCP:
    """
    Cria e configura o servidor MCP para Template_Filler.
    
    Returns:
        FastMCP: Instância configurada do servidor MCP
    """
    mcp = FastMCP(
        name="Template_Filler",
        # TODO: Adicionar lifespan para inicializar componentes
    )
    
    # Instâncias dos componentes principais (inicializadas sob demanda)
    _drive_manager = None
    _template_parser = None
    _data_collector = None
    _document_generator = None
    _receitaws_client = None
    _contractor_manager = None
    
    def get_drive_manager() -> GoogleDriveManager:
        """Lazy loading do GoogleDriveManager."""
        nonlocal _drive_manager
        if _drive_manager is None:
            import os
            # Obter credentials path do ambiente ou usar padrão
            credentials_path = os.getenv(
                'GOOGLE_APPLICATION_CREDENTIALS',
                'backoffice-469614-3a9d99cb9df3.json'
            )
            _drive_manager = GoogleDriveManager(credentials_path)
        return _drive_manager
    
    def get_template_parser() -> TemplateParser:
        """Lazy loading do TemplateParser."""
        nonlocal _template_parser
        if _template_parser is None:
            _template_parser = TemplateParser(get_drive_manager())
        return _template_parser
    
    def get_data_collector() -> DataCollector:
        """Lazy loading do DataCollector.""" 
        nonlocal _data_collector
        if _data_collector is None:
            _data_collector = DataCollector()
        return _data_collector
    
    def get_document_generator() -> DocumentGenerator:
        """Lazy loading do DocumentGenerator."""
        nonlocal _document_generator
        if _document_generator is None:
            _document_generator = DocumentGenerator(get_drive_manager())
        return _document_generator
    
    def get_receitaws_client() -> ReceitaWSClient:
        """Lazy loading do ReceitaWSClient."""
        nonlocal _receitaws_client
        if _receitaws_client is None:
            _receitaws_client = ReceitaWSClient()
        return _receitaws_client
    
    def get_contractor_manager() -> ContractorManager:
        """Lazy loading do ContractorManager."""
        nonlocal _contractor_manager
        if _contractor_manager is None:
            _contractor_manager = ContractorManager()
        return _contractor_manager
    
    @mcp.tool()
    def list_templates() -> List[Dict[str, Any]]:
        """
        Lista todos os templates disponíveis no Google Drive.
        
        Returns:
            Lista de templates com id, nome, data de modificação
        """
        try:
            drive_manager = get_drive_manager()
            templates = drive_manager.list_templates()
            
            # Converter para formato serializable
            result = []
            for template in templates:
                result.append({
                    "id": template["id"],
                    "name": template["name"],
                    "modified": template.get("modified", "N/A"),
                    "size": template.get("size", "N/A")
                })
            
            logger.info(f"Listados {len(result)} templates via MCP")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao listar templates via MCP: {e}")
            raise ValueError(f"Erro ao listar templates: {str(e)}")
    
    @mcp.tool()
    def parse_template(template_id: str) -> Dict[str, Any]:
        """
        Analisa um template específico e extrai todos os marcadores encontrados.
        
        Args:
            template_id: ID do template no Google Drive
            
        Returns:
            Dicionário com informações do template e lista de campos detectados
        """
        try:
            template_parser = get_template_parser()
            drive_manager = get_drive_manager()
            
            # Obter informações básicas do template
            templates = drive_manager.list_templates()
            template_info = None
            for template in templates:
                if template["id"] == template_id:
                    template_info = template
                    break
            
            if not template_info:
                raise ValueError(f"Template com ID '{template_id}' não encontrado")
            
            # Extrair campos do template
            logger.info(f"Analisando template: {template_info['name']}")
            fields = template_parser.extract_fields(template_id, interactive=False)
            
            # Converter campos para formato serializable
            fields_data = []
            for field in fields:
                field_dict = {
                    "name": field.name,
                    "type": field.type,
                    "format": field.format,
                    "required": field.required,
                    "description": field.description or "",
                    "example": field.example or ""
                }
                fields_data.append(field_dict)
            
            result = {
                "template_info": {
                    "id": template_info["id"],
                    "name": template_info["name"],
                    "modified": template_info.get("modified", "N/A"),
                    "size": template_info.get("size", "N/A")
                },
                "fields": fields_data,
                "total_fields": len(fields_data),
                "field_types": list(set(field.type for field in fields)),
                "required_fields": [field.name for field in fields if field.required],
                "optional_fields": [field.name for field in fields if not field.required]
            }
            
            logger.info(f"Template analisado: {len(fields_data)} campos encontrados")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao analisar template via MCP: {e}")
            raise ValueError(f"Erro ao analisar template: {str(e)}")
    
    @mcp.tool()
    def collect_data(template_id: str, field_data: Dict[str, str], template_name: str = "") -> Dict[str, Any]:
        """
        Coleta e valida dados para um template específico.
        Esta tool é projetada para ser usada após conversa natural com o usuário.
        
        Args:
            template_id: ID do template no Google Drive
            field_data: Dicionário com dados coletados (campo -> valor)
            template_name: Nome do template (opcional, será detectado automaticamente)
            
        Returns:
            Dicionário com resultado da coleta e path do arquivo salvo
        """
        try:
            template_parser = get_template_parser()
            data_collector = get_data_collector()
            drive_manager = get_drive_manager()
            
            # Obter informações do template se não fornecidas
            if not template_name:
                templates = drive_manager.list_templates()
                for template in templates:
                    if template["id"] == template_id:
                        template_name = template["name"]
                        break
                
                if not template_name:
                    raise ValueError(f"Template com ID '{template_id}' não encontrado")
            
            # Validar campos usando o TemplateParser
            logger.info(f"Validando dados para template: {template_name}")
            fields = template_parser.extract_fields(template_id, interactive=False)
            
            # Criar mapeamento de campos esperados
            expected_fields = {field.name: field for field in fields}
            
            # Validar dados fornecidos
            validated_data = {}
            validation_errors = []
            missing_required = []
            
            for field in fields:
                field_name = field.name
                field_value = field_data.get(field_name, "")
                
                if field.required and not field_value.strip():
                    missing_required.append(field_name)
                    continue
                
                if field_value.strip():  # Só validar se não estiver vazio
                    try:
                        # Usar os validadores existentes
                        from ..utils.validators import validate_field
                        validate_field(field_value, field.type, field.format, optional=not field.required)
                        validated_data[field_name] = field_value.strip()
                    except Exception as validation_error:
                        validation_errors.append(f"{field_name}: {str(validation_error)}")
                else:
                    # Campo opcional vazio
                    validated_data[field_name] = ""
            
            # Verificar se há erros críticos
            if missing_required:
                raise ValueError(f"Campos obrigatórios faltando: {', '.join(missing_required)}")
            
            if validation_errors:
                raise ValueError(f"Erros de validação: {'; '.join(validation_errors)}")
            
            # Criar resultado da coleta usando a estrutura existente
            from ..core.data_collector import DataCollectionResult
            import datetime
            
            collection_result = DataCollectionResult(
                template_id=template_id,
                template_name=template_name,
                data=validated_data,
                collected_at=datetime.datetime.now().isoformat(),
                metadata={
                    "total_fields": len(validated_data),
                    "collector_version": "1.0-mcp",
                    "collected_via": "mcp_conversational"
                }
            )
            
            # Salvar dados coletados
            output_path = data_collector.save_to_file(collection_result)
            
            # Preparar resposta
            result = {
                "success": True,
                "template_id": template_id,
                "template_name": template_name,
                "collected_fields": len(validated_data),
                "saved_to": str(output_path),
                "collected_at": collection_result.collected_at,
                "field_summary": {
                    "total": len(validated_data),
                    "filled": len([v for v in validated_data.values() if v.strip()]),
                    "empty": len([v for v in validated_data.values() if not v.strip()])
                },
                "ready_for_generation": len(missing_required) == 0 and len(validation_errors) == 0
            }
            
            logger.info(f"Dados coletados via MCP: {len(validated_data)} campos, salvos em {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao coletar dados via MCP: {e}")
            raise ValueError(f"Erro ao coletar dados: {str(e)}")
    
    @mcp.tool()
    def generate_document(template_id: str, data_source: Any, custom_name: str = "") -> Dict[str, Any]:
        """
        Gera documento final a partir de template e dados coletados.
        
        Args:
            template_id: ID do template no Google Drive
            data_source: Path do arquivo de dados OU dados como dict/JSON string
            custom_name: Nome personalizado para o documento (opcional)
            
        Returns:
            Dicionário com informações do documento gerado
        """
        try:
            document_generator = get_document_generator()
            data_collector = get_data_collector()
            drive_manager = get_drive_manager()
            
            # Determinar o tipo de data_source e processar adequadamente
            collection_result = None
            
            if isinstance(data_source, dict):
                # data_source é dict com dados
                data_dict = data_source
                
                # Obter nome do template
                templates = drive_manager.list_templates()
                template_name = None
                for template in templates:
                    if template["id"] == template_id:
                        template_name = template["name"]
                        break
                
                if not template_name:
                    raise ValueError(f"Template com ID '{template_id}' não encontrado")
                
                # Criar DataCollectionResult
                from ..core.data_collector import DataCollectionResult
                import datetime
                
                collection_result = DataCollectionResult(
                    template_id=template_id,
                    template_name=template_name,
                    data=data_dict,
                    collected_at=datetime.datetime.now().isoformat(),
                    metadata={
                        "total_fields": len(data_dict),
                        "collector_version": "1.0-mcp",
                        "collected_via": "mcp_direct_dict"
                    }
                )
                
            elif isinstance(data_source, str) and data_source.startswith('{') and data_source.endswith('}'):
                # data_source é JSON string com dados
                import json
                try:
                    data_dict = json.loads(data_source)
                    
                    # Obter nome do template
                    templates = drive_manager.list_templates()
                    template_name = None
                    for template in templates:
                        if template["id"] == template_id:
                            template_name = template["name"]
                            break
                    
                    if not template_name:
                        raise ValueError(f"Template com ID '{template_id}' não encontrado")
                    
                    # Criar DataCollectionResult
                    from ..core.data_collector import DataCollectionResult
                    import datetime
                    
                    collection_result = DataCollectionResult(
                        template_id=template_id,
                        template_name=template_name,
                        data=data_dict,
                        collected_at=datetime.datetime.now().isoformat(),
                        metadata={
                            "total_fields": len(data_dict),
                            "collector_version": "1.0-mcp",
                            "collected_via": "mcp_direct"
                        }
                    )
                    
                except json.JSONDecodeError as e:
                    raise ValueError(f"Dados JSON inválidos: {str(e)}")
                    
            else:
                # data_source é path para arquivo
                from pathlib import Path
                data_path = Path(data_source)
                
                if not data_path.exists():
                    raise ValueError(f"Arquivo de dados não encontrado: {data_source}")
                
                # Carregar dados do arquivo
                collection_result = data_collector.load_from_file(data_path)
                
                # Verificar se template_id corresponde
                if collection_result.template_id != template_id:
                    logger.warning(f"Template ID dos dados ({collection_result.template_id}) difere do solicitado ({template_id})")
            
            if not collection_result:
                raise ValueError("Não foi possível carregar dados para geração")
            
            logger.info(f"Gerando documento para template: {collection_result.template_name}")
            logger.info(f"Campos disponíveis: {len(collection_result.data)}")
            
            # Gerar documento
            generation_result = document_generator.generate_document(
                template_id=template_id,
                collection_result=collection_result,
                custom_name=custom_name if custom_name else None
            )
            
            # Preparar resposta detalhada
            result = {
                "success": True,
                "document_info": {
                    "id": generation_result.document_id,
                    "name": generation_result.document_name,
                    "url": generation_result.document_url,
                    "preview_url": f"https://docs.google.com/document/d/{generation_result.document_id}/preview"
                },
                "template_info": {
                    "id": generation_result.template_name,
                    "name": collection_result.template_name
                },
                "generation_details": {
                    "generated_at": generation_result.generated_at,
                    "fields_used": len(collection_result.data),
                    "data_source": "file" if not data_source.startswith('{') else "direct",
                    "custom_name_used": bool(custom_name)
                },
                "next_steps": {
                    "edit_document": generation_result.document_url,
                    "view_document": f"https://docs.google.com/document/d/{generation_result.document_id}/preview",
                    "download_pdf": f"https://docs.google.com/document/d/{generation_result.document_id}/export?format=pdf"
                }
            }
            
            logger.info(f"Documento gerado via MCP: {generation_result.document_name}")
            logger.info(f"URL: {generation_result.document_url}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar documento via MCP: {e}")
            raise ValueError(f"Erro ao gerar documento: {str(e)}")
    
    @mcp.tool()
    def lookup_cnpj(cnpj: str) -> Dict[str, Any]:
        """
        Busca dados automáticos de empresa via CNPJ usando ReceitaWS.
        
        Args:
            cnpj: CNPJ com ou sem formatação (ex: "12.345.678/0001-90" ou "12345678000190")
            
        Returns:
            Dicionário com dados da empresa e campos formatados para templates
        """
        try:
            receitaws_client = get_receitaws_client()
            
            logger.info(f"Buscando dados do CNPJ: {cnpj}")
            
            # Buscar dados brutos
            raw_data = receitaws_client.get_company_data(cnpj)
            
            # Extrair campos formatados para templates
            template_fields = receitaws_client.extract_template_fields(raw_data)
            
            # Preparar resposta estruturada
            result = {
                "success": True,
                "cnpj_consulted": cnpj,
                "company_info": {
                    "nome": raw_data.get("nome", ""),
                    "fantasia": raw_data.get("fantasia", ""),
                    "cnpj": raw_data.get("cnpj", ""),
                    "situacao": raw_data.get("situacao", ""),
                    "atividade_principal": raw_data.get("atividade_principal", [{}])[0].get("text", "") if raw_data.get("atividade_principal") else ""
                },
                "address_info": {
                    "logradouro": raw_data.get("logradouro", ""),
                    "numero": raw_data.get("numero", ""),
                    "complemento": raw_data.get("complemento", ""),
                    "bairro": raw_data.get("bairro", ""),
                    "municipio": raw_data.get("municipio", ""),
                    "uf": raw_data.get("uf", ""),
                    "cep": raw_data.get("cep", "")
                },
                "contact_info": {
                    "telefone": raw_data.get("telefone", ""),
                    "email": raw_data.get("email", "")
                },
                "template_fields": template_fields,
                "fields_extracted": len(template_fields),
                "usage_tip": "Use os campos de 'template_fields' diretamente no collect_data()"
            }
            
            logger.info(f"Dados obtidos com sucesso para CNPJ {cnpj}: {len(template_fields)} campos extraídos")
            return result
            
        except ReceitaWSError as e:
            logger.error(f"Erro ReceitaWS ao buscar CNPJ {cnpj}: {e}")
            raise ValueError(f"Erro ao consultar CNPJ: {str(e)}")
        except Exception as e:
            logger.error(f"Erro geral ao buscar CNPJ {cnpj}: {e}")
            raise ValueError(f"Erro interno ao consultar CNPJ: {str(e)}")
    
    @mcp.tool()
    def manage_contractors(action: str, contractor_data: Dict[str, Any] = None, query: str = "", contractor_id: str = "") -> Dict[str, Any]:
        """
        Gerencia memória de contratados/clientes para reutilização em documentos.
        
        Args:
            action: Ação a realizar (list, search, get, save, delete, from_cnpj)
            contractor_data: Dados do contratado (para action=save)
            query: Termo de busca (para action=search)
            contractor_id: ID do contratado (para action=get, delete)
            
        Returns:
            Resultado da operação solicitada
        """
        try:
            contractor_manager = get_contractor_manager()
            
            if action == "list":
                # Listar todos os contratados
                contractors = contractor_manager.list_contractors("usage_count")
                result = {
                    "success": True,
                    "action": "list",
                    "contractors": [
                        {
                            "id": c.id,
                            "razao_social": c.razao_social,
                            "cnpj": c.cnpj,
                            "cidade": c.cidade,
                            "usage_count": c.usage_count,
                            "last_used": c.last_used
                        }
                        for c in contractors
                    ],
                    "total": len(contractors),
                    "stats": contractor_manager.get_stats()
                }
                
                logger.info(f"Listados {len(contractors)} contratados via MCP")
                return result
            
            elif action == "search":
                # Buscar contratados por termo
                if not query:
                    raise ValueError("Campo 'query' é obrigatório para action=search")
                
                contractors = contractor_manager.search_contractors(query, limit=10)
                result = {
                    "success": True,
                    "action": "search",
                    "query": query,
                    "contractors": [
                        {
                            "id": c.id,
                            "razao_social": c.razao_social,
                            "cnpj": c.cnpj,
                            "nome_fantasia": c.nome_fantasia,
                            "cidade": f"{c.cidade} - {c.uf}" if c.cidade and c.uf else "",
                            "email": c.email,
                            "usage_count": c.usage_count,
                            "template_fields_preview": list(c.to_template_fields("contratante_").keys())[:5]
                        }
                        for c in contractors
                    ],
                    "found": len(contractors),
                    "usage_tip": "Use get() com o ID para obter campos completos para templates"
                }
                
                logger.info(f"Busca '{query}' encontrou {len(contractors)} contratados")
                return result
            
            elif action == "get":
                # Obter contratado específico com todos os campos
                if not contractor_id:
                    raise ValueError("Campo 'contractor_id' é obrigatório para action=get")
                
                contractor = contractor_manager.get_contractor(contractor_id)
                if not contractor:
                    raise ValueError(f"Contratado '{contractor_id}' não encontrado")
                
                result = {
                    "success": True,
                    "action": "get",
                    "contractor": {
                        "id": contractor.id,
                        "razao_social": contractor.razao_social,
                        "nome_fantasia": contractor.nome_fantasia,
                        "cnpj": contractor.cnpj,
                        "endereco_completo": f"{contractor.logradouro}, {contractor.numero}, {contractor.bairro}" if contractor.logradouro else "",
                        "cidade": contractor.cidade,
                        "uf": contractor.uf,
                        "cep": contractor.cep,
                        "telefone": contractor.telefone,
                        "email": contractor.email,
                        "contato_responsavel": contractor.contato_responsavel,
                        "tags": contractor.tags,
                        "usage_count": contractor.usage_count,
                        "last_used": contractor.last_used
                    },
                    "template_fields": {
                        "contratante": contractor.to_template_fields("contratante_"),
                        "contratada": contractor.to_template_fields("contratada_"),
                        "generic": contractor.to_template_fields("")
                    },
                    "usage_tip": "Use os campos de 'template_fields' diretamente no collect_data()"
                }
                
                logger.info(f"Contratado obtido via MCP: {contractor.razao_social}")
                return result
            
            elif action == "save":
                # Salvar/atualizar contratado
                if not contractor_data:
                    raise ValueError("Campo 'contractor_data' é obrigatório para action=save")
                
                # Criar instância do contratado
                contractor = Contractor(
                    cnpj=contractor_data.get("cnpj", ""),
                    razao_social=contractor_data.get("razao_social", ""),
                    nome_fantasia=contractor_data.get("nome_fantasia", ""),
                    logradouro=contractor_data.get("logradouro", ""),
                    numero=contractor_data.get("numero", ""),
                    complemento=contractor_data.get("complemento", ""),
                    bairro=contractor_data.get("bairro", ""),
                    cidade=contractor_data.get("cidade", ""),
                    uf=contractor_data.get("uf", ""),
                    cep=contractor_data.get("cep", ""),
                    telefone=contractor_data.get("telefone", ""),
                    email=contractor_data.get("email", ""),
                    contato_responsavel=contractor_data.get("contato_responsavel", ""),
                    tags=contractor_data.get("tags", []),
                    observacoes=contractor_data.get("observacoes", "")
                )
                
                # Validar dados mínimos
                if not contractor.razao_social and not contractor.cnpj:
                    raise ValueError("Pelo menos 'razao_social' ou 'cnpj' deve ser fornecido")
                
                contractor_id = contractor_manager.add_contractor(contractor, overwrite=True)
                
                result = {
                    "success": True,
                    "action": "save",
                    "contractor_id": contractor_id,
                    "razao_social": contractor.razao_social,
                    "saved_fields": len([v for v in contractor.to_dict().values() if v]),
                    "template_fields_available": len(contractor.to_template_fields("")),
                    "usage_tip": f"Use manage_contractors(action='get', contractor_id='{contractor_id}') para obter campos"
                }
                
                logger.info(f"Contratado salvo via MCP: {contractor_id} - {contractor.razao_social}")
                return result
            
            elif action == "delete":
                # Remover contratado
                if not contractor_id:
                    raise ValueError("Campo 'contractor_id' é obrigatório para action=delete")
                
                success = contractor_manager.delete_contractor(contractor_id)
                if not success:
                    raise ValueError(f"Contratado '{contractor_id}' não encontrado")
                
                result = {
                    "success": True,
                    "action": "delete",
                    "contractor_id": contractor_id,
                    "message": f"Contratado '{contractor_id}' removido com sucesso"
                }
                
                logger.info(f"Contratado removido via MCP: {contractor_id}")
                return result
            
            elif action == "from_cnpj":
                # Criar contratado a partir de dados do CNPJ (ReceitaWS)
                if not query:  # usar query como CNPJ
                    raise ValueError("Campo 'query' com CNPJ é obrigatório para action=from_cnpj")
                
                # Verificar se já existe
                existing = contractor_manager.find_by_cnpj(query)
                if existing:
                    return {
                        "success": True,
                        "action": "from_cnpj",
                        "message": "Contratado já existe na base de dados",
                        "existing_contractor": {
                            "id": existing.id,
                            "razao_social": existing.razao_social,
                            "usage_count": existing.usage_count
                        },
                        "usage_tip": f"Use manage_contractors(action='get', contractor_id='{existing.id}') para obter dados"
                    }
                
                # Buscar dados via ReceitaWS
                receitaws_client = get_receitaws_client()
                cnpj_data = receitaws_client.get_company_data(query)
                
                # Criar contratado a partir dos dados
                contractor = Contractor(
                    cnpj=cnpj_data.get("cnpj", ""),
                    razao_social=cnpj_data.get("nome", ""),
                    nome_fantasia=cnpj_data.get("fantasia", ""),
                    logradouro=cnpj_data.get("logradouro", ""),
                    numero=cnpj_data.get("numero", ""),
                    complemento=cnpj_data.get("complemento", ""),
                    bairro=cnpj_data.get("bairro", ""),
                    cidade=cnpj_data.get("municipio", ""),
                    uf=cnpj_data.get("uf", ""),
                    cep=cnpj_data.get("cep", ""),
                    telefone=cnpj_data.get("telefone", ""),
                    email=cnpj_data.get("email", ""),
                    tags=["auto_receitaws"]
                )
                
                contractor_id = contractor_manager.add_contractor(contractor)
                
                result = {
                    "success": True,
                    "action": "from_cnpj",
                    "cnpj": query,
                    "contractor_id": contractor_id,
                    "razao_social": contractor.razao_social,
                    "fields_imported": len([v for v in contractor.to_dict().values() if v]),
                    "template_fields": contractor.to_template_fields("contratante_"),
                    "usage_tip": "Contratado salvo automaticamente e pronto para uso em templates"
                }
                
                logger.info(f"Contratado criado via CNPJ: {contractor_id} - {contractor.razao_social}")
                return result
            
            else:
                raise ValueError(f"Ação '{action}' não suportada. Use: list, search, get, save, delete, from_cnpj")
                
        except Exception as e:
            logger.error(f"Erro ao gerenciar contratados via MCP: {e}")
            raise ValueError(f"Erro ao gerenciar contratados: {str(e)}")
    
    @mcp.tool()
    def generate_document_inline(template_id: str, field_data: Dict[str, Any], force_generate: bool = False) -> Dict[str, Any]:
        """
        Gera documento diretamente sem salvar arquivos no sistema.
        VALIDA campos obrigatórios antes de gerar - falha se dados incompletos.
        
        Args:
            template_id: ID do template no Google Drive
            field_data: Dados para preenchimento dos campos
            force_generate: Se True, gera mesmo com campos faltantes (usar com cuidado)
            
        Returns:
            Documento gerado com conteúdo pronto para edição/salvamento
        """
        try:
            # VALIDAÇÃO OBRIGATÓRIA ANTES DE GERAR
            if not force_generate:
                validation = validate_template_data(template_id, field_data)
                
                if not validation["validation_summary"]["can_generate_document"]:
                    missing_fields = validation["missing_required"]
                    missing_names = [f["name"] for f in missing_fields]
                    
                    raise ValueError(
                        f"❌ DOCUMENTO NÃO PODE SER GERADO - Campos obrigatórios faltantes:\n" +
                        f"📋 Faltam {len(missing_fields)} campos: {', '.join(missing_names)}\n" +
                        f"📊 Completado: {validation['validation_summary']['completion_percentage']:.1f}%\n" +
                        f"💡 Use 'smart_data_collection' primeiro ou forneça todos os campos obrigatórios."
                    )
            template_parser = get_template_parser()
            drive_manager = get_drive_manager()
            document_generator = get_document_generator()
            
            # Obter informações do template
            templates = drive_manager.list_templates()
            template_info = None
            for template in templates:
                if template["id"] == template_id:
                    template_info = template
                    break
            
            if not template_info:
                raise ValueError(f"Template com ID '{template_id}' não encontrado")
            
            logger.info(f"Gerando documento inline para template: {template_info['name']}")
            
            # Criar DataCollectionResult temporário (sem salvar)
            from ..core.data_collector import DataCollectionResult
            import datetime
            
            collection_result = DataCollectionResult(
                template_id=template_id,
                template_name=template_info["name"],
                data=field_data,
                collected_at=datetime.datetime.now().isoformat(),
                metadata={
                    "total_fields": len(field_data),
                    "collector_version": "1.0-mcp-inline",
                    "collected_via": "mcp_inline_generation"
                }
            )
            
            # Gerar documento
            generation_result = document_generator.generate_document(
                template_id=template_id,
                collection_result=collection_result,
                custom_name=None
            )
            
            # Baixar conteúdo do documento gerado
            try:
                # Usar Google Docs API para obter conteúdo como texto
                docs_service = drive_manager.docs_service
                document = docs_service.documents().get(documentId=generation_result.document_id).execute()
                
                # Extrair texto do documento
                content = ""
                for element in document.get('body', {}).get('content', []):
                    if 'paragraph' in element:
                        for text_run in element['paragraph'].get('elements', []):
                            if 'textRun' in text_run:
                                content += text_run['textRun'].get('content', '')
                
                # Preparar resposta com conteúdo inline
                result = {
                    "success": True,
                    "template_info": {
                        "id": template_info["id"],
                        "name": template_info["name"]
                    },
                    "document_info": {
                        "id": generation_result.document_id,
                        "name": generation_result.document_name,
                        "url": generation_result.document_url,
                        "preview_url": f"https://docs.google.com/document/d/{generation_result.document_id}/preview"
                    },
                    "document_content": content,
                    "generation_details": {
                        "generated_at": generation_result.generated_at,
                        "fields_used": len(field_data),
                        "generation_mode": "inline"
                    },
                    "field_data_used": field_data,
                    "next_steps": {
                        "edit_online": generation_result.document_url,
                        "view_document": f"https://docs.google.com/document/d/{generation_result.document_id}/preview",
                        "download_pdf": f"https://docs.google.com/document/d/{generation_result.document_id}/export?format=pdf",
                        "download_docx": f"https://docs.google.com/document/d/{generation_result.document_id}/export?format=docx"
                    },
                    "usage_tip": "Documento criado no Google Drive e conteúdo retornado inline. Use os links para acessar ou baixar."
                }
                
                logger.info(f"Documento gerado inline: {generation_result.document_name}")
                logger.info(f"Conteúdo extraído: {len(content)} caracteres")
                
                return result
                
            except Exception as content_error:
                logger.warning(f"Erro ao extrair conteúdo do documento: {content_error}")
                
                # Retornar informações do documento mesmo sem conteúdo
                result = {
                    "success": True,
                    "template_info": {
                        "id": template_info["id"],
                        "name": template_info["name"]
                    },
                    "document_info": {
                        "id": generation_result.document_id,
                        "name": generation_result.document_name,
                        "url": generation_result.document_url,
                        "preview_url": f"https://docs.google.com/document/d/{generation_result.document_id}/preview"
                    },
                    "document_content": "⚠️ Documento criado mas conteúdo não pôde ser extraído automaticamente",
                    "generation_details": {
                        "generated_at": generation_result.generated_at,
                        "fields_used": len(field_data),
                        "generation_mode": "inline_fallback"
                    },
                    "field_data_used": field_data,
                    "next_steps": {
                        "edit_online": generation_result.document_url,
                        "view_document": f"https://docs.google.com/document/d/{generation_result.document_id}/preview",
                        "download_pdf": f"https://docs.google.com/document/d/{generation_result.document_id}/export?format=pdf",
                        "download_docx": f"https://docs.google.com/document/d/{generation_result.document_id}/export?format=docx"
                    },
                    "usage_tip": "Documento criado no Google Drive. Use os links para acessar, visualizar ou baixar."
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Erro ao gerar documento inline via MCP: {e}")
            raise ValueError(f"Erro ao gerar documento inline: {str(e)}")
    
    @mcp.tool()
    def validate_template_data(template_id: str, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados fornecidos contra os campos obrigatórios do template.
        Retorna lista de campos obrigatórios que estão faltando.
        
        Args:
            template_id: ID do template no Google Drive
            field_data: Dados fornecidos pelo usuário
            
        Returns:
            Validação detalhada com campos faltantes
        """
        try:
            template_parser = get_template_parser()
            drive_manager = get_drive_manager()
            
            # Obter informações do template
            templates = drive_manager.list_templates()
            template_info = None
            for template in templates:
                if template["id"] == template_id:
                    template_info = template
                    break
            
            if not template_info:
                raise ValueError(f"Template com ID '{template_id}' não encontrado")
            
            # Analisar campos do template
            logger.info(f"Validando dados para template: {template_info['name']}")
            fields = template_parser.extract_fields(template_id, interactive=False)
            
            # Classificar campos
            required_fields = []
            optional_fields = []
            provided_fields = list(field_data.keys())
            
            for field in fields:
                if field.required:
                    required_fields.append({
                        "name": field.name,
                        "type": field.type,
                        "description": getattr(field, 'description', ''),
                        "provided": field.name in field_data and bool(str(field_data[field.name]).strip())
                    })
                else:
                    optional_fields.append({
                        "name": field.name,
                        "type": field.type,
                        "description": getattr(field, 'description', ''),
                        "provided": field.name in field_data and bool(str(field_data[field.name]).strip())
                    })
            
            # Verificar campos obrigatórios faltantes
            missing_required = [f for f in required_fields if not f["provided"]]
            provided_required = [f for f in required_fields if f["provided"]]
            provided_optional = [f for f in optional_fields if f["provided"]]
            
            # Calcular completeness
            total_required = len(required_fields)
            completed_required = len(provided_required)
            completion_percentage = (completed_required / total_required * 100) if total_required > 0 else 100
            
            can_generate = len(missing_required) == 0
            
            result = {
                "success": True,
                "template_info": {
                    "id": template_info["id"],
                    "name": template_info["name"]
                },
                "validation_summary": {
                    "can_generate_document": can_generate,
                    "completion_percentage": round(completion_percentage, 1),
                    "total_required_fields": total_required,
                    "completed_required_fields": completed_required,
                    "missing_required_fields": len(missing_required),
                    "provided_optional_fields": len(provided_optional)
                },
                "missing_required": missing_required,
                "provided_required": provided_required,
                "provided_optional": provided_optional,
                "field_data_provided": field_data,
                "next_steps": {
                    "action_needed": "collect_missing_fields" if not can_generate else "ready_to_generate",
                    "message": f"Faltam {len(missing_required)} campos obrigatórios" if not can_generate else "Todos os campos obrigatórios fornecidos"
                }
            }
            
            logger.info(f"Validação concluída: {completion_percentage:.1f}% completo, pode gerar: {can_generate}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao validar dados do template: {e}")
            raise ValueError(f"Erro na validação: {str(e)}")
    
    @mcp.tool()
    def smart_data_collection(template_id: str, cnpj: str = None) -> Dict[str, Any]:
        """
        Coleta inteligente de dados: busca CNPJ se fornecido e identifica campos que ainda precisam ser coletados.
        NÃO gera documento - apenas prepara dados e mostra o que falta.
        
        Args:
            template_id: ID do template no Google Drive
            cnpj: CNPJ para buscar dados automaticamente (opcional)
            
        Returns:
            Dados coletados e lista de campos que ainda precisam ser fornecidos
        """
        try:
            collected_data = {}
            
            # Buscar dados do CNPJ se fornecido
            if cnpj:
                logger.info(f"Buscando dados do CNPJ: {cnpj}")
                try:
                    receitaws_client = get_receitaws_client()
                    raw_cnpj_data = receitaws_client.get_company_data(cnpj)
                    cnpj_fields = receitaws_client.extract_template_fields(raw_cnpj_data)
                    collected_data.update(cnpj_fields)
                    
                    # Salvar na memória
                    contractor_manager = get_contractor_manager()
                    existing = contractor_manager.find_by_cnpj(cnpj)
                    if not existing:
                        from ..core.contractor_manager import Contractor
                        contractor = Contractor(
                            cnpj=raw_cnpj_data.get("cnpj", ""),
                            razao_social=raw_cnpj_data.get("nome", ""),
                            nome_fantasia=raw_cnpj_data.get("fantasia", ""),
                            logradouro=raw_cnpj_data.get("logradouro", ""),
                            numero=raw_cnpj_data.get("numero", ""),
                            bairro=raw_cnpj_data.get("bairro", ""),
                            cidade=raw_cnpj_data.get("municipio", ""),
                            uf=raw_cnpj_data.get("uf", ""),
                            cep=raw_cnpj_data.get("cep", ""),
                            telefone=raw_cnpj_data.get("telefone", ""),
                            email=raw_cnpj_data.get("email", ""),
                            tags=["auto_receitaws"]
                        )
                        contractor_manager.add_contractor(contractor)
                    
                except Exception as cnpj_error:
                    logger.warning(f"Erro ao buscar CNPJ: {cnpj_error}")
            
            # Validar dados coletados contra template
            validation_result = validate_template_data(template_id, collected_data)
            
            # Preparar resposta
            result = {
                "success": True,
                "cnpj_processed": cnpj,
                "data_collected": collected_data,
                "fields_from_cnpj": len(collected_data),
                "validation": validation_result["validation_summary"],
                "missing_required_fields": validation_result["missing_required"],
                "next_steps": {
                    "action": "provide_missing_fields" if not validation_result["validation_summary"]["can_generate_document"] else "ready_to_generate",
                    "message": f"Coletados {len(collected_data)} campos via CNPJ. " + 
                              (f"Ainda precisa fornecer {len(validation_result['missing_required'])} campos obrigatórios." 
                               if not validation_result["validation_summary"]["can_generate_document"] 
                               else "Todos os dados necessários coletados!"),
                    "missing_fields_details": validation_result["missing_required"]
                },
                "usage_tip": "Use 'generate_document_inline' apenas DEPOIS de fornecer todos os campos obrigatórios"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro na coleta inteligente de dados: {e}")
            raise ValueError(f"Erro na coleta de dados: {str(e)}")
    
    return mcp


if __name__ == "__main__":
    """Execução direta do servidor MCP."""
    server = create_mcp_server()
    server.run()