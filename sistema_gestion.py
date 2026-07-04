"""
Capa de negocio: orquestación de clientes, servicios y reservas en memoria.
Centraliza validaciones, logging y respuestas a la interfaz.
"""

from catalogo_servicios import CATALOGO_INICIAL, construir_servicio
from cliente import Cliente
from excepciones import (
    ClienteInvalidoError,
    DatosInvalidosError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ReservaInvalidaError,
    SoftwareFJError,
)
from logger_util import LoggerSistema
from reserva import Reserva
from servicios import Servicio


class SistemaGestion:
    """Repositorio en memoria y punto de acceso a operaciones del dominio."""

    def __init__(self) -> None:
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []
        self._ultimo_mensaje = ""
        self._logger = LoggerSistema()
        self._logger.limpiar_log()
        self._logger.registrar_evento("Sistema Software FJ iniciado.")

    @property
    def ultimo_mensaje(self) -> str:
        return self._ultimo_mensaje

    @property
    def clientes(self) -> list[Cliente]:
        return self._clientes.copy()

    @property
    def servicios(self) -> list[Servicio]:
        return self._servicios.copy()

    @property
    def reservas(self) -> list[Reserva]:
        return self._reservas.copy()

    def _resultado(self, exito: bool, mensaje: str, valor=None):
        """Actualiza el último mensaje y retorna el valor de la operación."""
        self._ultimo_mensaje = mensaje
        if not exito:
            print(f"  [ERROR] {mensaje}")
        return valor

    def registrar_error_ui(self, mensaje: str, excepcion: Exception | None = None) -> None:
        """Persistencia de errores originados en la interfaz gráfica."""
        self._logger.registrar_error(f"[Interfaz] {mensaje}", excepcion)
        self._ultimo_mensaje = mensaje

    # --- Gestión de clientes ---

    def registrar_cliente(
        self,
        nombre: str,
        apellido: str,
        documento: str,
        email: str,
        telefono: str,
    ) -> Cliente | None:
        try:
            if not all([nombre, apellido, documento, email, telefono]):
                raise ParametroFaltanteError("Todos los campos del cliente son obligatorios.")

            if any(c.documento == documento for c in self._clientes):
                raise ClienteInvalidoError(f"Ya existe un cliente con documento {documento}.")

            cliente = Cliente(nombre, apellido, documento, email, telefono)
            self._clientes.append(cliente)
            self._logger.registrar_evento(cliente.obtener_resumen())
            return self._resultado(True, f"Cliente registrado: {cliente.nombre_completo}", cliente)

        except SoftwareFJError as error:
            self._logger.registrar_error("Error al registrar cliente", error)
            return self._resultado(False, str(error), None)

    def desactivar_cliente(self, documento: str) -> bool:
        try:
            cliente = self._buscar_cliente(documento)
            if cliente is None:
                raise ClienteInvalidoError(f"No existe cliente con documento {documento}.")
            if not cliente.activo:
                raise OperacionNoPermitidaError("El cliente ya está inactivo.")

            cliente.desactivar()
            self._logger.registrar_evento(f"Cliente desactivado: {cliente.nombre_completo}")
            return self._resultado(True, f"Cliente {cliente.nombre_completo} desactivado.", True)

        except SoftwareFJError as error:
            self._logger.registrar_error("Error al desactivar cliente", error)
            return self._resultado(False, str(error), False)

    # --- Gestión de servicios ---

    def registrar_servicio(self, servicio: Servicio, *, registrar_log: bool = True) -> Servicio | None:
        try:
            if not servicio.validar():
                raise DatosInvalidosError(f"El servicio '{servicio.nombre}' no es válido.")

            if any(s.nombre.lower() == servicio.nombre.lower() for s in self._servicios):
                raise DatosInvalidosError(f"Ya existe el servicio '{servicio.nombre}'.")

            self._servicios.append(servicio)
            if registrar_log:
                self._logger.registrar_evento(servicio.obtener_resumen())
            return self._resultado(True, f"Servicio '{servicio.nombre}' registrado.", servicio)

        except SoftwareFJError as error:
            self._logger.registrar_error(f"Error al registrar '{servicio.nombre}'", error)
            return self._resultado(False, str(error), None)

    def inicializar_servicios_predeterminados(self) -> None:
        """Carga del catálogo inicial sin generar un log por cada servicio."""
        for registro in CATALOGO_INICIAL:
            servicio = construir_servicio(registro["tipo"], registro)
            self.registrar_servicio(servicio, registrar_log=False)
        self._logger.registrar_evento(
            f"Catálogo inicial cargado: {len(CATALOGO_INICIAL)} servicios."
        )

    # --- Gestión de reservas ---

    def crear_reserva(
        self,
        documento_cliente: str,
        nombre_servicio: str,
        duracion: float,
        parametros_extra: dict | None = None,
    ) -> Reserva | None:
        try:
            cliente = self._buscar_cliente(documento_cliente)
            if cliente is None:
                raise ReservaInvalidaError(f"No existe cliente con documento {documento_cliente}.")
            if not cliente.activo:
                raise ReservaInvalidaError(f"El cliente con documento {documento_cliente} está inactivo.")

            servicio = self._buscar_servicio(nombre_servicio)
            if servicio is None:
                raise ReservaInvalidaError(f"No existe servicio '{nombre_servicio}'.")

            if duracion <= 0:
                raise DatosInvalidosError("La duración debe ser mayor a cero.")

            params = parametros_extra or {}
            servicio.validar_parametros(duracion, **params)

            reserva = Reserva(cliente, servicio, duracion, parametros_extra)
            self._reservas.append(reserva)
            self._logger.registrar_evento(f"Reserva #{reserva.id} creada.")
            return self._resultado(
                True,
                f"Reserva #{reserva.id} creada (pendiente). "
                f"Selecciónela y pulse Confirmar para aplicar impuesto y costo final.",
                reserva,
            )

        except SoftwareFJError as error:
            self._logger.registrar_error("Error al crear reserva", error)
            return self._resultado(False, str(error), None)

    def confirmar_reserva(
        self,
        id_reserva: int,
        impuesto: float | None = None,
        descuento: float | None = None,
    ) -> float | None:
        try:
            reserva = self._buscar_reserva(id_reserva)
            if reserva is None:
                raise ReservaInvalidaError(f"No existe reserva #{id_reserva}.")

            costo = reserva.confirmar(impuesto, descuento)
            mensaje = f"Reserva #{id_reserva} confirmada. Costo: ${costo:,.2f}"
            self._logger.registrar_evento(mensaje)
            return self._resultado(True, mensaje, costo)

        except SoftwareFJError as error:
            self._logger.registrar_error(f"Error al confirmar reserva #{id_reserva}", error)
            return self._resultado(False, str(error), None)

    def cancelar_reserva(self, id_reserva: int, motivo: str = "") -> bool:
        try:
            reserva = self._buscar_reserva(id_reserva)
            if reserva is None:
                raise ReservaInvalidaError(f"No existe reserva #{id_reserva}.")

            reserva.cancelar(motivo)
            detalle = motivo or "Sin motivo"
            self._logger.registrar_evento(f"Reserva #{id_reserva} cancelada. Motivo: {detalle}")
            return self._resultado(True, f"Reserva #{id_reserva} cancelada.", True)

        except SoftwareFJError as error:
            self._logger.registrar_error(f"Error al cancelar reserva #{id_reserva}", error)
            return self._resultado(False, str(error), False)

    def procesar_reserva(self, id_reserva: int) -> str | None:
        try:
            reserva = self._buscar_reserva(id_reserva)
            if reserva is None:
                raise ReservaInvalidaError(f"No existe reserva #{id_reserva}.")

            resultado = reserva.procesar()
            self._logger.registrar_evento(resultado)
            return self._resultado(True, resultado, resultado)

        except SoftwareFJError as error:
            self._logger.registrar_error(f"Error al procesar reserva #{id_reserva}", error)
            return self._resultado(False, str(error), None)

    # --- Consultas y reportes ---

    def listar_clientes(self) -> None:
        print("\n--- CLIENTES REGISTRADOS ---")
        if not self._clientes:
            print("  (vacío)")
            return
        for cliente in self._clientes:
            estado = "activo" if cliente.activo else "inactivo"
            print(f"  [{estado}] {cliente.obtener_resumen()}")

    def listar_servicios(self) -> None:
        print("\n--- SERVICIOS DISPONIBLES ---")
        if not self._servicios:
            print("  (vacío)")
            return
        for servicio in self._servicios:
            print(f"  {servicio.describir_servicio()}")

    def listar_reservas(self) -> None:
        print("\n--- RESERVAS ---")
        if not self._reservas:
            print("  (vacío)")
            return
        for reserva in self._reservas:
            print(f"  {reserva.obtener_resumen()}")

    def obtener_estadisticas(self) -> dict:
        return {
            "total_clientes": len(self._clientes),
            "total_servicios": len(self._servicios),
            "total_reservas": len(self._reservas),
            "confirmadas": sum(1 for r in self._reservas if r.estado.value == "confirmada"),
            "completadas": sum(1 for r in self._reservas if r.estado.value == "completada"),
            "canceladas": sum(1 for r in self._reservas if r.estado.value == "cancelada"),
            "ingresos_totales": sum(r.costo_total for r in self._reservas if r.costo_total > 0),
        }

    def buscar_servicio_por_nombre(self, nombre: str) -> Servicio | None:
        return self._buscar_servicio(nombre)

    # --- Búsquedas internas ---

    def _buscar_cliente(self, documento: str) -> Cliente | None:
        return next((c for c in self._clientes if c.documento == documento), None)

    def _buscar_servicio(self, nombre: str) -> Servicio | None:
        return next((s for s in self._servicios if s.nombre.lower() == nombre.lower()), None)

    def _buscar_reserva(self, id_reserva: int) -> Reserva | None:
        return next((r for r in self._reservas if r.id == id_reserva), None)
