
document.addEventListener("DOMContentLoaded", () => {
    const universidadSelect = document.getElementById("id_universidad");
    const carreraSelect = document.getElementById("id_carrera");
    const mensajeCarreras = document.getElementById("mensajeCarreras");
    const formulario = document.getElementById("formConfiguracionCarrera");

    if (!universidadSelect || !carreraSelect) {
        return;
    }

    const carreraGuardada = carreraSelect.dataset.carreraSeleccionada || "";

    function mostrarEstadoCarreras(mensaje, deshabilitar = true) {
        carreraSelect.innerHTML = "";

        const opcion = document.createElement("option");
        opcion.value = "";
        opcion.textContent = mensaje;

        carreraSelect.appendChild(opcion);
        carreraSelect.disabled = deshabilitar;

        if (mensajeCarreras) {
            mensajeCarreras.textContent = mensaje;
        }
    }

    async function cargarCarreras(idUniversidad, carreraSeleccionada = "") {
        if (!idUniversidad) {
            mostrarEstadoCarreras("Primero selecciona una institución");
            return;
        }

        mostrarEstadoCarreras("Cargando carreras...");

        try {
            const respuesta = await fetch(
                `/api/carreras/${encodeURIComponent(idUniversidad)}`,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

            if (!respuesta.ok) {
                throw new Error("No se pudieron consultar las carreras.");
            }

            const carreras = await respuesta.json();

            carreraSelect.innerHTML = "";

            const opcionInicial = document.createElement("option");
            opcionInicial.value = "";
            opcionInicial.textContent = "Selecciona tu carrera";
            carreraSelect.appendChild(opcionInicial);

            if (!Array.isArray(carreras) || carreras.length === 0) {
                mostrarEstadoCarreras(
                    "No hay carreras registradas para esta institución"
                );
                return;
            }

            carreras.forEach((carrera) => {
                const opcion = document.createElement("option");

                opcion.value = carrera.id_carrera;
                opcion.textContent = carrera.nombre;

                if (
                    String(carrera.id_carrera) ===
                    String(carreraSeleccionada)
                ) {
                    opcion.selected = true;
                }

                carreraSelect.appendChild(opcion);
            });

            carreraSelect.disabled = false;

            if (mensajeCarreras) {
                mensajeCarreras.textContent =
                    "Selecciona la carrera que estás cursando.";
            }
        } catch (error) {
            console.error("Error al cargar carreras:", error);

            mostrarEstadoCarreras(
                "Ocurrió un error al cargar las carreras"
            );
        }
    }

    universidadSelect.addEventListener("change", () => {
        cargarCarreras(universidadSelect.value);
    });

    if (universidadSelect.value) {
        cargarCarreras(universidadSelect.value, carreraGuardada);
    }

    if (formulario) {
        formulario.addEventListener("submit", (evento) => {
            if (
                !universidadSelect.value ||
                !carreraSelect.value ||
                carreraSelect.disabled
            ) {
                evento.preventDefault();
                window.alert(
                    "Selecciona tu institución y tu carrera antes de continuar."
                );
            }
        });
    }
});
