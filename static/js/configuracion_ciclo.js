
document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formConfiguracionCiclo");

    if (!formulario) {
        return;
    }

    const opcionesCiclo = formulario.querySelectorAll(
        'input[name="id_ciclo"]'
    );

    function actualizarSeleccion() {
        opcionesCiclo.forEach((opcion) => {
            const tarjeta = opcion.closest(".ciclo-card");

            if (!tarjeta) {
                return;
            }

            tarjeta.classList.toggle("border-primary", opcion.checked);
            tarjeta.classList.toggle("bg-primary-subtle", opcion.checked);
            tarjeta.classList.toggle("shadow-sm", opcion.checked);
        });
    }

    opcionesCiclo.forEach((opcion) => {
        opcion.addEventListener("change", actualizarSeleccion);
    });

    formulario.addEventListener("submit", (evento) => {
        const cicloSeleccionado = formulario.querySelector(
            'input[name="id_ciclo"]:checked'
        );

        if (!cicloSeleccionado) {
            evento.preventDefault();
            window.alert("Selecciona tu ciclo académico para continuar.");
        }
    });

    actualizarSeleccion();
});
