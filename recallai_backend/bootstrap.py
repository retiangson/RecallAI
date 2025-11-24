# recallai_backend/bootstrap.py

from recallai_backend.domain.domain_installer import DomainInstaller
from recallai_backend.business.service_installer import ServiceInstaller

# Global DI container for the entire backend
domain = DomainInstaller()
container = ServiceInstaller(domain)
