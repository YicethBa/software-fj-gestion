"""
Jerarquía de servicios: clase abstracta y tres implementaciones concretas.
Incluye validación de parámetros y cálculo de costos con impuesto y descuento.
"""

from abc import abstractmethod
from typing import overload

from entidad import Entidad
from excepciones import (
    CalculoInconsistenteError,
    DatosInvalidosError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
)


class Servicio(Entidad):
    """Contrato común para reservas de sala, alquiler de equipo y asesorías."""

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        tarifa_base: float,
        disponible: bool = True,
    ) -> None:
        super().__init__()
        self._nombre = nombre
        self._descripcion = descripcion
        self._tarifa_base = tarifa_base
        self._disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    def marcar_no_disponible(self) -> None:
        self._disponible = False
        self.desactivar()

    def marcar_disponible(self) -> None:
        self._disponible = True

    def verificar_disponibilidad(self) -> None:
        if not self._disponible or not self.activo:
            raise ServicioNoDisponibleError(
                f"El servicio '{self._nombre}' no está disponible."
            )

    @abstractmethod
    def describir_servicio(self) -> str:
        """Descripción legible según atributos del tipo concreto."""

    @abstractmethod
    def validar_parametros(self, duracion: float, **kwargs) -> None:
        """Reglas de duración y parámetros adicionales por tipo de servicio."""

    @overload
    def calcular_costo(self, duracion: float, /, **kwargs) -> float: ...

    @overload
    def calcular_costo(self, duracion: float, impuesto: float, /, **kwargs) -> float: ...

    @overload
    def calcular_costo(
        self, duracion: float, impuesto: float, descuento: float, /, **kwargs
    ) -> float: ...

    def calcular_costo(
        self,
        duracion: float,
        impuesto: float | None = None,
        descuento: float | None = None,
        **parametros_reserva,
    ) -> float:
        try:
            if duracion <= 0:
                raise DatosInvalidosError("La duración debe ser mayor a cero.")

            self.validar_parametros(duracion, **parametros_reserva)
            costo = self._calcular_costo_base(duracion, **parametros_reserva)

            # Ajustes opcionales sobre el costo base
            if impuesto is not None:
                if not 0 <= impuesto <= 1:
                    raise CalculoInconsistenteError("El impuesto debe estar entre 0 y 1 (0% a 100%).")
                costo *= 1 + impuesto

            if descuento is not None:
                if not 0 <= descuento <= 1:
                    raise CalculoInconsistenteError("El descuento debe estar entre 0 y 1 (0% a 100%).")
                costo *= 1 - descuento

            if costo < 0:
                raise CalculoInconsistenteError("El costo calculado no puede ser negativo.")

            return round(costo, 2)

        except (DatosInvalidosError, CalculoInconsistenteError):
            raise
        except Exception as error:
            raise CalculoInconsistenteError(
                f"Error al calcular costo del servicio '{self._nombre}'."
            ) from error

    @abstractmethod
    def _calcular_costo_base(self, duracion: float, **kwargs) -> float:
        """Tarifa antes de impuestos y descuentos; definida en cada subclase."""

    def validar(self) -> bool:
        return bool(self._nombre and self._descripcion and self._tarifa_base > 0)

    def obtener_resumen(self) -> str:
        estado = "Disponible" if self._disponible and self.activo else "No disponible"
        return (
            f"Servicio #{self._id}: {self._nombre} | "
            f"Tarifa: {self.formatear_tarifa()} | {estado}"
        )

    def obtener_cupo_permitido(self) -> str:
        """Límite de uso del servicio para mostrar en listados."""
        return "—"

    def unidad_tarifa(self) -> str:
        """Unidad de cobro de la tarifa base (hora o día)."""
        return "hora"

    def formatear_tarifa(self) -> str:
        """Tarifa base con símbolo de moneda y unidad de cobro."""
        return f"${self._tarifa_base:,.0f}/{self.unidad_tarifa()}"


class ReservaSala(Servicio):
    """Salas de reuniones o capacitación con capacidad y equipamiento."""

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        tarifa_base: float,
        capacidad: int,
        tiene_proyector: bool = False,
        disponible: bool = True,
    ) -> None:
        super().__init__(nombre, descripcion, tarifa_base, disponible)
        self._capacidad = capacidad
        self._tiene_proyector = tiene_proyector

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def describir_servicio(self) -> str:
        proyector = "Sí" if self._tiene_proyector else "No"
        return (
            f"Sala: {self._nombre} | {self.formatear_tarifa()} | "
            f"Capacidad: {self._capacidad} | Proyector: {proyector} | {self._descripcion}"
        )

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        if duracion > 12:
            raise DatosInvalidosError("La reserva de sala no puede exceder 12 horas.")
        personas = kwargs.get("personas")
        if personas is None:
            raise ParametroFaltanteError(
                f"Debe indicar el número de personas (máximo {self._capacidad})."
            )
        if personas <= 0:
            raise DatosInvalidosError("El número de personas debe ser mayor a cero.")
        if personas > self._capacidad:
            raise DatosInvalidosError(
                f"Capacidad máxima: {self._capacidad} personas. Solicitadas: {personas}."
            )

    def obtener_cupo_permitido(self) -> str:
        return f"{self._capacidad} personas"

    def _calcular_costo_base(self, duracion: float, **kwargs) -> float:
        costo = self._tarifa_base * duracion
        if self._tiene_proyector:
            costo += 55000 * duracion
        return costo


class AlquilerEquipo(Servicio):
    """Equipos tecnológicos con stock disponible para alquiler."""

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        tarifa_base: float,
        tipo_equipo: str,
        cantidad_disponible: int,
        disponible: bool = True,
    ) -> None:
        super().__init__(nombre, descripcion, tarifa_base, disponible)
        self._tipo_equipo = tipo_equipo
        self._cantidad_disponible = cantidad_disponible

    @property
    def cantidad_disponible(self) -> int:
        return self._cantidad_disponible

    def describir_servicio(self) -> str:
        return (
            f"Equipo: {self._nombre} | {self.formatear_tarifa()} | "
            f"Tipo: {self._tipo_equipo} | Stock: {self._cantidad_disponible} | {self._descripcion}"
        )

    def unidad_tarifa(self) -> str:
        return "día"

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        if duracion > 365:
            raise DatosInvalidosError("El alquiler no puede exceder 365 días.")
        cantidad = kwargs.get("cantidad")
        if cantidad is None:
            raise ParametroFaltanteError(
                f"Debe indicar la cantidad de equipos (máximo {self._cantidad_disponible})."
            )
        if cantidad <= 0:
            raise ParametroFaltanteError("La cantidad debe ser mayor a cero.")
        if cantidad > self._cantidad_disponible:
            raise ServicioNoDisponibleError(
                f"Solo hay {self._cantidad_disponible} unidades de '{self._nombre}'."
            )

    def obtener_cupo_permitido(self) -> str:
        return f"{self._cantidad_disponible} unidades"

    def _calcular_costo_base(self, duracion: float, **kwargs) -> float:
        cantidad = kwargs.get("cantidad", 1)
        return self._tarifa_base * duracion * cantidad


class AsesoriaEspecializada(Servicio):
    """Asesorías técnicas con área de especialidad y nivel de complejidad."""

    NIVELES = ("básico", "intermedio", "avanzado")

    def __init__(
        self,
        nombre: str,
        descripcion: str,
        tarifa_base: float,
        area_especialidad: str,
        nivel: str,
        disponible: bool = True,
    ) -> None:
        super().__init__(nombre, descripcion, tarifa_base, disponible)
        self._area_especialidad = area_especialidad
        self._nivel = nivel

    def describir_servicio(self) -> str:
        return (
            f"Asesoría: {self._nombre} | {self.formatear_tarifa()} | "
            f"Área: {self._area_especialidad} | Nivel: {self._nivel} | {self._descripcion}"
        )

    def validar_parametros(self, duracion: float, **kwargs) -> None:
        if duracion < 1:
            raise DatosInvalidosError("La asesoría requiere al menos 1 hora.")
        if duracion > 8:
            raise DatosInvalidosError("La asesoría no puede exceder 8 horas.")
        if self._nivel.lower() not in self.NIVELES:
            raise DatosInvalidosError(f"Nivel inválido: {self._nivel}")

    def obtener_cupo_permitido(self) -> str:
        return "1 cliente · máx. 8 h"

    def _calcular_costo_base(self, duracion: float, **kwargs) -> float:
        # Tarifa por hora; el nivel ya está reflejado en la tarifa del servicio
        return self._tarifa_base * duracion
