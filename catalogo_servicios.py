"""
Catálogo declarativo de servicios y fábrica de instancias POO.
Separa datos de configuración de la lógica en servicios.py.
"""

from enum import Enum

from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala, Servicio


class TipoServicio(Enum):
    """Tipos de servicio soportados por el sistema."""

    SALA = "sala"
    EQUIPO = "equipo"
    ASESORIA = "asesoria"

    @classmethod
    def desde_etiqueta(cls, etiqueta: str) -> "TipoServicio":
        """Conversión entre etiqueta de interfaz y valor del enum."""
        mapa = {
            "Reserva de Sala": cls.SALA,
            "Alquiler de Equipo": cls.EQUIPO,
            "Asesoría Especializada": cls.ASESORIA,
        }
        if etiqueta not in mapa:
            raise ValueError(f"Tipo de servicio no reconocido: {etiqueta}")
        return mapa[etiqueta]

    @property
    def etiqueta(self) -> str:
        return {
            TipoServicio.SALA: "Reserva de Sala",
            TipoServicio.EQUIPO: "Alquiler de Equipo",
            TipoServicio.ASESORIA: "Asesoría Especializada",
        }[self]


ETIQUETAS_SERVICIO = [t.etiqueta for t in TipoServicio]

# Servicios precargados al iniciar la aplicación
CATALOGO_INICIAL: list[dict] = [
    {
        "tipo": TipoServicio.SALA,
        "nombre": "Auditorio Jardín Central",
        "descripcion": "Espacio amplio con iluminación natural",
        "tarifa_base": 285000,
        "capacidad": 20,
        "tiene_proyector": True,
    },
    {
        "tipo": TipoServicio.SALA,
        "nombre": "Salón Emprendimiento 101",
        "descripcion": "Ambiente colaborativo para talleres",
        "tarifa_base": 220000,
        "capacidad": 40,
        "tiene_proyector": True,
    },
    {
        "tipo": TipoServicio.EQUIPO,
        "nombre": "Portátil ROG Strix G16 (G614PM-RV010W)",
        "descripcion": "Portátil gaming de alto rendimiento",
        "tarifa_base": 380000,
        "tipo_equipo": "Portátil",
        "cantidad_disponible": 10,
    },
    {
        "tipo": TipoServicio.EQUIPO,
        "nombre": "Proyector Epson",
        "descripcion": "Proyector HD",
        "tarifa_base": 195000,
        "tipo_equipo": "Proyector",
        "cantidad_disponible": 5,
    },
    {
        "tipo": TipoServicio.ASESORIA,
        "nombre": "Asesoría Marketing Digital",
        "descripcion": "Estrategias de posicionamiento en línea",
        "tarifa_base": 480000,
        "area_especialidad": "Marketing",
        "nivel": "avanzado",
    },
    {
        "tipo": TipoServicio.ASESORIA,
        "nombre": "Asesoría Gestión de Proyectos",
        "descripcion": "Metodologías ágiles y planificación",
        "tarifa_base": 350000,
        "area_especialidad": "Administración",
        "nivel": "intermedio",
    },
]

# Metadatos para formularios de registro y reserva
CAMPOS_POR_TIPO: dict[TipoServicio, list[tuple[str, str]]] = {
    TipoServicio.SALA: [("Capacidad (personas):", "capacidad"), ("¿Tiene proyector?:", "proyector")],
    TipoServicio.EQUIPO: [("Tipo de equipo:", "tipo_equipo"), ("Cantidad disponible:", "cantidad")],
    TipoServicio.ASESORIA: [("Área de especialidad:", "area"), ("Nivel:", "nivel")],
}

PARAMETRO_RESERVA: dict[TipoServicio, str] = {
    TipoServicio.SALA: "personas",
    TipoServicio.EQUIPO: "cantidad",
}

# Unidad de la duración según tipo de servicio
UNIDAD_DURACION: dict[TipoServicio, str] = {
    TipoServicio.SALA: "horas",
    TipoServicio.EQUIPO: "días",
    TipoServicio.ASESORIA: "horas",
}

ETIQUETA_DURACION: dict[TipoServicio, str] = {
    TipoServicio.SALA: "Duración (horas):",
    TipoServicio.EQUIPO: "Duración (días):",
    TipoServicio.ASESORIA: "Duración (horas):",
}

# Unidad en la que se cobra la tarifa base
UNIDAD_TARIFA: dict[TipoServicio, str] = {
    TipoServicio.SALA: "hora",
    TipoServicio.EQUIPO: "día",
    TipoServicio.ASESORIA: "hora",
}

ETIQUETA_TARIFA_FORMULARIO: dict[TipoServicio, str] = {
    TipoServicio.SALA: "Tarifa base ($/hora):",
    TipoServicio.EQUIPO: "Tarifa base ($/día):",
    TipoServicio.ASESORIA: "Tarifa base ($/hora):",
}

ETIQUETA_PARAMETRO_RESERVA: dict[TipoServicio, str] = {
    TipoServicio.SALA: "Número de personas:",
    TipoServicio.EQUIPO: "Cantidad de equipos:",
}

LIMITE_DURACION: dict[TipoServicio, tuple[float, float]] = {
    TipoServicio.SALA: (1, 12),
    TipoServicio.EQUIPO: (1, 365),
    TipoServicio.ASESORIA: (1, 8),
}


def tipo_de_instancia(servicio: Servicio) -> TipoServicio | None:
    """Determina el tipo enum a partir de la instancia concreta."""
    if isinstance(servicio, ReservaSala):
        return TipoServicio.SALA
    if isinstance(servicio, AlquilerEquipo):
        return TipoServicio.EQUIPO
    if isinstance(servicio, AsesoriaEspecializada):
        return TipoServicio.ASESORIA
    return None


def unidad_de_servicio(servicio: Servicio) -> str:
    """Retorna 'horas' o 'días' según el tipo concreto del servicio."""
    tipo = tipo_de_instancia(servicio)
    return UNIDAD_DURACION.get(tipo, "horas") if tipo else "horas"


def construir_servicio(tipo: TipoServicio, datos: dict) -> Servicio:
    """Instanciación de la subclase correspondiente según tipo y datos."""
    nombre = datos["nombre"]
    descripcion = datos["descripcion"]
    tarifa = float(datos["tarifa_base"])

    if tipo == TipoServicio.SALA:
        return ReservaSala(
            nombre,
            descripcion,
            tarifa,
            capacidad=int(datos["capacidad"]),
            tiene_proyector=datos.get("tiene_proyector", datos.get("proyector", "No") == "Sí"),
        )

    if tipo == TipoServicio.EQUIPO:
        return AlquilerEquipo(
            nombre,
            descripcion,
            tarifa,
            tipo_equipo=str(datos["tipo_equipo"]),
            cantidad_disponible=int(datos["cantidad_disponible"]),
        )

    return AsesoriaEspecializada(
        nombre,
        descripcion,
        tarifa,
        area_especialidad=str(datos["area_especialidad"]),
        nivel=str(datos.get("nivel", "intermedio")),
    )
