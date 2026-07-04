"""
Clase abstracta base del dominio Software FJ.
Define identificador, fecha de creación y estado activo compartidos por entidades.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Entidad(ABC):
    """Estructura común de clientes y servicios."""

    _contador_ids: int = 0

    def __init__(self) -> None:
        # Asignación secuencial de identificador y metadatos de creación
        Entidad._contador_ids += 1
        self._id = Entidad._contador_ids
        self._fecha_creacion = datetime.now()
        self._activo = True

    @property
    def id(self) -> int:
        return self._id

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @property
    def activo(self) -> bool:
        return self._activo

    def desactivar(self) -> None:
        """Marca la entidad como inactiva en el sistema."""
        self._activo = False

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Texto descriptivo de la entidad para listados y logs."""

    @abstractmethod
    def validar(self) -> bool:
        """Comprobación de integridad según reglas de negocio."""

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id})"

    def __repr__(self) -> str:
        return self.__str__()
