"""
Interfaz gráfica Tkinter: pestañas de clientes, servicios, reservas y estadísticas.
"""

import os
import tkinter as tk
from tkinter import messagebox, ttk

from catalogo_servicios import (
    CAMPOS_POR_TIPO,
    ETIQUETAS_SERVICIO,
    ETIQUETA_DURACION,
    ETIQUETA_PARAMETRO_RESERVA,
    ETIQUETA_TARIFA_FORMULARIO,
    LIMITE_DURACION,
    PARAMETRO_RESERVA,
    TipoServicio,
    construir_servicio,
    tipo_de_instancia,
)
from sistema_gestion import SistemaGestion


class InterfazSoftwareFJ:
    """Ventana principal de la aplicación."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Software FJ - Sistema de Gestión")
        self.root.geometry("960x640")
        self.root.minsize(800, 550)

        self.sistema = SistemaGestion()
        self.sistema.inicializar_servicios_predeterminados()

        self._configurar_estilos()
        self._crear_interfaz()
        self._actualizar_todas_las_listas()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TNotebook.Tab", padding=[12, 4], font=("Segoe UI", 10))
        estilo.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        estilo.configure("Status.TLabel", font=("Segoe UI", 9))

    def _crear_interfaz(self) -> None:
        marco_header = ttk.Frame(self.root, padding=10)
        marco_header.pack(fill=tk.X)
        ttk.Label(
            marco_header,
            text="Software FJ - Gestión de Clientes, Servicios y Reservas",
            style="Header.TLabel",
        ).pack(side=tk.LEFT)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        self._crear_pestana_clientes()
        self._crear_pestana_servicios()
        self._crear_pestana_reservas()
        self._crear_pestana_estadisticas()

        self.lbl_estado = ttk.Label(
            self.root, text="Sistema listo.", style="Status.TLabel", relief=tk.SUNKEN
        )
        self.lbl_estado.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)

    def _mostrar_estado(self, mensaje: str, es_error: bool = False) -> None:
        self.lbl_estado.config(text=mensaje)
        if es_error:
            messagebox.showerror("Error", mensaje)
        else:
            messagebox.showinfo("Operación exitosa", mensaje)

    def _error_validacion(self, mensaje: str, error: Exception | None = None) -> None:
        """Registro en log y notificación visual de errores de validación."""
        self.sistema.registrar_error_ui(mensaje, error)
        self._mostrar_estado(mensaje, es_error=True)

    def _crear_pestana_clientes(self) -> None:
        """Formulario de registro y tabla de clientes."""
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Clientes")

        marco_form = ttk.LabelFrame(frame, text="Registrar nuevo cliente", padding=10)
        marco_form.pack(fill=tk.X, pady=(0, 10))

        campos = [
            ("Nombre:", "nombre"),
            ("Apellido:", "apellido"),
            ("Documento:", "documento"),
            ("Email:", "email"),
            ("Teléfono:", "telefono"),
        ]
        self.vars_cliente = {}
        for i, (etiqueta, clave) in enumerate(campos):
            ttk.Label(marco_form, text=etiqueta).grid(row=i, column=0, sticky=tk.W, pady=3)
            var = tk.StringVar()
            self.vars_cliente[clave] = var
            ttk.Entry(marco_form, textvariable=var, width=40).grid(row=i, column=1, padx=5, pady=3)

        ttk.Button(marco_form, text="Registrar Cliente", command=self._registrar_cliente).grid(
            row=len(campos), column=0, columnspan=2, pady=10
        )

        marco_lista = ttk.LabelFrame(frame, text="Clientes registrados", padding=10)
        marco_lista.pack(fill=tk.BOTH, expand=True)

        columnas = ("id", "nombre", "documento", "email", "telefono")
        self.tree_clientes = ttk.Treeview(marco_lista, columns=columnas, show="headings", height=10)
        for col, texto, ancho in [
            ("id", "ID", 50),
            ("nombre", "Nombre completo", 180),
            ("documento", "Documento", 120),
            ("email", "Email", 180),
            ("telefono", "Teléfono", 120),
        ]:
            self.tree_clientes.heading(col, text=texto)
            self.tree_clientes.column(col, width=ancho)

        scroll = ttk.Scrollbar(marco_lista, orient=tk.VERTICAL, command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscrollcommand=scroll.set)
        self.tree_clientes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _registrar_cliente(self) -> None:
        resultado = self.sistema.registrar_cliente(
            self.vars_cliente["nombre"].get(),
            self.vars_cliente["apellido"].get(),
            self.vars_cliente["documento"].get(),
            self.vars_cliente["email"].get(),
            self.vars_cliente["telefono"].get(),
        )
        es_exito = resultado is not None
        self._mostrar_estado(self.sistema.ultimo_mensaje, es_error=not es_exito)
        if es_exito:
            for var in self.vars_cliente.values():
                var.set("")
            self._actualizar_lista_clientes()

    def _actualizar_lista_clientes(self) -> None:
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        for cliente in self.sistema.clientes:
            self.tree_clientes.insert(
                "",
                tk.END,
                values=(
                    cliente.id,
                    cliente.nombre_completo,
                    cliente.documento,
                    cliente.email,
                    cliente.telefono,
                ),
            )

    def _crear_pestana_servicios(self) -> None:
        """Formulario dinámico según tipo de servicio y listado."""
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Servicios")

        marco_form = ttk.LabelFrame(frame, text="Registrar nuevo servicio", padding=10)
        marco_form.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(marco_form, text="Tipo de servicio:").grid(row=0, column=0, sticky=tk.W)
        self.var_tipo_servicio = tk.StringVar(value="Reserva de Sala")
        combo_tipo = ttk.Combobox(
            marco_form,
            textvariable=self.var_tipo_servicio,
            values=ETIQUETAS_SERVICIO,
            state="readonly",
            width=37,
        )
        combo_tipo.grid(row=0, column=1, padx=5, pady=3)
        combo_tipo.bind("<<ComboboxSelected>>", self._cambiar_tipo_servicio)

        campos_comunes = [
            ("Nombre:", "srv_nombre"),
            ("Descripción:", "srv_descripcion"),
            ("Tarifa base ($/hora):", "srv_tarifa"),
        ]
        self.vars_servicio = {}
        self.lbl_tarifa_servicio = None
        for i, (etiqueta, clave) in enumerate(campos_comunes, start=1):
            lbl = ttk.Label(marco_form, text=etiqueta)
            lbl.grid(row=i, column=0, sticky=tk.W, pady=3)
            if clave == "srv_tarifa":
                self.lbl_tarifa_servicio = lbl
            var = tk.StringVar()
            self.vars_servicio[clave] = var
            ttk.Entry(marco_form, textvariable=var, width=40).grid(row=i, column=1, padx=5, pady=3)

        self.marco_extra = ttk.Frame(marco_form)
        self.marco_extra.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.vars_extra = {}
        self._cambiar_tipo_servicio()

        ttk.Button(marco_form, text="Registrar Servicio", command=self._registrar_servicio).grid(
            row=5, column=0, columnspan=2, pady=10
        )

        marco_lista = ttk.LabelFrame(frame, text="Servicios disponibles", padding=10)
        marco_lista.pack(fill=tk.BOTH, expand=True)

        self.tree_servicios = ttk.Treeview(
            marco_lista,
            columns=("id", "nombre", "tipo", "tarifa", "cupo", "disponible"),
            show="headings",
            height=10,
        )
        for col, texto, ancho in [
            ("id", "ID", 50),
            ("nombre", "Nombre", 180),
            ("tipo", "Tipo", 130),
            ("tarifa", "Tarifa (unidad)", 120),
            ("cupo", "Cupo permitido", 120),
            ("disponible", "Estado", 100),
        ]:
            self.tree_servicios.heading(col, text=texto)
            self.tree_servicios.column(col, width=ancho)

        scroll = ttk.Scrollbar(marco_lista, orient=tk.VERTICAL, command=self.tree_servicios.yview)
        self.tree_servicios.configure(yscrollcommand=scroll.set)
        self.tree_servicios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _cambiar_tipo_servicio(self, event=None) -> None:
        for widget in self.marco_extra.winfo_children():
            widget.destroy()
        self.vars_extra.clear()

        tipo = TipoServicio.desde_etiqueta(self.var_tipo_servicio.get())
        if self.lbl_tarifa_servicio is not None:
            self.lbl_tarifa_servicio.config(text=ETIQUETA_TARIFA_FORMULARIO[tipo])
        campos = CAMPOS_POR_TIPO[tipo]

        for i, (etiqueta, clave) in enumerate(campos):
            ttk.Label(self.marco_extra, text=etiqueta).grid(row=i, column=0, sticky=tk.W, pady=3)
            if clave == "proyector":
                var = tk.StringVar(value="No")
                ttk.Combobox(
                    self.marco_extra, textvariable=var, values=["Sí", "No"], state="readonly", width=15
                ).grid(row=i, column=1, padx=5)
            elif clave == "nivel":
                var = tk.StringVar(value="intermedio")
                ttk.Combobox(
                    self.marco_extra,
                    textvariable=var,
                    values=["básico", "intermedio", "avanzado"],
                    state="readonly",
                    width=15,
                ).grid(row=i, column=1, padx=5)
            else:
                var = tk.StringVar()
                ttk.Entry(self.marco_extra, textvariable=var, width=20).grid(row=i, column=1, padx=5)
            self.vars_extra[clave] = var

    def _registrar_servicio(self) -> None:
        try:
            tipo = TipoServicio.desde_etiqueta(self.var_tipo_servicio.get())
            datos = {
                "nombre": self.vars_servicio["srv_nombre"].get().strip(),
                "descripcion": self.vars_servicio["srv_descripcion"].get().strip(),
                "tarifa_base": float(self.vars_servicio["srv_tarifa"].get().strip()),
            }

            if tipo == TipoServicio.SALA:
                datos["capacidad"] = int(self.vars_extra["capacidad"].get())
                datos["proyector"] = self.vars_extra["proyector"].get()
            elif tipo == TipoServicio.EQUIPO:
                datos["tipo_equipo"] = self.vars_extra["tipo_equipo"].get()
                datos["cantidad_disponible"] = int(self.vars_extra["cantidad"].get())
            else:
                datos["area_especialidad"] = self.vars_extra["area"].get()
                datos["nivel"] = self.vars_extra["nivel"].get()

            servicio = construir_servicio(tipo, datos)
            resultado = self.sistema.registrar_servicio(servicio)
            es_exito = resultado is not None
            self._mostrar_estado(self.sistema.ultimo_mensaje, es_error=not es_exito)
            if es_exito:
                for var in self.vars_servicio.values():
                    var.set("")
                self._actualizar_lista_servicios()
                self._actualizar_combos_reserva()

        except ValueError as error:
            self._error_validacion(
                "Verifique que los campos numéricos sean válidos.",
                error,
            )
        except Exception as error:
            self._error_validacion("Error inesperado al registrar servicio.", error)

    def _actualizar_lista_servicios(self) -> None:
        for item in self.tree_servicios.get_children():
            self.tree_servicios.delete(item)
        for servicio in self.sistema.servicios:
            tipo = tipo_de_instancia(servicio)
            etiqueta = tipo.etiqueta if tipo else type(servicio).__name__
            estado = "Disponible" if servicio.disponible else "No disponible"
            self.tree_servicios.insert(
                "",
                tk.END,
                values=(
                    servicio.id,
                    servicio.nombre,
                    etiqueta,
                    servicio.formatear_tarifa(),
                    servicio.obtener_cupo_permitido(),
                    estado,
                ),
            )

    def _crear_pestana_reservas(self) -> None:
        """Creación, confirmación, procesamiento y cancelación de reservas."""
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Reservas")

        marco_form = ttk.LabelFrame(frame, text="Crear / Gestionar reserva", padding=10)
        marco_form.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(marco_form, text="Cliente (documento):").grid(row=0, column=0, sticky=tk.W)
        self.var_res_doc = tk.StringVar()
        self.combo_clientes = ttk.Combobox(marco_form, textvariable=self.var_res_doc, width=30)
        self.combo_clientes.grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(marco_form, text="Servicio:").grid(row=1, column=0, sticky=tk.W)
        self.var_res_servicio = tk.StringVar()
        self.combo_servicios = ttk.Combobox(marco_form, textvariable=self.var_res_servicio, width=30)
        self.combo_servicios.grid(row=1, column=1, padx=5, pady=3)
        self.combo_servicios.bind("<<ComboboxSelected>>", self._actualizar_etiquetas_reserva)

        self.lbl_duracion = ttk.Label(marco_form, text="Duración (horas):")
        self.lbl_duracion.grid(row=2, column=0, sticky=tk.W)
        self.var_res_duracion = tk.StringVar(value="1")
        ttk.Entry(marco_form, textvariable=self.var_res_duracion, width=15).grid(
            row=2, column=1, sticky=tk.W, padx=5
        )

        self.lbl_parametro_extra = ttk.Label(marco_form, text="Número de personas:")
        self.lbl_parametro_extra.grid(row=3, column=0, sticky=tk.W)
        self.var_res_extra = tk.StringVar()
        ttk.Entry(marco_form, textvariable=self.var_res_extra, width=15).grid(
            row=3, column=1, sticky=tk.W, padx=5
        )

        self.lbl_info_cupo = ttk.Label(
            marco_form,
            text="Cupo del servicio: —",
            font=("Segoe UI", 9),
            foreground="#444444",
        )
        self.lbl_info_cupo.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        self.lbl_info_flujo = ttk.Label(
            marco_form,
            text="Flujo: Crear reserva (pendiente) → Confirmar (costo final) → Procesar (completada).",
            font=("Segoe UI", 9),
            foreground="#444444",
        )
        self.lbl_info_flujo.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        marco_botones = ttk.Frame(marco_form)
        marco_botones.grid(row=6, column=0, columnspan=2, pady=10)

        for texto, comando in [
            ("Crear Reserva", self._crear_reserva),
            ("Confirmar", self._confirmar_reserva),
            ("Procesar", self._procesar_reserva),
            ("Cancelar", self._cancelar_reserva),
        ]:
            ttk.Button(marco_botones, text=texto, command=comando).pack(side=tk.LEFT, padx=3)

        marco_calculo = ttk.LabelFrame(marco_form, text="Cálculo de costo", padding=5)
        marco_calculo.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(marco_calculo, text="Impuesto (%):").pack(side=tk.LEFT)
        self.var_impuesto = tk.StringVar(value="19")
        ttk.Entry(marco_calculo, textvariable=self.var_impuesto, width=8).pack(side=tk.LEFT, padx=5)

        ttk.Label(marco_calculo, text="Descuento (%):").pack(side=tk.LEFT)
        self.var_descuento = tk.StringVar(value="0")
        ttk.Entry(marco_calculo, textvariable=self.var_descuento, width=8).pack(side=tk.LEFT, padx=5)

        marco_lista = ttk.LabelFrame(frame, text="Reservas registradas", padding=10)
        marco_lista.pack(fill=tk.BOTH, expand=True)

        self.tree_reservas = ttk.Treeview(
            marco_lista,
            columns=("id", "cliente", "servicio", "duracion", "estado", "costo"),
            show="headings",
            height=8,
        )
        for col, texto, ancho in [
            ("id", "ID", 40),
            ("cliente", "Cliente", 150),
            ("servicio", "Servicio", 150),
            ("duracion", "Duración", 90),
            ("estado", "Estado", 90),
            ("costo", "Costo", 140),
        ]:
            self.tree_reservas.heading(col, text=texto)
            self.tree_reservas.column(col, width=ancho)

        scroll = ttk.Scrollbar(marco_lista, orient=tk.VERTICAL, command=self.tree_reservas.yview)
        self.tree_reservas.configure(yscrollcommand=scroll.set)
        self.tree_reservas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def _actualizar_etiquetas_reserva(self, event=None) -> None:
        """Ajusta etiquetas de duración, cupo y parámetros según el servicio seleccionado."""
        servicio = self.sistema.buscar_servicio_por_nombre(self.var_res_servicio.get())
        tipo = tipo_de_instancia(servicio) if servicio else TipoServicio.SALA

        self.lbl_duracion.config(text=ETIQUETA_DURACION.get(tipo, "Duración (horas):"))

        if servicio and tipo == TipoServicio.SALA:
            self.lbl_parametro_extra.config(
                text=f"Número de personas (máx. {servicio.capacidad}):"
            )
        elif servicio and tipo == TipoServicio.EQUIPO:
            self.lbl_parametro_extra.config(
                text=f"Cantidad de equipos (máx. {servicio.cantidad_disponible}):"
            )
        elif tipo == TipoServicio.ASESORIA:
            self.lbl_parametro_extra.config(text="Parámetro extra (no aplica):")
        else:
            self.lbl_parametro_extra.config(text=ETIQUETA_PARAMETRO_RESERVA.get(tipo, "Parámetro:"))

        if servicio:
            self.lbl_info_cupo.config(text=f"Cupo permitido: {servicio.obtener_cupo_permitido()}")
        else:
            self.lbl_info_cupo.config(text="Cupo del servicio: —")

    def _actualizar_combos_reserva(self) -> None:
        self.combo_clientes["values"] = [c.documento for c in self.sistema.clientes]
        self.combo_servicios["values"] = [s.nombre for s in self.sistema.servicios]
        self._actualizar_etiquetas_reserva()

    def _obtener_id_reserva_seleccionada(self) -> int | None:
        seleccion = self.tree_reservas.selection()
        if not seleccion:
            self._error_validacion("Seleccione una reserva de la tabla.")
            return None
        try:
            return int(self.tree_reservas.item(seleccion[0], "values")[0])
        except (ValueError, IndexError) as error:
            self._error_validacion("No se pudo leer el identificador de la reserva.", error)
            return None

    def _crear_reserva(self) -> None:
        try:
            duracion = float(self.var_res_duracion.get())
            servicio = self.sistema.buscar_servicio_por_nombre(self.var_res_servicio.get())
            if servicio is None:
                self._error_validacion("Seleccione un servicio válido.")
                return

            tipo = tipo_de_instancia(servicio)

            if tipo and tipo in LIMITE_DURACION:
                minimo, maximo = LIMITE_DURACION[tipo]
                unidad = "horas" if tipo != TipoServicio.EQUIPO else "días"
                if duracion < minimo or duracion > maximo:
                    self._error_validacion(
                        f"La duración debe estar entre {minimo:g} y {maximo:g} {unidad}."
                    )
                    return

            parametros_extra = {}
            extra = self.var_res_extra.get().strip()
            if tipo in PARAMETRO_RESERVA:
                if not extra:
                    self._error_validacion(
                        "Debe indicar "
                        + ("el número de personas." if tipo == TipoServicio.SALA else "la cantidad de equipos.")
                    )
                    return
                valor = int(extra)
                if tipo == TipoServicio.SALA and valor > servicio.capacidad:
                    self._error_validacion(
                        f"Máximo {servicio.capacidad} personas para '{servicio.nombre}'."
                    )
                    return
                if tipo == TipoServicio.EQUIPO and valor > servicio.cantidad_disponible:
                    self._error_validacion(
                        f"Máximo {servicio.cantidad_disponible} unidades de '{servicio.nombre}'."
                    )
                    return
                parametros_extra[PARAMETRO_RESERVA[tipo]] = valor

            resultado = self.sistema.crear_reserva(
                self.var_res_doc.get(),
                self.var_res_servicio.get(),
                duracion,
                parametros_extra or None,
            )
            es_exito = resultado is not None
            self._mostrar_estado(self.sistema.ultimo_mensaje, es_error=not es_exito)
            if es_exito:
                self._actualizar_lista_reservas()

        except ValueError as error:
            self._error_validacion(
                "La duración y el parámetro extra deben ser numéricos.",
                error,
            )

    def _parsear_porcentaje(self, texto: str) -> float:
        """Convierte texto numérico (acepta coma decimal) a valor entre 0 y 100."""
        return float(texto.strip().replace(",", "."))

    def _obtener_impuesto_y_descuento(self) -> tuple[float | None, float | None]:
        """Lee porcentajes 0-100 de la interfaz y los convierte a decimal para el cálculo."""
        impuesto_pct = None
        descuento_pct = None

        if self.var_impuesto.get().strip():
            impuesto_pct = self._parsear_porcentaje(self.var_impuesto.get())
            if not 0 <= impuesto_pct <= 100:
                raise ValueError("impuesto fuera de rango")

        if self.var_descuento.get().strip():
            descuento_pct = self._parsear_porcentaje(self.var_descuento.get())
            if not 0 <= descuento_pct <= 100:
                raise ValueError("descuento fuera de rango")

        impuesto = impuesto_pct / 100 if impuesto_pct is not None else None
        descuento = descuento_pct / 100 if descuento_pct and descuento_pct > 0 else None
        return impuesto, descuento

    def _confirmar_reserva(self) -> None:
        id_reserva = self._obtener_id_reserva_seleccionada()
        if id_reserva is None:
            return
        try:
            impuesto, descuento = self._obtener_impuesto_y_descuento()
            resultado = self.sistema.confirmar_reserva(id_reserva, impuesto, descuento)
            es_exito = resultado is not None
            self._mostrar_estado(self.sistema.ultimo_mensaje, es_error=not es_exito)
            if es_exito:
                self._actualizar_lista_reservas()
        except ValueError as error:
            if str(error) == "impuesto fuera de rango":
                self._error_validacion("El impuesto debe estar entre 0 y 100.", error)
            elif str(error) == "descuento fuera de rango":
                self._error_validacion("El descuento debe estar entre 0 y 100.", error)
            else:
                self._error_validacion("Impuesto y descuento deben ser numéricos (0-100).", error)

    def _procesar_reserva(self) -> None:
        id_reserva = self._obtener_id_reserva_seleccionada()
        if id_reserva is None:
            return
        resultado = self.sistema.procesar_reserva(id_reserva)
        es_exito = resultado is not None
        self._mostrar_estado(self.sistema.ultimo_mensaje, es_error=not es_exito)
        if es_exito:
            self._actualizar_lista_reservas()

    def _cancelar_reserva(self) -> None:
        id_reserva = self._obtener_id_reserva_seleccionada()
        if id_reserva is None:
            return
        resultado = self.sistema.cancelar_reserva(id_reserva, "Cancelada desde la interfaz")
        self._mostrar_estado(self.sistema.ultimo_mensaje, es_error=not resultado)
        if resultado:
            self._actualizar_lista_reservas()

    def _actualizar_lista_reservas(self) -> None:
        for item in self.tree_reservas.get_children():
            self.tree_reservas.delete(item)
        for reserva in self.sistema.reservas:
            costo = reserva.obtener_costo_visual()
            texto_costo = (
                f"${costo:,.2f} (est.)"
                if reserva.estado.value == "pendiente"
                else f"${costo:,.2f}"
            )
            self.tree_reservas.insert(
                "",
                tk.END,
                values=(
                    reserva.id,
                    reserva.cliente.nombre_completo,
                    reserva.servicio.nombre,
                    reserva.formatear_duracion(),
                    reserva.estado.value,
                    texto_costo,
                ),
            )

    def _crear_pestana_estadisticas(self) -> None:
        """Resumen numérico del sistema y visualización del archivo de log."""
        frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame, text="Estadísticas")

        marco_stats = ttk.LabelFrame(frame, text="Resumen del sistema", padding=15)
        marco_stats.pack(fill=tk.X, pady=(0, 10))

        self.lbl_stats = ttk.Label(marco_stats, text="", font=("Segoe UI", 11), justify=tk.LEFT)
        self.lbl_stats.pack(anchor=tk.W)

        ttk.Button(
            marco_stats, text="Actualizar estadísticas", command=self._actualizar_estadisticas
        ).pack(anchor=tk.W, pady=10)

        marco_logs = ttk.LabelFrame(frame, text="Registro de eventos", padding=10)
        marco_logs.pack(fill=tk.BOTH, expand=True)

        self.txt_logs = tk.Text(marco_logs, height=15, font=("Consolas", 9), state=tk.DISABLED)
        scroll = ttk.Scrollbar(marco_logs, orient=tk.VERTICAL, command=self.txt_logs.yview)
        self.txt_logs.configure(yscrollcommand=scroll.set)
        self.txt_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Button(marco_logs, text="Cargar logs", command=self._cargar_logs).pack(pady=5)

    def _actualizar_estadisticas(self) -> None:
        stats = self.sistema.obtener_estadisticas()
        self.lbl_stats.config(
            text=(
                f"Clientes registrados:    {stats['total_clientes']}\n"
                f"Servicios disponibles:   {stats['total_servicios']}\n"
                f"Total de reservas:       {stats['total_reservas']}\n"
                f"  - Confirmadas:         {stats['confirmadas']}\n"
                f"  - Completadas:         {stats['completadas']}\n"
                f"  - Canceladas:          {stats['canceladas']}\n"
                f"Ingresos totales:        ${stats['ingresos_totales']:,.2f}"
            )
        )

    def _cargar_logs(self) -> None:
        ruta_log = os.path.join("logs", "sistema.log")
        contenido = ""
        try:
            with open(ruta_log, encoding="utf-8") as archivo:
                contenido = archivo.read()
        except FileNotFoundError as error:
            contenido = "No se encontró el archivo de logs."
            self.sistema.registrar_error_ui("Archivo de logs no encontrado", error)
        finally:
            self.txt_logs.config(state=tk.NORMAL)
            self.txt_logs.delete("1.0", tk.END)
            self.txt_logs.insert(tk.END, contenido)
            self.txt_logs.config(state=tk.DISABLED)

    def _actualizar_todas_las_listas(self) -> None:
        self._actualizar_lista_clientes()
        self._actualizar_lista_servicios()
        self._actualizar_lista_reservas()
        self._actualizar_combos_reserva()
        self._actualizar_estadisticas()


def iniciar_interfaz() -> None:
    """Inicialización de la ventana principal y manejo global de excepciones Tk."""
    root = tk.Tk()
    app = InterfazSoftwareFJ(root)

    def manejar_error_tk(exc, val, tb) -> None:
        import traceback

        detalle = "".join(traceback.format_exception(exc, val, tb))
        app.sistema.registrar_error_ui("Error no controlado en la interfaz", val)
        messagebox.showerror(
            "Error del sistema",
            "Ocurrió un error inesperado. Detalle en logs/sistema.log.\n"
            "La aplicación continuará en ejecución.",
        )
        print(detalle)

    root.report_callback_exception = manejar_error_tk
    root.mainloop()


if __name__ == "__main__":
    iniciar_interfaz()
