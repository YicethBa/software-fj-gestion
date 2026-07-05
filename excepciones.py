"""
Jerarquía de excepciones
Permite distinguir errores de validación, operación y cálculo.
"""


class SoftwareFJError(Exception):
    """Excepción raíz del dominio."""

    def __init__(self, mensaje: str, causa: Exception | None = None) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.causa = causa


# --- Errores generales de validación y operación ---

class DatosInvalidosError(SoftwareFJError):
    """Datos que no cumplen las reglas del dominio."""


class ParametroFaltanteError(SoftwareFJError):
    """Parámetro obligatorio ausente."""


class OperacionNoPermitidaError(SoftwareFJError):
    """Transición o acción no permitida en el estado actual."""


# --- Errores específicos por módulo ---

class ClienteInvalidoError(DatosInvalidosError):
    """Datos personales del cliente inválidos."""


class ServicioNoDisponibleError(SoftwareFJError):
    """Servicio inactivo o sin disponibilidad."""


class ReservaInvalidaError(SoftwareFJError):
    """Reserva que no puede crearse, confirmarse o procesarse."""


class CalculoInconsistenteError(SoftwareFJError):
    """Resultado de costo fuera de rango o incoherente."""
