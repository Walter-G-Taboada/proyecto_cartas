function toggleModal(action) {
        const modal = document.getElementById('modal-locales');
        if (modal) {
            if (action) {
                modal.classList.remove('hidden');
            } else {
                modal.classList.add('hidden');
            }
        }
    }

    function actualizarContador() {
        const checkboxes = document.querySelectorAll('input[name="locales_seleccionados"]:checked');
        const contador = document.getElementById('contador-locales');
        if (contador) {
            contador.innerText = checkboxes.length;
        }
    }

    document.addEventListener("DOMContentLoaded", function() {
        actualizarContador();
    });