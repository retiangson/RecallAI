# recallai_backend/bootstrap.py
"""
DEPRECATED GLOBAL DI CONTAINER

We now use TRANSIENT, per-request DI.

Usage pattern in controllers should be:

    from fastapi import Depends
    from sqlalchemy.orm import Session
    from recallai_backend.core.db import get_db
    from recallai_backend.domain.domain_installer import DomainInstaller
    from recallai_backend.business.service_installer import ServiceInstaller

    @router.post("/something")
    def endpoint(dto: SomeDTO, db: Session = Depends(get_db)):
        domain = DomainInstaller(db)
        services = ServiceInstaller(domain)
        service = services.get_xyz_service()
        return service.do_work(...)

This file keeps a helper to build ServiceInstaller
and a deprecated `container` object for backwards compatibility.
"""

from typing import Any
from sqlalchemy.orm import Session

from recallai_backend.domain.domain_installer import DomainInstaller
from recallai_backend.business.service_installer import ServiceInstaller


def get_service_installer(db: Session) -> ServiceInstaller:
    """
    Factory helper to create a per-request ServiceInstaller.

    Example usage in a controller:

        def endpoint(dto: DTO, db: Session = Depends(get_db)):
            services = get_service_installer(db)
            svc = services.get_note_service()
            return svc.list_notes(dto.user_id)
    """
    domain = DomainInstaller(db)
    return ServiceInstaller(domain)


class _DeprecatedContainer:
    """
    Backwards-compat shim for old `container = ServiceInstaller(...)` usage.

    Any attempt to access attributes (e.g. container.get_note_service())
    will raise a clear runtime error telling you to switch to the new pattern.
    """

    def __getattr__(self, item: str) -> Any:
        raise RuntimeError(
            "Global DI container has been removed.\n"
            "Use per-request DI instead:\n\n"
            "  def endpoint(dto: DTO, db: Session = Depends(get_db)):\n"
            "      from recallai_backend.bootstrap import get_service_installer\n"
            "      services = get_service_installer(db)\n"
            "      svc = services.get_note_service()\n"
            "      return svc.list_notes(dto.user_id)\n"
        )


# Old code used: from recallai_backend.bootstrap import container
# We keep this name so imports don't crash, but any usage will raise.
container = _DeprecatedContainer()
