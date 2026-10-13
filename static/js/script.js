document.addEventListener("DOMContentLoaded", () => {
    const universidad = document.getElementById("id_universidad");
    const carrera = document.getElementById("id_carrera");
    const mensaje = document.getElementById("mensajeCarreras");

    if (!universidad || !carrera) {
        console.error("StudySpace: no se encontraron los selectores académicos.");
        return;
    }

    const carreraInicial = carrera.dataset.carreraInicial || "";
    let solicitudCarreras = 0;

    const ENDPOINTS = {
        carreras: id => `/api/carreras/${encodeURIComponent(id)}`,
        crearCarrera: "/api/carreras",
        crearUniversidad: "/api/universidades"
    };

    // --------------------------------------------------
    // UTILIDADES
    // --------------------------------------------------

    function mostrarMensaje(texto, tipo = "success") {
        if (!mensaje) return;

        mensaje.textContent = texto;
        mensaje.classList.remove("text-success", "text-danger", "text-muted");
        mensaje.classList.add(
            tipo === "error" ? "text-danger" :
            tipo === "info" ? "text-muted" : "text-success"
        );
    }

    function crearElemento(tag, opciones = {}) {
        const elemento = document.createElement(tag);

        if (opciones.texto !== undefined) {
            elemento.textContent = opciones.texto;
        }

        if (opciones.clase) {
            elemento.className = opciones.clase;
        }

        if (opciones.tipo) {
            elemento.type = opciones.tipo;
        }

        if (opciones.valor !== undefined) {
            elemento.value = opciones.valor;
        }

        if (opciones.placeholder) {
            elemento.placeholder = opciones.placeholder;
        }

        return elemento;
    }

    function crearBoton(texto, clase, accion) {
        const boton = crearElemento("button", {
            texto,
            clase: `btn ${clase}`,
            tipo: "button"
        });

        boton.addEventListener("click", accion);
        return boton;
    }

    async function solicitar(url, opciones = {}) {
        const respuesta = await fetch(url, {
            ...opciones,
            headers: {
                ...(opciones.body ? { "Content-Type": "application/json" } : {}),
                ...opciones.headers
            }
        });

        const datos = await respuesta.json().catch(() => ({}));

        if (!respuesta.ok) {
            throw new Error(
                datos.error || datos.mensaje || `Error HTTP ${respuesta.status}`
            );
        }

        return datos;
    }

    function enviar(url, datos) {
        return solicitar(url, {
            method: "POST",
            body: JSON.stringify(datos)
        });
    }

    function establecerCarga(boton, cargando, textoOriginal) {
        boton.disabled = cargando;
        boton.textContent = cargando ? "Guardando..." : textoOriginal;
    }

    function cerrarPanel(id) {
        document.getElementById(id)?.remove();
    }

    function crearPanel(id, tituloTexto, referencia) {
        cerrarPanel(id);

        const panel = crearElemento("div", {
            clase: "mt-3 p-3 border rounded"
        });

        panel.id = id;

        const titulo = crearElemento("h5", {
            texto: tituloTexto
        });

        panel.appendChild(titulo);
        referencia.insertAdjacentElement("afterend", panel);

        return panel;
    }

    function agregarOpcion(select, valor, texto) {
        let opcion = Array.from(select.options).find(
            item => String(item.value) === String(valor)
        );

        if (!opcion) {
            opcion = crearElemento("option", { valor, texto });
            select.appendChild(opcion);
        } else {
            opcion.textContent = texto;
        }

        return opcion;
    }


    // CARGAR CARRERAS

    async function cargarCarreras(idUniversidad, idCarrera = "") {
        const numeroSolicitud = ++solicitudCarreras;

        carrera.replaceChildren(
            crearElemento("option", {
                texto: idUniversidad
                    ? "Cargando carreras..."
                    : "Primero selecciona tu institución",
                valor: ""
            })
        );

        carrera.disabled = true;

        if (!idUniversidad) {
            mostrarMensaje("Selecciona una institución para consultar sus carreras.", "info");
            return;
        }

        try {
            const carreras = await solicitar(
                ENDPOINTS.carreras(idUniversidad)
            );

            // Ignorar resultados antiguos si cambió la institución.
            if (numeroSolicitud !== solicitudCarreras) return;

            carrera.replaceChildren(
                crearElemento("option", {
                    texto: "Selecciona tu carrera",
                    valor: ""
                })
            );

            carreras.forEach(item => {
                const opcion = crearElemento("option", {
                    texto: item.nombre,
                    valor: item.id_carrera
                });

                opcion.selected = String(item.id_carrera) === String(idCarrera);
                carrera.appendChild(opcion);
            });

            carrera.appendChild(
                crearElemento("option", {
                    texto: "+ Agregar una carrera",
                    valor: "__agregar__"
                })
            );

            carrera.disabled = false;

            mostrarMensaje(
                carreras.length
                    ? "Selecciona tu carrera o agrega una si no aparece."
                    : "No hay carreras asociadas. Puedes registrar una.",
                "info"
            );

        } catch (error) {
            if (numeroSolicitud !== solicitudCarreras) return;

            console.error("Error al cargar carreras:", error);

            carrera.replaceChildren(
                crearElemento("option", {
                    texto: "No se pudieron cargar las carreras",
                    valor: ""
                })
            );

            mostrarMensaje(error.message, "error");
        }
    }


    // FORMULARIO REUTILIZABLE PARA REGISTROS
    function crearFormulario({
        id,
        titulo,
        referencia,
        campos,
        textoGuardar,
        guardarDatos
    }) {
        const panel = crearPanel(id, titulo, referencia);
        const entradas = {};

        campos.forEach(campo => {
            const etiqueta = crearElemento("label", {
                texto: campo.etiqueta,
                clase: "form-label mt-2"
            });

            const entrada = crearElemento(campo.tag || "input", {
                clase: "form-control",
                tipo: campo.tipo || "text",
                placeholder: campo.placeholder || "",
                valor: campo.valor || ""
            });

            if (campo.tag === "select") {
                campo.opciones.forEach(opcion => {
                    entrada.appendChild(
                        crearElemento("option", {
                            texto: opcion.texto,
                            valor: opcion.valor
                        })
                    );
                });
            }

            if (campo.maxLength) entrada.maxLength = campo.maxLength;
            if (campo.requerido !== false) entrada.required = true;

            panel.append(etiqueta, entrada);
            entradas[campo.nombre] = entrada;
        });

        const acciones = crearElemento("div", {
            clase: "d-flex gap-2 mt-3"
        });

        const botonGuardar = crearBoton(
            textoGuardar,
            "btn-primary",
            async () => {
                for (const entrada of Object.values(entradas)) {
                    if (!entrada.value.trim()) {
                        entrada.reportValidity();
                        entrada.focus();
                        return;
                    }
                }

                const datos = Object.fromEntries(
                    Object.entries(entradas).map(([nombre, entrada]) => [
                        nombre,
                        entrada.value.trim()
                    ])
                );

                establecerCarga(botonGuardar, true, textoGuardar);

                try {
                    await guardarDatos(datos);
                    panel.remove();
                } catch (error) {
                    console.error(error);
                    mostrarMensaje(error.message || "No se pudo guardar.", "error");
                } finally {
                    if (botonGuardar.isConnected) {
                        establecerCarga(botonGuardar, false, textoGuardar);
                    }
                }
            }
        );

        const botonCancelar = crearBoton(
            "Cancelar",
            "btn-secondary",
            () => panel.remove()
        );

        acciones.append(botonGuardar, botonCancelar);
        panel.appendChild(acciones);

        Object.values(entradas)[0]?.focus();

        return panel;
    }

    // --------------------------------------------------
    // AGREGAR CARRERA
    // --------------------------------------------------

    function mostrarFormularioCarrera() {
        if (!universidad.value) {
            mostrarMensaje("Primero selecciona una institución.", "error");
            return;
        }

        crearFormulario({
            id: "panelAgregarCarrera",
            titulo: "Agregar carrera",
            referencia: carrera,
            textoGuardar: "Guardar carrera",

            campos: [
                {
                    nombre: "nombre",
                    etiqueta: "Nombre de la carrera",
                    placeholder: "Ej.: Desarrollo de Sistemas de Información",
                    maxLength: 100
                }
            ],

            guardarDatos: async datos => {
                const resultado = await enviar(ENDPOINTS.crearCarrera, {
                    nombre: datos.nombre,
                    id_universidad: universidad.value
                });

                if (!resultado.id_carrera) {
                    throw new Error("El servidor no devolvió el ID de la carrera.");
                }

                await cargarCarreras(universidad.value, resultado.id_carrera);

                mostrarMensaje(
                    resultado.created
                        ? "Carrera registrada correctamente."
                        : "La carrera existente se ha reutilizado."
                );
            }
        });
    }

    // --------------------------------------------------
    // AGREGAR UNIVERSIDAD O INSTITUTO
    // --------------------------------------------------

    function mostrarFormularioUniversidad() {
        crearFormulario({
            id: "panelAgregarUniversidad",
            titulo: "Agregar universidad o instituto",
            referencia: universidad,
            textoGuardar: "Guardar institución",

            campos: [
                {
                    nombre: "nombre",
                    etiqueta: "Nombre de la institución",
                    placeholder: "Escribe el nombre",
                    maxLength: 150
                },
                {
                    nombre: "tipo_institucion",
                    etiqueta: "Tipo de institución",
                    tag: "select",
                    opciones: [
                        { texto: "Universidad", valor: "UNIVERSIDAD" },
                        { texto: "Instituto", valor: "INSTITUTO" }
                    ]
                }
            ],

            guardarDatos: async datos => {
                const resultado = await enviar(
                    ENDPOINTS.crearUniversidad,
                    datos
                );

                if (!resultado.id_universidad) {
                    throw new Error("El servidor no devolvió el ID de la institución.");
                }

                const opcionAgregar = Array.from(universidad.options).find(
                    item => item.value === "__agregar__"
                );

                const opcion = agregarOpcion(
                    universidad,
                    resultado.id_universidad,
                    resultado.nombre
                );

                // Mantener la opción especial al final de la lista.
                if (opcionAgregar) {
                    universidad.appendChild(opcionAgregar);
                }

                universidad.value = resultado.id_universidad;

                await cargarCarreras(resultado.id_universidad);

                mostrarMensaje(
                    resultado.created
                        ? "Institución registrada. Ahora selecciona o agrega tu carrera."
                        : "La institución existente se ha seleccionado."
                );
            }
        });
    }

    // --------------------------------------------------
    // OPCIONES PARA AGREGAR
    // --------------------------------------------------

    universidad.appendChild(
        crearElemento("option", {
            texto: "+ Agregar universidad o instituto",
            valor: "__agregar__"
        })
    );

    universidad.addEventListener("change", () => {
        if (universidad.value === "__agregar__") {
            universidad.value = "";
            mostrarFormularioUniversidad();
            return;
        }

        cerrarPanel("panelAgregarUniversidad");
        cerrarPanel("panelAgregarCarrera");

        cargarCarreras(universidad.value);
    });

    carrera.addEventListener("change", () => {
        if (carrera.value === "__agregar__") {
            carrera.value = "";
            mostrarFormularioCarrera();
        }
    });

    // --------------------------------------------------
    // INICIALIZACIÓN
    // --------------------------------------------------

    if (universidad.value) {
        cargarCarreras(universidad.value, carreraInicial);
    } else {
        carrera.replaceChildren(
            crearElemento("option", {
                texto: "Primero selecciona tu institución",
                valor: ""
            })
        );

        carrera.disabled = true;
    }
});

// ojito 
document.addEventListener("click", function (evento) {
    const boton = evento.target.closest("[data-toggle-password]");

    if (!boton) return;

    const campo = document.getElementById(
        boton.dataset.togglePassword
    );

    if (!campo) return;

    const mostrar = campo.type === "password";

    campo.type = mostrar ? "text" : "password";

    boton.setAttribute(
        "aria-label",
        mostrar ? "Ocultar contraseña" : "Mostrar contraseña"
    );

    boton.setAttribute("aria-pressed", String(mostrar));

    const icono = boton.querySelector("svg");

    if (icono) {
        icono.innerHTML = mostrar
            ? `
                <path d="M3 3l18 18"/>
                <path d="M10.6 10.6a2 2 0 002.8 2.8"/>
                <path d="M9.9 5.2A11 11 0 0112 5c6.5 0 10 7 10 7a15 15 0 01-4 4.8"/>
                <path d="M6.2 6.2C3.5 8 2 12 2 12s3.5 7 10 7c1 0 2-.2 2.9-.5"/>
            `
            : `
                <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/>
                <circle cx="12" cy="12" r="3"/>
            `;
    }
});
