"""
Modelo Cliente con encapsulamiento mediante property.
Validaciones aplicadas en cada asignación de dato personal.
"""

import re

from entidad import Entidad
from excepciones import ClienteInvalidoError, ParametroFaltanteError

# Documento de identidad numérica, entre 6 y 10 dígitos
DOCUMENTO_MIN_DIGITOS = 6
DOCUMENTO_MAX_DIGITOS = 10


class Cliente(Entidad):
    """Datos personales de un cliente."""

    def __init__(
        self,
        nombre: str,
        apellido: str,
        documento: str,
        email: str,
        telefono: str,
    ) -> None:
        super().__init__()
        self._nombre = ""
        self._apellido = ""
        self._documento = ""
        self._email = ""
        self._telefono = ""

        # Los setters centralizan formato y reglas de validación
        self.nombre = nombre
        self.apellido = apellido
        self.documento = documento
        self.email = email
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor or len(valor.strip()) < 2:
            raise ClienteInvalidoError("El nombre debe tener al menos 2 caracteres.")
        self._nombre = valor.strip().title()

    @property
    def apellido(self) -> str:
        return self._apellido

    @apellido.setter
    def apellido(self, valor: str) -> None:
        if not valor or len(valor.strip()) < 2:
            raise ClienteInvalidoError("El apellido debe tener al menos 2 caracteres.")
        self._apellido = valor.strip().title()

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        documento_limpio = valor.strip()
        patron = rf"^\d{{{DOCUMENTO_MIN_DIGITOS},{DOCUMENTO_MAX_DIGITOS}}}$"
        if not documento_limpio or not re.match(patron, documento_limpio):
            raise ClienteInvalidoError(
                f"El documento debe tener entre {DOCUMENTO_MIN_DIGITOS} y "
                f"{DOCUMENTO_MAX_DIGITOS} dígitos numéricos (cédula de ciudadanía)."
            )
        self._documento = documento_limpio

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ParametroFaltanteError("El email es obligatorio.")
        email_limpio = valor.strip().lower()
        patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron, email_limpio):
            raise ClienteInvalidoError(f"Formato de email inválido: {valor}")
        self._email = email_limpio

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not valor or not valor.strip():
            raise ParametroFaltanteError("El teléfono es obligatorio.")
        telefono_limpio = re.sub(r"[\s\-()]", "", valor.strip())
        if not re.match(r"^\d{7,15}$", telefono_limpio):
            raise ClienteInvalidoError(
                "El teléfono debe contener entre 7 y 15 dígitos numéricos."
            )
        self._telefono = telefono_limpio

    @property
    def nombre_completo(self) -> str:
        return f"{self._nombre} {self._apellido}"

    def validar(self) -> bool:
        return all([self._nombre, self._apellido, self._documento, self._email, self._telefono])

    def obtener_resumen(self) -> str:
        return (
            f"Cliente #{self._id}: {self.nombre_completo} | "
            f"Doc: {self._documento} | Email: {self._email} | Tel: {self._telefono}"
        )

    def __str__(self) -> str:
        return f"Cliente(id={self._id}, doc={self._documento})"
