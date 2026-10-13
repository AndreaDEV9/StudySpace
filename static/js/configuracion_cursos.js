
document.addEventListener("DOMContentLoaded", () => {
    const formularioCursos = document.getElementById("formSeleccionCursos");
    const formularioCrearCurso = document.getElementById("formCrearCurso");
    const contadorCursos = document.getElementById("contadorCursos");

    if (formularioCursos) {
        const casillasCursos = formularioCursos.querySelectorAll(
            ".curso-checkbox"
        );

        function actualizarCursosSeleccionados() {
            let cantidadSeleccionada = 0;

            casillasCursos.forEach((casilla) => {
                const tarjeta = casilla.closest(".curso-card");

                if (casilla.checked) {
                    cantidadSeleccionada += 1;
                }

                if (tarjeta) {
                    tarjeta.classList.toggle(
                        "border-primary",
                        casilla.checked
                    );

                    tarjeta.classList.toggle(
                        "bg-primary-subtle",
                        casilla.checked
                    );

                    tarjeta.classList.toggle(
                        "shadow-sm",
                        casilla.checked
                    );
                }
            });

            if (contadorCursos) {
                contadorCursos.textContent = cantidadSeleccionada;
            }
        }

        casillasCursos.forEach((casilla) => {
            casilla.addEventListener(
                "change",
                actualizarCursosSeleccionados
            );
        });

        actualizarCursosSeleccionados();
    }

    if (formularioCrearCurso) {
        formularioCrearCurso.addEventListener("submit", (evento) => {
            const campoNombre = document.getElementById("nombre_curso");

            if (!campoNombre || !campoNombre.value.trim()) {
                evento.preventDefault();

                window.alert("Escribe el nombre del curso que deseas crear.");

                if (campoNombre) {
                    campoNombre.focus();
                }

                return;
            }

            campoNombre.value = campoNombre.value.trim();
        });
    }
});
