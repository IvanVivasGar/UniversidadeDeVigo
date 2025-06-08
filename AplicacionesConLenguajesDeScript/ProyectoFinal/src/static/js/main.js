/**
 * WesterosTracker - Script Principal
 * Contiene funcionalidades interactivas para la aplicación web
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('WesterosTracker cargado correctamente');

    // Inicializar toasts de Bootstrap para mensajes flash
    initializeFlashToasts();

    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers de Bootstrap
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Gestionar botones de favoritos
    setupFavoriteButtons();

    // Gestionar sistema de valoración
    setupRatingSystem();

    // Añadir animación fade-in a las tarjetas al cargar la página
    animateElements();

    // Gestionar formularios AJAX
    setupAjaxForms();

    // Configurar búsqueda dinámica
    setupDynamicSearch();
});

/**
 * Inicializa los toasts para mensajes flash
 */
function initializeFlashToasts() {
    // Obtener todos los toasts en el contenedor 
    const toasts = document.querySelectorAll('.toast-container .toast');
    
    // Configurar cada toast
    toasts.forEach(toast => {
        // Crear instancia de Toast de Bootstrap con opciones
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: 5000
        });
        
        // Mostrar automáticamente
        bsToast.show();
        
        // Auto-eliminar después de ocultarse
        toast.addEventListener('hidden.bs.toast', function() {
            // Eliminar después de un pequeño retraso para permitir la animación
            setTimeout(() => {
                this.remove();
            }, 300);
        });
    });
}

/**
 * Configura los botones de favoritos para hacer peticiones AJAX
 */
function setupFavoriteButtons() {
    const favoriteButtons = document.querySelectorAll('.js-favorite-btn');
    
    favoriteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const itemId = this.dataset.id;
            const itemType = this.dataset.type;
            const isActive = this.classList.contains('active');
            
            // URL para añadir/quitar favorito
            const url = isActive 
                ? `/api/favorites/${itemType}/${itemId}/remove` 
                : `/api/favorites/${itemType}/${itemId}/add`;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.classList.toggle('active');
                    
                    // Actualizar el icono y texto
                    const icon = this.querySelector('i');
                    const text = this.querySelector('span');
                    
                    if (this.classList.contains('active')) {
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                        if (text) text.textContent = 'En favoritos';
                        
                        showToast('Añadido a favoritos', 'success');
                    } else {
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                        if (text) text.textContent = 'Añadir a favoritos';
                        
                        showToast('Eliminado de favoritos', 'info');
                    }
                } else {
                    showToast(data.message || 'Error al actualizar favoritos', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error al procesar la solicitud', 'error');
            });
        });
    });
}

/**
 * Configura el sistema de valoración (estrellas)
 */
function setupRatingSystem() {
    const ratingContainers = document.querySelectorAll('.rating-container');
    
    ratingContainers.forEach(container => {
        const stars = container.querySelectorAll('.star-rating');
        const ratingValue = container.querySelector('.rating-value');
        const itemId = container.dataset.id;
        const itemType = container.dataset.type;
        
        stars.forEach(star => {
            // Mostrar valoración al pasar el cursor
            star.addEventListener('mouseenter', function() {
                const value = parseInt(this.dataset.value);
                highlightStars(stars, value);
            });
            
            // Restaurar valoración actual al quitar el cursor
            star.addEventListener('mouseleave', function() {
                const currentRating = parseInt(ratingValue.value) || 0;
                highlightStars(stars, currentRating);
            });
            
            // Establecer valoración al hacer clic
            star.addEventListener('click', function() {
                const value = parseInt(this.dataset.value);
                
                fetch(`/api/ratings/${itemType}/${itemId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ rating: value })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        ratingValue.value = value;
                        highlightStars(stars, value);
                        
                        // Actualizar promedio si existe el elemento
                        const avgElement = document.querySelector('.average-rating-value');
                        if (avgElement && data.averageRating) {
                            avgElement.textContent = data.averageRating.toFixed(1);
                        }
                        
                        showToast('¡Valoración registrada!', 'success');
                    } else {
                        showToast(data.message || 'Error al registrar valoración', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showToast('Error al procesar la solicitud', 'error');
                });
            });
        });
    });
}

/**
 * Resalta las estrellas hasta un valor determinado
 */
function highlightStars(stars, value) {
    stars.forEach(star => {
        const starValue = parseInt(star.dataset.value);
        const icon = star.querySelector('i');
        
        if (starValue <= value) {
            icon.classList.add('fas');
            icon.classList.remove('far');
        } else {
            icon.classList.add('far');
            icon.classList.remove('fas');
        }
    });
}

/**
 * Muestra un toast (notificación) en la pantalla
 */
function showToast(message, type = 'info') {
    // Crear contenedor de toasts si no existe
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Crear el toast
    const toastId = 'toast-' + new Date().getTime();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center border-0 ${getToastClass(type)}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.setAttribute('id', toastId);
    
    // Contenido del toast
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${getToastIcon(type)} ${message}
            </div>
            <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Añadir al contenedor
    toastContainer.appendChild(toast);
    
    // Inicializar y mostrar
    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 3000
    });
    bsToast.show();
    
    // Eliminar después de ocultarse
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Obtiene la clase CSS para un tipo de toast
 */
function getToastClass(type) {
    switch (type) {
        case 'success': return 'text-white bg-success';
        case 'error': return 'text-white bg-danger';
        case 'warning': return 'text-white bg-warning';
        default: return 'text-white bg-primary';
    }
}

/**
 * Obtiene el icono para un tipo de toast
 */
function getToastIcon(type) {
    switch (type) {
        case 'success': return '<i class="fas fa-check-circle me-2"></i>';
        case 'error': return '<i class="fas fa-exclamation-circle me-2"></i>';
        case 'warning': return '<i class="fas fa-exclamation-triangle me-2"></i>';
        default: return '<i class="fas fa-info-circle me-2"></i>';
    }
}

/**
 * Añade animaciones a elementos al cargar la página
 */
function animateElements() {
    const elements = document.querySelectorAll('.card, .list-group-item');
    
    elements.forEach((element, index) => {
        setTimeout(() => {
            element.classList.add('fade-in');
        }, index * 100);
    });
}

/**
 * Configura formularios para envío por AJAX
 */
function setupAjaxForms() {
    const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
    
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('[type="submit"]');
            const originalText = submitBtn ? submitBtn.innerHTML : null;
            
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            }
            
            const formData = new FormData(form);
            const url = form.getAttribute('action') || window.location.href;
            const method = form.getAttribute('method') || 'POST';
            
            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (data.message) {
                        showToast(data.message, 'success');
                    }
                    
                    if (data.redirect) {
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 1000);
                    }
                    
                    if (data.reload) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    }
                    
                    if (form.dataset.reset === 'true') {
                        form.reset();
                    }
                } else {
                    showToast(data.message || 'Error al procesar la solicitud', 'error');
                    
                    // Mostrar errores específicos de los campos si existen
                    if (data.errors) {
                        for (const [field, message] of Object.entries(data.errors)) {
                            const inputField = form.querySelector(`[name="${field}"]`);
                            if (inputField) {
                                inputField.classList.add('is-invalid');
                                
                                // Crear o actualizar mensaje de error
                                let feedbackDiv = inputField.nextElementSibling;
                                if (!feedbackDiv || !feedbackDiv.classList.contains('invalid-feedback')) {
                                    feedbackDiv = document.createElement('div');
                                    feedbackDiv.className = 'invalid-feedback';
                                    inputField.parentNode.insertBefore(feedbackDiv, inputField.nextSibling);
                                }
                                
                                feedbackDiv.textContent = message;
                            }
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error al procesar la solicitud', 'error');
            })
            .finally(() => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }
            });
        });
    });
}

/**
 * Configura la búsqueda dinámica en campos de búsqueda
 */
function setupDynamicSearch() {
    // Búsqueda para listas locales (personajes y casas)
    const filterInputs = document.querySelectorAll('#filterInput');
    
    filterInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            const items = document.querySelectorAll('.filter-item');
            
            items.forEach(item => {
                // Buscar en cualquier texto dentro del elemento
                const text = item.textContent.toLowerCase();
                
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Mostrar mensaje si no hay resultados
            const visibleItems = document.querySelectorAll('.filter-item[style="display: none;"]');
            const noResultsMsg = document.getElementById('noResultsMessage');
            
            if (visibleItems.length === items.length && searchTerm) {
                // Si no existe el mensaje, crearlo
                if (!noResultsMsg) {
                    const msg = document.createElement('div');
                    msg.id = 'noResultsMessage';
                    msg.className = 'col-12 text-center py-4';
                    msg.innerHTML = '<div class="alert alert-info">No se encontraron resultados para tu búsqueda</div>';
                    
                    // Insertar después de la fila de filtros
                    const parentRow = document.querySelector('.row:has(.filter-item)');
                    if (parentRow) {
                        parentRow.appendChild(msg);
                    }
                } else {
                    noResultsMsg.style.display = '';
                }
            } else if (noResultsMsg) {
                noResultsMsg.style.display = 'none';
            }
        });
    });
    
    // Mantener la configuración AJAX original para otros casos
    const searchInputs = document.querySelectorAll('[data-search="dynamic"]');
    
    searchInputs.forEach(input => {
        const resultsContainer = document.querySelector(input.dataset.results);
        const debounceTimeout = parseInt(input.dataset.debounce || '300');
        let timeoutId;
        
        if (resultsContainer) {
            input.addEventListener('input', function() {
                clearTimeout(timeoutId);
                
                const query = this.value.trim();
                const url = input.dataset.url;
                
                if (query.length < 2) {
                    resultsContainer.innerHTML = '';
                    return;
                }
                
                timeoutId = setTimeout(() => {
                    resultsContainer.innerHTML = '<div class="text-center py-3"><i class="fas fa-spinner fa-spin"></i> Buscando...</div>';
                    
                    fetch(`${url}?q=${encodeURIComponent(query)}`, {
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.html) {
                            resultsContainer.innerHTML = data.html;
                        } else {
                            resultsContainer.innerHTML = '<div class="text-center py-3">No se encontraron resultados</div>';
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        resultsContainer.innerHTML = '<div class="text-center py-3 text-danger">Error al buscar</div>';
                    });
                }, debounceTimeout);
            });
        }
    });
}