"""
Contractor Manager
Sistema de memória persistente para contratados/clientes.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Contractor:
    """Modelo de dados para um contratado/cliente."""
    
    # Identificação
    cnpj: str = ""
    razao_social: str = ""
    nome_fantasia: str = ""
    
    # Endereço
    logradouro: str = ""
    numero: str = ""
    complemento: str = ""
    bairro: str = ""
    cidade: str = ""
    uf: str = ""
    cep: str = ""
    
    # Contato
    telefone: str = ""
    email: str = ""
    contato_responsavel: str = ""
    
    # Metadados
    id: str = ""
    tags: List[str] = None
    observacoes: str = ""
    created_at: str = ""
    updated_at: str = ""
    last_used: str = ""
    usage_count: int = 0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        
        if not self.id:
            # Gerar ID baseado no CNPJ ou razão social
            if self.cnpj:
                self.id = self.cnpj.replace(".", "").replace("/", "").replace("-", "")
            else:
                # Fallback para nome sem espaços/caracteres especiais
                import re
                self.id = re.sub(r'[^a-zA-Z0-9]', '_', self.razao_social.lower())[:20]
        
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
            
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário serializable."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contractor':
        """Cria instância a partir de dicionário."""
        # Garantir que tags seja lista
        if 'tags' in data and data['tags'] is None:
            data['tags'] = []
        return cls(**data)
    
    def matches_search(self, query: str) -> bool:
        """Verifica se o contratado corresponde à busca."""
        query_lower = query.lower()
        search_fields = [
            self.cnpj,
            self.razao_social,
            self.nome_fantasia,
            self.email,
            " ".join(self.tags)
        ]
        
        return any(query_lower in field.lower() for field in search_fields if field)
    
    def to_template_fields(self, prefix: str = "") -> Dict[str, str]:
        """
        Converte dados do contratado para campos de template.
        
        Args:
            prefix: Prefixo para os campos (ex: "contratante_", "contratada_")
        """
        fields = {}
        
        # Dados básicos
        if self.razao_social:
            fields[f"{prefix}razaoSocial"] = self.razao_social
        
        if self.cnpj:
            fields[f"{prefix}cnpj"] = self.cnpj
            
        if self.nome_fantasia:
            fields[f"{prefix}nomeFantasia"] = self.nome_fantasia
        
        # Endereço completo
        endereco_parts = []
        if self.logradouro:
            endereco_parts.append(self.logradouro)
        if self.numero:
            endereco_parts.append(self.numero)
        if self.complemento:
            endereco_parts.append(self.complemento)
        if self.bairro:
            endereco_parts.append(self.bairro)
            
        if endereco_parts:
            fields[f"{prefix}logradouro"] = ", ".join(endereco_parts)
        
        if self.cidade:
            fields[f"{prefix}cidade"] = self.cidade
            
        if self.uf:
            fields[f"{prefix}uf"] = self.uf
            
        if self.cep:
            fields[f"{prefix}cep"] = self.cep
        
        # Contato
        if self.telefone:
            fields[f"{prefix}telefone"] = self.telefone
            
        if self.email:
            fields[f"{prefix}email"] = self.email
            
        if self.contato_responsavel:
            fields[f"{prefix}contato"] = self.contato_responsavel
        
        return fields


class ContractorManager:
    """Gerenciador de memória de contratados."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Inicializa o gerenciador.
        
        Args:
            data_dir: Diretório para armazenar dados
        """
        # Usar caminho absoluto se não for absoluto
        if not os.path.isabs(data_dir):
            # Obter diretório do projeto (3 níveis acima)
            project_root = Path(__file__).parent.parent.parent
            self.data_dir = project_root / data_dir
        else:
            self.data_dir = Path(data_dir)
            
        self.data_dir.mkdir(exist_ok=True)
        
        self.contractors_file = self.data_dir / "contractors.json"
        self._contractors = {}
        
        # Carregar dados existentes
        self._load_contractors()
        
        logger.info(f"ContractorManager inicializado com {len(self._contractors)} contratados")
    
    def _load_contractors(self):
        """Carrega contratados do arquivo JSON."""
        if self.contractors_file.exists():
            try:
                with open(self.contractors_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for contractor_id, contractor_data in data.items():
                    self._contractors[contractor_id] = Contractor.from_dict(contractor_data)
                    
                logger.info(f"Carregados {len(self._contractors)} contratados")
                
            except Exception as e:
                logger.error(f"Erro ao carregar contratados: {e}")
                self._contractors = {}
        else:
            logger.info("Arquivo de contratados não existe, iniciando com base vazia")
    
    def _save_contractors(self):
        """Salva contratados no arquivo JSON."""
        try:
            data = {
                contractor_id: contractor.to_dict()
                for contractor_id, contractor in self._contractors.items()
            }
            
            with open(self.contractors_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Salvos {len(self._contractors)} contratados")
            
        except Exception as e:
            logger.error(f"Erro ao salvar contratados: {e}")
            raise
    
    def add_contractor(self, contractor: Contractor, overwrite: bool = False) -> str:
        """
        Adiciona novo contratado.
        
        Args:
            contractor: Instância do contratado
            overwrite: Se deve sobrescrever caso já exista
            
        Returns:
            ID do contratado adicionado
            
        Raises:
            ValueError: Se contratado já existe e overwrite=False
        """
        if contractor.id in self._contractors and not overwrite:
            raise ValueError(f"Contratado {contractor.id} já existe. Use overwrite=True para atualizar.")
        
        # Atualizar timestamp
        if contractor.id in self._contractors:
            # Manter created_at original
            contractor.created_at = self._contractors[contractor.id].created_at
            contractor.usage_count = self._contractors[contractor.id].usage_count
        
        self._contractors[contractor.id] = contractor
        self._save_contractors()
        
        logger.info(f"Contratado adicionado/atualizado: {contractor.id} - {contractor.razao_social}")
        return contractor.id
    
    def get_contractor(self, contractor_id: str) -> Optional[Contractor]:
        """
        Busca contratado por ID.
        
        Args:
            contractor_id: ID do contratado
            
        Returns:
            Contratado encontrado ou None
        """
        contractor = self._contractors.get(contractor_id)
        
        if contractor:
            # Atualizar último uso
            contractor.last_used = datetime.now().isoformat()
            contractor.usage_count += 1
            self._save_contractors()
            
        return contractor
    
    def search_contractors(self, query: str, limit: int = 10) -> List[Contractor]:
        """
        Busca contratados por termo.
        
        Args:
            query: Termo de busca
            limit: Máximo de resultados
            
        Returns:
            Lista de contratados que correspondem à busca
        """
        matches = [
            contractor for contractor in self._contractors.values()
            if contractor.matches_search(query)
        ]
        
        # Ordenar por relevância (usage_count + updated_at)
        matches.sort(key=lambda c: (c.usage_count, c.updated_at), reverse=True)
        
        return matches[:limit]
    
    def list_contractors(self, sort_by: str = "usage_count") -> List[Contractor]:
        """
        Lista todos os contratados.
        
        Args:
            sort_by: Campo para ordenação (usage_count, updated_at, razao_social)
            
        Returns:
            Lista ordenada de contratados
        """
        contractors = list(self._contractors.values())
        
        if sort_by == "usage_count":
            contractors.sort(key=lambda c: c.usage_count, reverse=True)
        elif sort_by == "updated_at":
            contractors.sort(key=lambda c: c.updated_at, reverse=True)
        elif sort_by == "razao_social":
            contractors.sort(key=lambda c: c.razao_social.lower())
        
        return contractors
    
    def delete_contractor(self, contractor_id: str) -> bool:
        """
        Remove contratado.
        
        Args:
            contractor_id: ID do contratado
            
        Returns:
            True se removido, False se não encontrado
        """
        if contractor_id in self._contractors:
            contractor = self._contractors.pop(contractor_id)
            self._save_contractors()
            logger.info(f"Contratado removido: {contractor_id} - {contractor.razao_social}")
            return True
        
        return False
    
    def find_by_cnpj(self, cnpj: str) -> Optional[Contractor]:
        """
        Busca contratado por CNPJ.
        
        Args:
            cnpj: CNPJ com ou sem formatação
            
        Returns:
            Contratado encontrado ou None
        """
        # Limpar CNPJ
        clean_cnpj = ''.join(filter(str.isdigit, cnpj))
        
        for contractor in self._contractors.values():
            contractor_cnpj = ''.join(filter(str.isdigit, contractor.cnpj))
            if contractor_cnpj == clean_cnpj:
                return self.get_contractor(contractor.id)  # Atualiza usage
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da base de contratados."""
        contractors = list(self._contractors.values())
        
        return {
            "total_contractors": len(contractors),
            "most_used": max(contractors, key=lambda c: c.usage_count).razao_social if contractors else "N/A",
            "recently_added": max(contractors, key=lambda c: c.created_at).razao_social if contractors else "N/A",
            "with_cnpj": len([c for c in contractors if c.cnpj]),
            "with_email": len([c for c in contractors if c.email]),
            "total_usage": sum(c.usage_count for c in contractors)
        }
    
    def export_to_csv(self, output_path: str):
        """Exporta contratados para CSV."""
        import csv
        
        contractors = self.list_contractors("razao_social")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'razao_social', 'nome_fantasia', 'cnpj',
                'logradouro', 'cidade', 'uf', 'cep',
                'telefone', 'email', 'usage_count', 'last_used'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for contractor in contractors:
                row = {field: getattr(contractor, field, '') for field in fieldnames}
                writer.writerow(row)
        
        logger.info(f"Contratados exportados para {output_path}")