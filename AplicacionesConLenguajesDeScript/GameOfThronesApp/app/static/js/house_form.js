document.addEventListener('DOMContentLoaded', function() {
    // Get template data from HTML data attributes
    const formContainer = document.querySelector('.form-container');
    const isEditMode = formContainer.dataset.editMode === 'true';
    const currentHouseName = formContainer.dataset.houseName || '';
    
    const form = document.getElementById('houseForm');
    const nameInput = document.getElementById('name');
    const descTextarea = document.getElementById('description');
    const charCount = document.getElementById('desc-count');
    const imageInput = document.getElementById('image');
    const imagePreview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');
    const removePreview = document.getElementById('removePreview');
    const additionalImagesInput = document.getElementById('additional_images');
    const additionalPreview = document.getElementById('additional-preview');
    
    // Contador de caracteres para descripción
    descTextarea.addEventListener('input', function() {
        const count = this.value.length;
        charCount.textContent = count;
        
        if (count > 1500) {
            charCount.style.color = '#dc3545';
        } else if (count > 1200) {
            charCount.style.color = '#ffc107';
        } else {
            charCount.style.color = '#6c757d';
        }
    });
    
    // Validación de nombre único
    let nameTimeout;
    nameInput.addEventListener('input', function() {
        clearTimeout(nameTimeout);
        const feedback = this.parentNode.querySelector('.input-feedback');
        const name = this.value.trim();
        
        if (name.length < 2) {
            feedback.textContent = '';
            return;
        }
        
        nameTimeout = setTimeout(() => {
            fetch(`/api/houses/check-name?name=${encodeURIComponent(name)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.exists && (!isEditMode || name !== currentHouseName)) {
                        feedback.textContent = 'Este nombre de casa ya está en uso';
                        feedback.className = 'input-feedback error';
                    } else {
                        feedback.textContent = 'Nombre disponible';
                        feedback.className = 'input-feedback success';
                    }
                })
                .catch(() => {
                    feedback.textContent = '';
                });
        }, 500);
    });
    
    // Preview de imagen principal
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) {
                alert('La imagen no puede superar los 5MB');
                this.value = '';
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                imagePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Remover preview de imagen principal
    removePreview.addEventListener('click', function() {
        imageInput.value = '';
        imagePreview.style.display = 'none';
    });
    
    // Preview de imágenes adicionales
    additionalImagesInput.addEventListener('change', function(e) {
        const files = Array.from(e.target.files);
        additionalPreview.innerHTML = '';
        
        if (files.length > 3) {
            alert('Máximo 3 imágenes adicionales permitidas');
            this.value = '';
            return;
        }
        
        files.forEach(file => {
            if (file.size > 5 * 1024 * 1024) {
                alert(`La imagen ${file.name} supera los 5MB`);
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const previewDiv = document.createElement('div');
                previewDiv.className = 'additional-image-preview';
                previewDiv.innerHTML = `
                    <img src="${e.target.result}" alt="Preview">
                    <button type="button" class="remove-additional" onclick="this.parentElement.remove()">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                additionalPreview.appendChild(previewDiv);
            };
            reader.readAsDataURL(file);
        });
    });
    
    // Validación del formulario
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const name = nameInput.value.trim();
        const motto = document.getElementById('motto').value.trim();
        const description = descTextarea.value.trim();
        
        let isValid = true;
        let errorMessage = '';
        
        if (name.length < 2) {
            errorMessage = 'El nombre de la casa debe tener al menos 2 caracteres';
            isValid = false;
        } else if (motto.length < 5) {
            errorMessage = 'El lema de la casa debe tener al menos 5 caracteres';
            isValid = false;
        } else if (description.length < 30) {
            errorMessage = 'La descripción debe tener al menos 30 caracteres';
            isValid = false;
        } else if (description.length > 1500) {
            errorMessage = 'La descripción no puede superar los 1500 caracteres';
            isValid = false;
        }
        
        if (!isValid) {
            showNotification(errorMessage, 'error');
            return false;
        }
        
        // Deshabilitar botón durante envío
        const submitBtn = document.getElementById('submitBtn');
        const originalContent = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
        
        try {
            // Preparar datos del formulario
            const formData = new FormData(form);
            
            // Enviar formulario
            const response = await fetch(form.action || window.location.pathname, {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                // Verificar tipo de respuesta
                const contentType = response.headers.get('content-type');
                
                if (contentType && contentType.includes('application/json')) {
                    try {
                        // Manejar respuesta JSON
                        const result = await response.json();
                        
                        if (result.success) {
                            const successMessage = (result.message && result.message.trim()) ? 
                                result.message : 
                                (isEditMode ? '¡Casa actualizada exitosamente!' : '¡Casa creada exitosamente!');
                            
                            showNotification(successMessage, 'success');
                            
                            // Redirigir después de un breve delay
                            setTimeout(() => {
                                if (result.redirect) {
                                    window.location.href = result.redirect;
                                } else if (result.house_id) {
                                    window.location.href = `/houses/${result.house_id}`;
                                } else {
                                    window.location.href = '/houses';
                                }
                            }, 1500);
                        } else {
                            const errorMessage = (result.message && result.message.trim()) ? 
                                result.message : 
                                'Error al procesar la casa';
                            throw new Error(errorMessage);
                        }
                    } catch (jsonError) {
                        // Si hay error al parsear JSON pero la respuesta es exitosa, continuar
                        console.warn('Respuesta exitosa sin JSON válido, continuando...');
                        
                        showNotification(
                            isEditMode ? '¡Casa actualizada exitosamente!' : '¡Casa creada exitosamente!',
                            'success'
                        );
                        
                        setTimeout(() => {
                            window.location.href = '/houses';
                        }, 1500);
                    }
                } else {
                    // Manejar respuesta HTML (para edición)
                    console.log('Respuesta exitosa sin JSON, continuando...');
                    showNotification(
                        isEditMode ? '¡Casa actualizada exitosamente!' : '¡Casa creada exitosamente!',
                        'success'
                    );
                    
                    // Seguir la redirección
                    setTimeout(() => {
                        window.location.href = response.url || '/houses';
                    }, 1500);
                }
            } else {
                // Manejar errores HTTP
                let errorMessage = 'Error al procesar la casa';
                
                try {
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        const errorResult = await response.json();
                        errorMessage = (errorResult.message && errorResult.message.trim()) ? 
                            errorResult.message : errorMessage;
                    } else {
                        // Parsear error desde HTML si es posible
                        const htmlText = await response.text();
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(htmlText, 'text/html');
                        const errorElement = doc.querySelector('.alert-danger, .error-message');
                        errorMessage = (errorElement && errorElement.textContent.trim()) ? 
                            errorElement.textContent.trim() : errorMessage;
                    }
                } catch {
                    errorMessage = `Error del servidor (${response.status})`;
                }
                
                throw new Error(errorMessage);
            }
            
        } catch (error) {
            console.error('Error al enviar formulario:', error);
            const errorMessage = (error.message && error.message.trim()) ? 
                error.message : 
                'Error inesperado al procesar la casa';
            showNotification(errorMessage, 'error');
        } finally {
            // Rehabilitar botón
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalContent;
        }
    });
    
    // Función para mostrar notificaciones
    function showNotification(message, type = 'info') {
        // Verificar que el mensaje no esté vacío
        if (!message || !message.trim()) {
            // Asignar mensaje por defecto según el tipo
            switch(type) {
                case 'success':
                    message = 'Operación completada exitosamente';
                    break;
                case 'error':
                    message = 'Ha ocurrido un error';
                    break;
                case 'warning':
                    message = 'Advertencia';
                    break;
                default:
                    message = 'Información';
            }
        }
        
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Agregar a la página
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remover después de un tiempo
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }
    
    function getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
});