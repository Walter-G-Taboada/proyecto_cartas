// static/js/precios_masivos.js

/**
 * Aplica el incremento porcentual simulado a toda la carta o a un rubro específico
 * e incluye las técnicas de redondeo superior seleccionadas por el usuario.
 */
function aplicarAumentoMasivo() {
    const rubroSeleccionado = document.getElementById('Herramienta-rubro').value;
    const porcentajeAumento = parseFloat(document.getElementById('Herramienta-porcentaje').value) || 0;
    // Capturamos el método de redondeo del nuevo select del HTML
    const tipoRedondeo = document.getElementById('Herramienta-redondeo').value;
    
    if (porcentajeAumento <= 0) {
        alert("Por favor, ingresá un porcentaje de incremento válido mayor a 0.");
        return;
    }

    const factor = 1 + (porcentajeAumento / 100);
    const filas = document.querySelectorAll('.fila-producto');
    
    filas.forEach(fila => {
        const idRubroFila = fila.getAttribute('data-rubro');
        
        if (rubroSeleccionado === "TODOS" || rubroSeleccionado === idRubroFila) {
            const celdaBase = fila.querySelector('.precio-base-anterior');
            const inputPrecio = fila.querySelector('.input-precio-salon');
            const inputPorcentaje = fila.querySelector('.input-porcentaje-individual');
            
            // LIMPIEZA CLAVE: Quitamos el signo $ y espacios antes de parsear
            let precioAnterior = celdaBase ? parseFloat(celdaBase.innerText.replace('$', '').trim()) : 0;
            
            // Si el mes anterior da error o es cero, tomamos como base el input de salón
            if (isNaN(precioAnterior) || precioAnterior <= 0) {
                precioAnterior = parseFloat(inputPrecio.value) || 0;
            }
            
            // Si tenemos una base real mayor a cero, hacemos la cuenta
            if (precioAnterior > 0) {
                // 1. Calculamos el precio con el aumento exacto básico
                let nuevoPrecio = precioAnterior * factor;
                
                // 2. Aplicamos la técnica de redondeo superior elegida
                if (tipoRedondeo === "50") {
                    nuevoPrecio = Math.ceil(nuevoPrecio / 50) * 50;
                } else if (tipoRedondeo === "100") {
                    nuevoPrecio = Math.ceil(nuevoPrecio / 100) * 100;
                } else if (tipoRedondeo === "500") {
                    nuevoPrecio = Math.ceil(nuevoPrecio / 500) * 500;
                }
                
                // 3. Impactamos el valor final en el input azul
                inputPrecio.value = nuevoPrecio.toFixed(2);
                
                if (inputPorcentaje) {
                    inputPorcentaje.value = porcentajeAumento.toFixed(2);
                }
            }
        }
    });
}

/**
 * Calcula el Precio Salón de forma individual cuando el usuario escribe un porcentaje
 */
function calcularDesdePorcentaje(input) {
    const fila = input.closest('.fila-producto');
    const celdaBase = fila.querySelector('.precio-base-anterior');
    const inputPrecio = fila.querySelector('.input-precio-salon');
    const porcentaje = parseFloat(input.value) || 0;
    
    // LIMPIEZA CLAVE: Quitamos el signo $ y espacios
    let precioAnterior = celdaBase ? parseFloat(celdaBase.innerText.replace('$', '').trim()) : 0;
    
    if (isNaN(precioAnterior) || precioAnterior <= 0) {
        precioAnterior = parseFloat(inputPrecio.value) || 0;
    }
    
    if (precioAnterior > 0 && porcentaje > 0) {
        const nuevoPrecio = precioAnterior * (1 + (porcentaje / 100));
        inputPrecio.value = nuevoPrecio.toFixed(2);
    }
}

/**
 * Porcentaje de incremento de forma individual cuando el usuario escribe el precio a mano
 */
function calcularDesdePrecio(input) {
    const fila = input.closest('.fila-producto');
    const celdaBase = fila.querySelector('.precio-base-anterior');
    const precioNuevo = parseFloat(input.value) || 0;
    const inputPorcentaje = fila.querySelector('.input-porcentaje-individual');
    
    // LIMPIEZA CLAVE: Quitamos el signo $ y espacios
    let precioAnterior = celdaBase ? parseFloat(celdaBase.innerText.replace('$', '').trim()) : 0;
    
    if (isNaN(precioAnterior) || precioAnterior <= 0) {
        if (inputPorcentaje) inputPorcentaje.value = (0.00).toFixed(2);
        return;
    }
    
    if (precioAnterior > 0 && precioNuevo > 0) {
        const diferenciaPorcentaje = ((precioNuevo - precioAnterior) / precioAnterior) * 100;
        if (inputPorcentaje) {
            inputPorcentaje.value = diferenciaPorcentaje.toFixed(2);
        }
    }
}

/**
 * Control de solo lectura si se consulta un período anterior al mes corriente
 */
document.addEventListener("DOMContentLoaded", function() {
    const hoy = new Date();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0');
    const anio = hoy.getFullYear();
    const periodoActualSistema = `${mes}-${anio}`;
    
    const periodoPagina = window.mesActualVigencia;
    
    if (periodoPagina && periodoPagina !== periodoActualSistema) {
        const inputs = document.querySelectorAll('input, select');
        inputs.forEach(input => {
            if(input.id !== 'form-periodo' && input.name !== 'mes_vigencia') {
                input.disabled = true;
            }
        });
        const panel = document.getElementById('panel-incrementos');
        if (panel) panel.classList.add('hidden');
        const controles = document.getElementById('contenedor-controles');
        if (controles) {
            controles.innerHTML = `<p class="text-sm text-yellow-600 text-center w-full font-medium">* Vista Histórica de solo lectura.</p>`;
        }
    }
});