"""
Registro persistente de eventos y errores en logs/sistema.log.
"""

import os
from datetime import datetime


class LoggerSistema:
    """Persistencia de entradas con marca temporal y nivel."""

    def __init__(self, ruta_log: str = "logs/sistema.log") -> None:
        self._ruta_log = ruta_log
        os.makedirs(os.path.dirname(self._ruta_log), exist_ok=True)

    def _escribir(self, nivel: str, mensaje: str) -> None:
        """Formato de línea: [fecha] [nivel] mensaje."""
        marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{marca}] [{nivel}] {mensaje}\n"
        try:
            with open(self._ruta_log, "a", encoding="utf-8") as archivo:
                archivo.write(linea)
        except OSError as error:
            print(f"No se pudo escribir en el log: {error}")

    def registrar_evento(self, mensaje: str) -> None:
        """Operaciones exitosas y hitos del sistema."""
        self._escribir("EVENTO", mensaje)

    def registrar_error(self, mensaje: str, excepcion: Exception | None = None) -> None:
        """Fallos de validación u operación, con tipo de excepción opcional."""
        detalle = mensaje
        if excepcion is not None:
            detalle += f" | {type(excepcion).__name__}: {excepcion}"
        self._escribir("ERROR", detalle)

    def limpiar_log(self) -> None:
        """Reinicio del archivo al iniciar una nueva sesión."""
        try:
            with open(self._ruta_log, "w", encoding="utf-8") as archivo:
                archivo.write("")
        except OSError as error:
            print(f"No se pudo limpiar el log: {error}")
