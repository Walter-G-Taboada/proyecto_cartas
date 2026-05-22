// static/js/precios_masivos.js

/**
 * Función auxiliar para calcular e impactar el precio de Delivery (Columna Roja)
 * aplicando su propio recargo y su norma de REDONDEO INDEPENDIENTE.
 */
function calcularPrecioDelivery(fila, precioSalon) {
    const inputDelivery = fila.querySelector('.input-precio-peya');
    if (!inputDelivery) return;

    // 1. Capturamos el porcentaje de recargo y el tipo de redondeo exclusivo de Delivery
    const porcentajeRecargo = parseFloat(document.getElementById('Herramienta-recargo-delivery').value) || 0;
    const redondeoDelivery = document.getElementById('Herramienta-redondeo-delivery').value;
    
    if (precioSalon > 0) {
        // 2. Calculamos el precio de salón + el recargo bruto de delivery
        let precioDelivery = precioSalon * (1 + (porcentajeRecargo / 100));
        
        // 3. Aplicamos el criterio de redondeo independiente para la columna roja
        if (redondeoDelivery === "50") {
            precioDelivery = Math.ceil(precioDelivery / 50) * 50;
        } else if (redondeoDelivery === "100") {
            precioDelivery = Math.ceil(precioDelivery / 100) * 100;
        } else if (redondeoDelivery === "500") {
            precioDelivery = Math.ceil(precioDelivery / 500) * 500;
        }
        
        inputDelivery.value = precioDelivery.toFixed(2);
    } else {
        inputDelivery.value = (0.00).toFixed(2);
    }
}

/**
 * Recalcula TODA la columna de Delivery de la tabla en vivo si el usuario
 * modifica el porcentaje de recargo o el combo de redondeo superior de delivery.
 */
function actualizarTodaLaColumnaDelivery() {
    const filas = document.querySelectorAll('.fila-producto');
    filas.forEach(fila => {
        const inputPrecioSalon = fila.querySelector('.input-precio-salon');
        const precioSalon = parseFloat(inputPrecioSalon.value) || 0;
        calcularPrecioDelivery(fila, precioSalon);
    });
}

/**
 * Aplica el incremento porcentual simulado a toda la carta o a un rubro específico
 * e incluye las técnicas de redondeo superior y el recargo automático de delivery.
 */
function aplicarAumentoMasivo() {
    const rubroSeleccionado = document.getElementById('Herramienta-rubro').value;
    const porcentajeAumento = parseFloat(document.getElementById('Herramienta-porcentaje').value) || 0;
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
            
            let precioAnterior = celdaBase ? parseFloat(celdaBase.innerText.replace('$', '').trim()) : 0;
            
            if (isNaN(precioAnterior) || precioAnterior <= 0) {
                precioAnterior = parseFloat(inputPrecio.value) || 0;
            }
            
            if (precioAnterior > 0) {
                let nuevoPrecio = precioAnterior * factor;
                
                // Redondeo de Salón (Columna Azul)
                if (tipoRedondeo === "50") {
                    nuevoPrecio = Math.ceil(nuevoPrecio / 50) * 50;
                } else if (tipoRedondeo === "100") {
                    nuevoPrecio = Math.ceil(nuevoPrecio / 100) * 100;
                } else if (tipoRedondeo === "500") {
                    nuevoPrecio = Math.ceil(nuevoPrecio / 500) * 500;
                }
                
                inputPrecio.value = nuevoPrecio.toFixed(2);
                
                if (inputPorcentaje) {
                    inputPorcentaje.value = porcentajeAumento.toFixed(2);
                }

                // Calculamos el precio delivery pasándole el nuevo precio salón
                calcularPrecioDelivery(fila, nuevoPrecio);
            }
        }
    });
}

/**
 * Calcula el Precio Salón de forma individual cuando el usuario escribe un porcentaje (Columna Verde)
 */
function calcularDesdePorcentaje(input) {
    const fila = input.closest('.fila-producto');
    const celdaBase = fila.querySelector('.precio-base-anterior');
    const inputPrecio = fila.querySelector('.input-precio-salon');
    const porcentaje = parseFloat(input.value) || 0;
    
    const tipoRedondeo = document.getElementById('Herramienta-redondeo').value;
    let precioAnterior = celdaBase ? parseFloat(celdaBase.innerText.replace('$', '').trim()) : 0;
    
    if (isNaN(precioAnterior) || precioAnterior <= 0) {
        precioAnterior = parseFloat(inputPrecio.value) || 0;
    }
    
    if (precioAnterior > 0 && porcentaje > 0) {
        let nuevoPrecio = precioAnterior * (1 + (porcentaje / 100));
        
        // Redondeo de Salón
        if (tipoRedondeo === "50") {
            nuevoPrecio = Math.ceil(nuevoPrecio / 50) * 50;
        } else if (tipoRedondeo === "100") {
            nuevoPrecio = Math.ceil(nuevoPrecio / 100) * 100;
        } else if (tipoRedondeo === "500") {
            nuevoPrecio = Math.ceil(nuevoPrecio / 500) * 500;
        }
        
        inputPrecio.value = nuevoPrecio.toFixed(2);

        // Actualiza el delivery aplicando su propio redondeo
        calcularPrecioDelivery(fila, nuevoPrecio);
    }
}

/**
 * Porcentaje de incremento de forma individual cuando el usuario escribe el precio a mano (Columna Azul)
 */
function calcularDesdePrecio(input) {
    const fila = input.closest('.fila-producto');
    const celdaBase = fila.querySelector('.precio-base-anterior');
    const precioNuevo = parseFloat(input.value) || 0;
    const inputPorcentaje = fila.querySelector('.input-porcentaje-individual');
    
    let precioAnterior = celdaBase ? parseFloat(celdaBase.innerText.replace('$', '').trim()) : 0;
    
    if (isNaN(precioAnterior) || precioAnterior <= 0) {
        if (inputPorcentaje) inputPorcentaje.value = (0.00).toFixed(2);
        calcularPrecioDelivery(fila, precioNuevo);
        return;
    }
    
    if (precioAnterior > 0 && precioNuevo > 0) {
        const diferenciaPorcentaje = ((precioNuevo - precioAnterior) / precioAnterior) * 100;
        if (inputPorcentaje) {
            inputPorcentaje.value = diferenciaPorcentaje.toFixed(2);
        }
        
        // Al cambiar el precio de salón a mano, se recalcula su delivery con su propio redondeo
        calcularPrecioDelivery(fila, precioNuevo);
    }
}

/**
 * Control de solo lectura si se consulta un período anterior al mes corriente
 * Y doble candado de seguridad para evitar envíos accidentales por ENTER.
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

    const formulario = document.querySelector('form[action="/guardar_precios_masivo"]');
    if (formulario) {
        formulario.addEventListener('keydown', function(evento) {
            if (evento.key === 'Enter' && evento.target.tagName === 'INPUT') {
                evento.preventDefault();
                return false;
            }
        });

        formulario.addEventListener('submit', function(evento) {
            const confirmacion = confirm("⚠ ¿Estás seguro de que querés guardar de forma permanente los precios de este mes vigencia en el sistema?");
            if (!confirmacion) {
                evento.preventDefault();
            }
        });
    }
});