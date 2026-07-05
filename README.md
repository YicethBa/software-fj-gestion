# Software FJ — Sistema de Gestión

Sistema orientado a objetos para la empresa **Software FJ**. Gestiona clientes, servicios y reservas en memoria, con interfaz Tkinter, excepciones personalizadas y registro en archivo de log.

## Requisitos

- Python 3.10+
- Tkinter

## Ejecución

```bash
python main.py
python main.py --demo
```

## Estructura

| Archivo | Función |
|---------|---------|
| `entidad.py` | Clase abstracta base |
| `excepciones.py` | Jerarquía de excepciones |
| `logger_util.py` | Registro en `logs/sistema.log` |
| `cliente.py` | Modelo de cliente |
| `servicios.py` | Clases de servicio (POO) |
| `catalogo_servicios.py` | Catálogo declarativo y fábrica |
| `reserva.py` | Ciclo de vida de reservas |
| `sistema_gestion.py` | Lógica de negocio |
| `interfaz.py` | GUI Tkinter |
| `main.py` | Punto de entrada |

## Requerimientos del anexo cubiertos

| ID | Descripción |
|----|-------------|
| RF-01 | Registro de clientes con validación |
| RF-02 | Consulta de clientes |
| RF-03 | Servicios especializados (sala, equipo, asesoría) |
| RF-04 | Consulta de servicios y disponibilidad |
| RF-05 | Creación de reservas |
| RF-06 | Confirmación con impuesto y descuento |
| RF-07 | Cancelación de reservas |
| RF-08 | Procesamiento de reservas confirmadas |
| RF-09 | Logs de eventos y errores |
| RF-10 | Estadísticas del sistema |
| RF-11 | Interfaz Tkinter completa |


Desarrollo individual organizado en **5 módulos** equivalentes a integrantes:

| Módulo | Rama | Archivos |
|--------|------|----------|
| 1 | `feature/base-y-excepciones` | `entidad.py`, `excepciones.py`, `logger_util.py` |
| 2 | `feature/modulo-clientes` | `cliente.py` |
| 3 | `feature/modulo-servicios` | `servicios.py`, `catalogo_servicios.py` |
| 4 | `feature/modulo-reservas` | `reserva.py`, `sistema_gestion.py` |
| 5 | `feature/interfaz-y-documentacion` | `interfaz.py`, `main.py`, `README.md` |

Cada módulo: issue asignado → rama → commits descriptivos → pull request → merge a `main`.

Ver [GITHUB_GUIA.md](GITHUB_GUIA.md) para el proceso completo.

## Servicios: clases + catálogo

Las clases `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada` son obligatorias por POO del anexo. El archivo `catalogo_servicios.py` separa los **datos del catálogo** (listas de diccionarios) de la **lógica** (fábrica `construir_servicio`), evitando repetir bloques if/elif en la interfaz.
