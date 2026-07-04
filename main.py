"""
Punto de entrada: interfaz gráfica o simulación por consola (--demo).
"""

import sys

from catalogo_servicios import TipoServicio, construir_servicio
from interfaz import iniciar_interfaz
from logger_util import LoggerSistema
from servicios import AlquilerEquipo
from sistema_gestion import SistemaGestion


def _titulo(texto: str) -> None:
    print(f"\n{'=' * 60}\n  {texto}\n{'=' * 60}")


def ejecutar_simulacion() -> None:
    """13 escenarios de prueba: casos válidos y rechazos esperados."""
    sistema = SistemaGestion()
    sistema.inicializar_servicios_predeterminados()

    # Registro de clientes
    _titulo("Operación 1: Cliente válido")
    c1 = sistema.registrar_cliente(
        "María", "González", "1023456789", "maria@email.com", "3001234567"
    )
    if c1:
        print(f"  OK: {c1.obtener_resumen()}")

    _titulo("Operación 2: Segundo cliente válido")
    c2 = sistema.registrar_cliente(
        "Carlos", "Rodríguez", "1034567890", "carlos@email.com", "3109876543"
    )
    if c2:
        print(f"  OK: {c2.obtener_resumen()}")

    _titulo("Operación 3: Email inválido")
    print("  Rechazado:", sistema.registrar_cliente(
        "Pedro", "López", "1045678901", "email-invalido", "3201112233"
    ) is None)

    _titulo("Operación 4: Documento duplicado")
    print("  Rechazado:", sistema.registrar_cliente(
        "Ana", "Martínez", "1023456789", "ana@email.com", "3154445566"
    ) is None)

    # Registro de servicios
    _titulo("Operación 5: Servicio nuevo desde catálogo")
    sala = construir_servicio(
        TipoServicio.SALA,
        {
            "nombre": "Sala Innovación",
            "descripcion": "Espacio creativo",
            "tarifa_base": 265000,
            "capacidad": 15,
            "tiene_proyector": True,
        },
    )
    if sistema.registrar_servicio(sala):
        print(f"  OK: {sala.describir_servicio()}")

    _titulo("Operación 6: Servicio duplicado")
    dup = construir_servicio(
        TipoServicio.SALA,
        {
            "nombre": "Auditorio Jardín Central",
            "descripcion": "Duplicado",
            "tarifa_base": 285000,
            "capacidad": 10,
            "tiene_proyector": False,
        },
    )
    print("  Rechazado:", sistema.registrar_servicio(dup) is None)

    # Reservas con distintos escenarios de costo
    _titulo("Operación 7: Reserva con impuesto")
    r1 = sistema.crear_reserva("1023456789", "Auditorio Jardín Central", 3, {"personas": 15})
    if r1:
        costo = sistema.confirmar_reserva(r1.id, impuesto=19 / 100)
        print(f"  OK: ${costo:,.2f}" if costo else "  Error")

    _titulo("Operación 8: Reserva con impuesto y descuento")
    r2 = sistema.crear_reserva("1034567890", "Asesoría Marketing Digital", 2)
    if r2:
        costo = sistema.confirmar_reserva(r2.id, impuesto=19 / 100, descuento=10 / 100)
        print(f"  OK: ${costo:,.2f}" if costo else "  Error")

    # Casos de rechazo en reservas
    _titulo("Operación 9: Servicio no disponible")
    for s in sistema.servicios:
        if s.nombre == "Proyector Epson":
            s.marcar_no_disponible()
            break
    rf = sistema.crear_reserva("1023456789", "Proyector Epson", 5, {"cantidad": 2})
    if rf:
        print("  Rechazado:", sistema.confirmar_reserva(rf.id) is None)

    _titulo("Operación 10: Capacidad excedida")
    rc = sistema.crear_reserva("1034567890", "Salón Emprendimiento 101", 4, {"personas": 50})
    if rc:
        print("  Rechazado:", sistema.confirmar_reserva(rc.id) is None)

    _titulo("Operación 11: Cliente inexistente")
    print("  Rechazado:", sistema.crear_reserva("9999999999", "Sala Innovación", 2, {"personas": 10}) is None)

    # Ciclo completo: procesar, cancelar y desactivar
    _titulo("Operación 12: Procesar, cancelar y desactivar cliente")
    if r1:
        print(f"  {sistema.procesar_reserva(r1.id)}")
    ra = sistema.crear_reserva("1023456789", "Portátil ROG Strix G16 (G614PM-RV010W)", 7, {"cantidad": 3})
    if ra and sistema.confirmar_reserva(ra.id):
        sistema.cancelar_reserva(ra.id, "Cliente cambió de planes")
        print(f"  Reserva #{ra.id} cancelada.")
    sistema.registrar_cliente("Luis", "Pérez", "1045678901", "luis@email.com", "3000000000")
    sistema.desactivar_cliente("1045678901")

    _titulo("Operación 13: Tarifa negativa")
    invalido = AlquilerEquipo("Servidor X", "Tarifa inválida", -50000, "Servidor", 2)
    print("  Rechazado:", sistema.registrar_servicio(invalido) is None)

    # Resumen final de la simulación
    _titulo("Resumen del sistema")
    sistema.listar_clientes()
    sistema.listar_servicios()
    sistema.listar_reservas()
    print("\n--- ESTADÍSTICAS ---")
    for clave, valor in sistema.obtener_estadisticas().items():
        print(f"  {clave}: ${valor:,.2f}" if clave == "ingresos_totales" else f"  {clave}: {valor}")

    print("\nSimulación finalizada. Detalle en logs/sistema.log")


def main() -> None:
    logger = LoggerSistema()
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--demo":
            ejecutar_simulacion()
        else:
            iniciar_interfaz()
    except Exception as error:
        logger.registrar_error("Error crítico no controlado en main", error)
        print(f"\nError crítico: {error}")
        print("Detalle registrado en logs/sistema.log")
        sys.exit(1)


if __name__ == "__main__":
    main()
