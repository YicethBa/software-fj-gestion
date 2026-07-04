"""
Ciclo de vida de una reserva: pendiente → confirmada → completada o cancelada.
"""

from enum import Enum

from catalogo_servicios import unidad_de_servicio
from cliente import Cliente
from excepciones import OperacionNoPermitidaError, ReservaInvalidaError
from servicios import Servicio


class EstadoReserva(Enum):
    """Estados posibles de una reserva."""

    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    COMPLETADA = "completada"


class Reserva:
    """Relación entre cliente, servicio, duración y costo calculado."""

    _contador_ids: int = 0

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        parametros_extra: dict | None = None,
    ) -> None:
        Reserva._contador_ids += 1
        self._id = Reserva._contador_ids
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._parametros_extra = parametros_extra or {}
        self._estado = EstadoReserva.PENDIENTE
        self._costo_total = 0.0
        self._impuesto_aplicado: float | None = None
        self._descuento_aplicado: float | None = None

    @property
    def id(self) -> int:
        return self._id

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    def formatear_duracion(self) -> str:
        """Duración con unidad: horas para salas/asesorías, días para equipos."""
        unidad = unidad_de_servicio(self._servicio)
        sufijo = "h" if unidad == "horas" else "d"
        valor = int(self._duracion) if self._duracion == int(self._duracion) else self._duracion
        return f"{valor} {sufijo}"

    def obtener_costo_visual(self) -> float:
        """Costo confirmado o estimación base mientras la reserva está pendiente."""
        if self._estado != EstadoReserva.PENDIENTE:
            return self._costo_total
        try:
            return self._servicio.calcular_costo(
                self._duracion,
                **self._parametros_extra,
            )
        except Exception:
            return 0.0

    def confirmar(
        self, impuesto: float | None = None, descuento: float | None = None
    ) -> float:
        try:
            if self._estado != EstadoReserva.PENDIENTE:
                raise OperacionNoPermitidaError(
                    f"No se puede confirmar una reserva en estado '{self._estado.value}'."
                )

            self._servicio.verificar_disponibilidad()

            # Cálculo del costo con parámetros específicos del tipo de servicio
            self._costo_total = self._servicio.calcular_costo(
                self._duracion,
                impuesto,
                descuento,
                **self._parametros_extra,
            )
            self._impuesto_aplicado = impuesto
            self._descuento_aplicado = descuento if descuento and descuento > 0 else None

            self._estado = EstadoReserva.CONFIRMADA
            return self._costo_total

        except OperacionNoPermitidaError:
            raise
        except Exception as error:
            raise ReservaInvalidaError(
                f"No se pudo confirmar la reserva #{self._id}."
            ) from error

    def cancelar(self, motivo: str = "") -> None:
        try:
            if self._estado == EstadoReserva.CANCELADA:
                raise OperacionNoPermitidaError("La reserva ya está cancelada.")
            if self._estado == EstadoReserva.COMPLETADA:
                raise OperacionNoPermitidaError(
                    "No se puede cancelar una reserva completada."
                )
            self._estado = EstadoReserva.CANCELADA
            self._motivo_cancelacion = motivo
        except OperacionNoPermitidaError:
            raise
        except Exception as error:
            raise ReservaInvalidaError(
                f"Error al cancelar la reserva #{self._id}."
            ) from error

    def procesar(self) -> str:
        """Finaliza una reserva confirmada y genera el mensaje de resultado."""
        resultado = ""
        try:
            if self._estado != EstadoReserva.CONFIRMADA:
                raise OperacionNoPermitidaError(
                    f"Solo se procesan reservas confirmadas. Estado: {self._estado.value}."
                )
            if self._costo_total <= 0:
                raise ReservaInvalidaError("El costo total de la reserva es inválido.")
        except (OperacionNoPermitidaError, ReservaInvalidaError) as error:
            raise ReservaInvalidaError(
                f"Fallo al procesar reserva #{self._id}: {error}"
            ) from error
        else:
            self._estado = EstadoReserva.COMPLETADA
            resultado = (
                f"Reserva #{self._id} completada | "
                f"{self._cliente.nombre_completo} | "
                f"{self._servicio.nombre} | ${self._costo_total:,.2f}"
            )
        finally:
            self._procesada = True

        return resultado

    def obtener_resumen(self) -> str:
        impuesto = (
            f" | IVA: {self._impuesto_aplicado * 100:.0f}%"
            if self._impuesto_aplicado
            else ""
        )
        descuento = (
            f" | Desc: {self._descuento_aplicado * 100:.0f}%"
            if self._descuento_aplicado
            else ""
        )
        return (
            f"Reserva #{self._id} | {self._estado.value} | "
            f"{self._cliente.nombre_completo} | {self._servicio.nombre} | "
            f"{self.formatear_duracion()} | ${self.obtener_costo_visual():,.2f}{impuesto}{descuento}"
        )

    def __str__(self) -> str:
        return self.obtener_resumen()
