"""Template_Filler core modules (local-only)."""

from .contractor_manager import ContractorManager, Contractor
from .naming_config import NamingConfigManager

__all__ = ["ContractorManager", "Contractor", "NamingConfigManager"]
