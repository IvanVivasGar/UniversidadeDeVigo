/**
 * ========================================================================
 * GAME OF THRONES - EVENT FORM EPIC FUNCTIONALITY
 * ========================================================================
 * Sistema avanzado de creación y edición de eventos épicos
 * Con validación en tiempo real, efectos visuales y experiencia inmersiva
 */

class EventFormManager {
    constructor() {
        this.formContainer = document.querySelector('.form-container');
        this.isEditMode = this.formContainer?.dataset.editMode === 'true';
        this.currentEventName = this.formContainer?.dataset.eventName || '';
        
        this.form = document.getElementById('eventForm');
        this.elements = this.getFormElements();
        this.validationRules = this.setupValidationRules();
        this.uploadedFiles = {
            main: null,
            additional: []
        };
        
        this.init();
    }

    getFormElements() {
        return {
            nameInput: document.getElementById('name'),
            seasonSelect: document.getElementById('season'),
            episodeSelect: document.getElementById('episode'),
            importanceSelect: document.getElementById('importance_rating'),
            descTextarea: document.getElementById('description'),
            characterSelect: document.getElementById('character_ids'),
            houseSelect: document.getElementById('house_ids'),
            imageInput: document.getElementById('image'),
            additionalImagesInput: document.getElementById('additional_images'),
            charCount: document.getElementById('desc-count'),
            imagePreview: document.getElementById('image-preview'),
            previewImg: document.getElementById('preview-img'),
            removePreview: document.getElementById('removePreview'),
            additionalPreview: document.getElementById('additional-preview'),
            submitBtn: document.getElementById('submitBtn')
        };
    }

    setupValidationRules() {
        return {
            name: {
                required: true,
                minLength: 3,
                maxLength: 100,
                pattern: /^[a-zA-ZÀ-ÿ\u00f1\u00d1\s\-'\.,:;!?\(\)]+$/,
                asyncCheck: true
            },
            season: {
                required: true,
                min: 1,
                max: 8
            },
            episode: {
                required: true,
                min: 1,
                max: 10
            },
            importance_rating: {
                required: true,
                min: 1,
                max: 5
            },
            description: {
                required: true,
                minLength: 50,
                maxLength: 2000
            }
        };
    }

    init() {
        console.log('🏰 Inicializando Event Form Manager...');
        
        this.setupEventListeners();
        this.setupAdvancedFeatures();
        this.setupFormValidation();
        this.setupImageHandling();
        this.setupAutoSave();
        this.initializeFormState();
        
        console.log('⚔️ Event Form Manager listo para la batalla!');
    }

    setupEventListeners() {
        // Validación de nombre en tiempo real
        this.elements.nameInput?.addEventListener('input', (e) => {
            this.handleNameValidation(e.target);
        });

        // Validación de descripción con contador de caracteres
        this.elements.descTextarea?.addEventListener('input', (e) => {
            this.handleDescriptionValidation(e.target);
        });

        // Validación dinámica de selects
        ['seasonSelect', 'episodeSelect', 'importanceSelect'].forEach(elementKey => {
            this.elements[elementKey]?.addEventListener('change', (e) => {
                this.validateField(e.target);
            });
        });

        // Manejo de imágenes
        this.elements.imageInput?.addEventListener('change', (e) => {
            this.handleMainImageUpload(e);
        });

        this.elements.additionalImagesInput?.addEventListener('change', (e) => {
            this.handleAdditionalImagesUpload(e);
        });

        this.elements.removePreview?.addEventListener('click', () => {
            this.removeMainImagePreview();
        });

        // Validación del formulario al enviar
        this.form?.addEventListener('submit', (e) => {
            this.handleFormSubmission(e);
        });

        // Efectos visuales en focus/blur
        this.setupFocusEffects();
    }

    setupAdvancedFeatures() {
        // Sistema de episodios dinámicos según temporada
        this.elements.seasonSelect?.addEventListener('change', (e) => {
            this.updateEpisodeOptions(e.target.value);
        });

        // Búsqueda en selects múltiples
        this.setupMultiSelectSearch();

        // Tooltips informativos
        this.setupTooltips();

        // Atajos de teclado
        this.setupKeyboardShortcuts();

        // Confirmación antes de salir si hay cambios
        this.setupUnsavedChangesWarning();
    }

    setupFormValidation() {
        // Validación en tiempo real para todos los campos
        Object.keys(this.elements).forEach(key => {
            const element = this.elements[key];
            if (element && element.tagName !== 'BUTTON' && element.type !== 'file') {
                element.addEventListener('blur', () => {
                    this.validateField(element);
                });
            }
        });
    }

    setupImageHandling() {
        // Drag & Drop para imágenes
        this.setupDragAndDrop();
        
        // Validación de archivos
        this.setupFileValidation();
        
        // Compresión de imágenes
        this.setupImageCompression();
    }

    setupDragAndDrop() {
        const dropZones = document.querySelectorAll('.file-label');
        
        dropZones.forEach(dropZone => {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('drag-over');
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('drag-over');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('drag-over');
                
                const files = e.dataTransfer.files;
                const input = dropZone.parentElement.querySelector('input[type="file"]');
                
                if (input && files.length > 0) {
                    this.handleFilesDrop(input, files);
                }
            });
        });
    }

    handleFilesDrop(input, files) {
        if (input.id === 'image') {
            if (files.length === 1) {
                const dt = new DataTransfer();
                dt.items.add(files[0]);
                input.files = dt.files;
                this.handleMainImageUpload({ target: input });
            }
        } else if (input.id === 'additional_images') {
            const dt = new DataTransfer();
            Array.from(files).slice(0, 4).forEach(file => dt.items.add(file));
            input.files = dt.files;
            this.handleAdditionalImagesUpload({ target: input });
        }
    }

    async handleNameValidation(input) {
        const name = input.value.trim();
        const feedback = this.getFeedbackElement(input);
        
        // Validación local primero
        if (name.length === 0) {
            this.setFieldState(input, 'neutral', '');
            return;
        }

        if (name.length < this.validationRules.name.minLength) {
            this.setFieldState(input, 'error', `Mínimo ${this.validationRules.name.minLength} caracteres`);
            return;
        }

        if (name.length > this.validationRules.name.maxLength) {
            this.setFieldState(input, 'error', `Máximo ${this.validationRules.name.maxLength} caracteres`);
            return;
        }

        if (!this.validationRules.name.pattern.test(name)) {
            this.setFieldState(input, 'error', 'Solo letras, espacios y algunos signos de puntuación');
            return;
        }

        // Validación asíncrona de disponibilidad
        this.setFieldState(input, 'loading', 'Verificando disponibilidad...');
        
        try {
            const response = await fetch(`/events/api/check-name?name=${encodeURIComponent(name)}`);
            const data = await response.json();
            
            if (data.exists && (!this.isEditMode || name !== this.currentEventName)) {
                this.setFieldState(input, 'error', 'Este nombre de evento ya está en uso');
            } else {
                this.setFieldState(input, 'success', '✓ Nombre disponible');
            }
        } catch (error) {
            console.error('Error validando nombre:', error);
            this.setFieldState(input, 'neutral', '');
        }
    }

    handleDescriptionValidation(textarea) {
        const text = textarea.value;
        const length = text.length;
        const charCountElement = this.elements.charCount;
        
        // Actualizar contador
        if (charCountElement) {
            charCountElement.textContent = length;
            
            if (length > 2000) {
                charCountElement.style.color = 'var(--blood-red)';
            } else if (length > 1600) {
                charCountElement.style.color = '#ffc107';
            } else if (length >= 50) {
                charCountElement.style.color = 'var(--primary-gold)';
            } else {
                charCountElement.style.color = '#6c757d';
            }
        }

        // Validación
        if (length === 0) {
            this.setFieldState(textarea, 'neutral', '');
        } else if (length < this.validationRules.description.minLength) {
            this.setFieldState(textarea, 'error', `Mínimo ${this.validationRules.description.minLength} caracteres`);
        } else if (length > this.validationRules.description.maxLength) {
            this.setFieldState(textarea, 'error', `Máximo ${this.validationRules.description.maxLength} caracteres`);
        } else {
            this.setFieldState(textarea, 'success', '✓ Descripción válida');
        }
    }

    validateField(field) {
        const fieldName = field.name || field.id;
        const rules = this.validationRules[fieldName];
        
        if (!rules) return true;

        const value = field.value.trim();
        
        // Campo requerido
        if (rules.required && !value) {
            this.setFieldState(field, 'error', 'Este campo es obligatorio');
            return false;
        }

        // Validaciones específicas ya manejadas por funciones dedicadas
        if (fieldName === 'name' || fieldName === 'description') {
            return true; // Ya validado por funciones específicas
        }

        // Validación de selects
        if (field.tagName === 'SELECT') {
            if (rules.required && (!value || value === '')) {
                this.setFieldState(field, 'error', 'Debes seleccionar una opción');
                return false;
            } else if (value) {
                this.setFieldState(field, 'success', '✓');
                return true;
            }
        }

        return true;
    }

    setFieldState(field, state, message) {
        const feedback = this.getFeedbackElement(field);
        
        // Remover clases previas
        field.classList.remove('valid', 'invalid', 'loading');
        
        // Aplicar nuevo estado
        switch (state) {
            case 'success':
                field.classList.add('valid');
                if (feedback) {
                    feedback.textContent = message;
                    feedback.className = 'input-feedback success';
                }
                break;
            case 'error':
                field.classList.add('invalid');
                if (feedback) {
                    feedback.textContent = message;
                    feedback.className = 'input-feedback error';
                }
                break;
            case 'loading':
                field.classList.add('loading');
                if (feedback) {
                    feedback.textContent = message;
                    feedback.className = 'input-feedback loading';
                }
                break;
            case 'neutral':
            default:
                if (feedback) {
                    feedback.textContent = message;
                    feedback.className = 'input-feedback';
                }
                break;
        }
    }

    getFeedbackElement(field) {
        let feedback = field.parentNode.querySelector('.input-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'input-feedback';
            field.parentNode.appendChild(feedback);
        }
        return feedback;
    }

    async handleMainImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        // Validar archivo
        if (!this.validateImageFile(file, 'main')) {
            event.target.value = '';
            return;
        }

        try {
            // Comprimir imagen si es necesario
            const processedFile = await this.compressImage(file);
            
            // Mostrar preview
            const reader = new FileReader();
            reader.onload = (e) => {
                if (this.elements.previewImg && this.elements.imagePreview) {
                    this.elements.previewImg.src = e.target.result;
                    this.elements.imagePreview.style.display = 'block';
                    
                    // Efecto de aparición
                    this.elements.imagePreview.style.opacity = '0';
                    this.elements.imagePreview.style.transform = 'scale(0.8)';
                    setTimeout(() => {
                        this.elements.imagePreview.style.transition = 'all 0.3s ease';
                        this.elements.imagePreview.style.opacity = '1';
                        this.elements.imagePreview.style.transform = 'scale(1)';
                    }, 50);
                }
            };
            reader.readAsDataURL(processedFile);
            
            this.uploadedFiles.main = processedFile;
            
            // Mostrar notificación de éxito
            this.showNotification('Imagen cargada exitosamente', 'success');
            
        } catch (error) {
            console.error('Error procesando imagen:', error);
            this.showNotification('Error al procesar la imagen', 'error');
            event.target.value = '';
        }
    }

    async handleAdditionalImagesUpload(event) {
        const files = Array.from(event.target.files);
        
        if (files.length > 4) {
            this.showNotification('Máximo 4 imágenes adicionales permitidas', 'warning');
            event.target.value = '';
            return;
        }

        try {
            this.elements.additionalPreview.innerHTML = '';
            this.uploadedFiles.additional = [];

            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                
                if (!this.validateImageFile(file, 'additional')) {
                    continue;
                }

                const processedFile = await this.compressImage(file);
                this.uploadedFiles.additional.push(processedFile);

                // Crear preview
                const reader = new FileReader();
                reader.onload = (e) => {
                    const previewDiv = document.createElement('div');
                    previewDiv.className = 'additional-image-preview';
                    previewDiv.style.opacity = '0';
                    previewDiv.style.transform = 'scale(0.8)';
                    previewDiv.innerHTML = `
                        <img src="${e.target.result}" alt="Preview ${i + 1}">
                        <button type="button" class="remove-additional" data-index="${i}">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                    
                    this.elements.additionalPreview.appendChild(previewDiv);
                    
                    // Efecto de aparición
                    setTimeout(() => {
                        previewDiv.style.transition = 'all 0.3s ease';
                        previewDiv.style.opacity = '1';
                        previewDiv.style.transform = 'scale(1)';
                    }, i * 100);

                    // Event listener para eliminar
                    previewDiv.querySelector('.remove-additional').addEventListener('click', (e) => {
                        this.removeAdditionalImage(e.target.closest('.remove-additional').dataset.index);
                    });
                };
                reader.readAsDataURL(processedFile);
            }

            this.showNotification(`${files.length} imágenes adicionales cargadas`, 'success');

        } catch (error) {
            console.error('Error procesando imágenes adicionales:', error);
            this.showNotification('Error al procesar las imágenes', 'error');
        }
    }

    validateImageFile(file, type) {
        const maxSize = 5 * 1024 * 1024; // 5MB
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];

        if (!allowedTypes.includes(file.type)) {
            this.showNotification(`Formato no válido: ${file.name}. Use JPG, PNG, GIF o WebP`, 'error');
            return false;
        }

        if (file.size > maxSize) {
            this.showNotification(`${file.name} supera los 5MB. Será comprimida automáticamente.`, 'warning');
        }

        return true;
    }

    async compressImage(file) {
        const maxSize = 5 * 1024 * 1024; // 5MB
        
        if (file.size <= maxSize) {
            return file;
        }

        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();

            img.onload = () => {
                // Calcular nuevas dimensiones manteniendo proporción
                const maxWidth = 1920;
                const maxHeight = 1080;
                let { width, height } = img;

                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width *= ratio;
                    height *= ratio;
                }

                canvas.width = width;
                canvas.height = height;

                // Dibujar imagen redimensionada
                ctx.drawImage(img, 0, 0, width, height);

                // Convertir a blob con calidad reducida
                canvas.toBlob((blob) => {
                    const compressedFile = new File([blob], file.name, {
                        type: file.type,
                        lastModified: Date.now()
                    });
                    resolve(compressedFile);
                }, file.type, 0.8);
            };

            img.src = URL.createObjectURL(file);
        });
    }

    removeMainImagePreview() {
        if (this.elements.imageInput && this.elements.imagePreview) {
            this.elements.imageInput.value = '';
            this.elements.imagePreview.style.opacity = '0';
            this.elements.imagePreview.style.transform = 'scale(0.8)';
            
            setTimeout(() => {
                this.elements.imagePreview.style.display = 'none';
                this.elements.imagePreview.style.opacity = '1';
                this.elements.imagePreview.style.transform = 'scale(1)';
            }, 300);
            
            this.uploadedFiles.main = null;
        }
    }

    removeAdditionalImage(index) {
        const preview = this.elements.additionalPreview.children[index];
        if (preview) {
            preview.style.opacity = '0';
            preview.style.transform = 'scale(0.8)';
            
            setTimeout(() => {
                preview.remove();
                this.uploadedFiles.additional.splice(index, 1);
                this.updateAdditionalImagesInput();
            }, 300);
        }
    }

    updateAdditionalImagesInput() {
        if (this.elements.additionalImagesInput) {
            const dt = new DataTransfer();
            this.uploadedFiles.additional.forEach(file => dt.items.add(file));
            this.elements.additionalImagesInput.files = dt.files;
        }
    }

    updateEpisodeOptions(season) {
        if (!this.elements.episodeSelect || !season) return;

        // Episodios por temporada según Game of Thrones
        const episodesBySession = {
            1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10, 7: 7, 8: 6
        };

        const maxEpisodes = episodesBySession[season] || 10;
        const currentValue = this.elements.episodeSelect.value;

        // Limpiar opciones
        this.elements.episodeSelect.innerHTML = '<option value="">Selecciona episodio</option>';

        // Agregar opciones válidas
        for (let i = 1; i <= maxEpisodes; i++) {
            const option = document.createElement('option');
            option.value = i;
            option.textContent = `Episodio ${i}`;
            if (currentValue == i) option.selected = true;
            this.elements.episodeSelect.appendChild(option);
        }

        // Efecto visual
        this.elements.episodeSelect.style.transform = 'scale(1.02)';
        setTimeout(() => {
            this.elements.episodeSelect.style.transform = 'scale(1)';
        }, 200);
    }

    setupMultiSelectSearch() {
        // Función para filtrar opciones en selects múltiples
        const searchableSelects = [this.elements.characterSelect, this.elements.houseSelect];

        searchableSelects.forEach(select => {
            if (!select) return;

            // Crear input de búsqueda
            const searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.placeholder = `Buscar ${select.id.includes('character') ? 'personajes' : 'casas'}...`;
            searchInput.className = 'form-input multi-search';
            searchInput.style.marginBottom = '0.5rem';

            select.parentNode.insertBefore(searchInput, select);

            searchInput.addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                const options = select.querySelectorAll('option');

                options.forEach(option => {
                    if (option.value === '') return; // Skip placeholder option
                    
                    const text = option.textContent.toLowerCase();
                    option.style.display = text.includes(searchTerm) ? 'block' : 'none';
                });
            });
        });
    }

    setupTooltips() {
        const tooltipElements = [
            { element: this.elements.importanceSelect, text: 'Rating de 1 a 5 según la importancia del evento en la historia' },
            { element: this.elements.characterSelect, text: 'Mantén Ctrl/Cmd para seleccionar múltiples personajes' },
            { element: this.elements.houseSelect, text: 'Mantén Ctrl/Cmd para seleccionar múltiples casas' }
        ];

        tooltipElements.forEach(({ element, text }) => {
            if (element) {
                element.setAttribute('data-tooltip', text);
                element.classList.add('tooltip');
            }
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + S para guardar
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                this.form.dispatchEvent(new Event('submit'));
            }

            // Escape para cancelar
            if (e.key === 'Escape') {
                if (confirm('¿Estás seguro de que quieres cancelar? Se perderán los cambios no guardados.')) {
                    window.history.back();
                }
            }
        });
    }

    setupUnsavedChangesWarning() {
        let hasUnsavedChanges = false;

        // Detectar cambios en el formulario
        const trackableElements = Object.values(this.elements).filter(el => 
            el && (el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA')
        );

        trackableElements.forEach(element => {
            element.addEventListener('input', () => {
                hasUnsavedChanges = true;
            });
        });

        // Warning al salir
        window.addEventListener('beforeunload', (e) => {
            if (hasUnsavedChanges) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        // Limpiar flag al enviar exitosamente
        this.form.addEventListener('submit', () => {
            hasUnsavedChanges = false;
        });
    }

    setupFocusEffects() {
        const inputs = this.form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.parentNode.classList.add('focused');
            });

            input.addEventListener('blur', () => {
                input.parentNode.classList.remove('focused');
            });
        });
    }

    setupAutoSave() {
        let autoSaveTimeout;
        const AUTOSAVE_DELAY = 30000; // 30 segundos

        const saveFormData = () => {
            const formData = new FormData(this.form);
            const data = Object.fromEntries(formData.entries());
            
            localStorage.setItem('eventFormDraft', JSON.stringify({
                data,
                timestamp: Date.now(),
                eventName: this.currentEventName
            }));

            this.showNotification('Borrador guardado automáticamente', 'info', 2000);
        };

        const trackableElements = Object.values(this.elements).filter(el => 
            el && (el.tagName === 'INPUT' || el.tagName === 'SELECT' || el.tagName === 'TEXTAREA')
        );

        trackableElements.forEach(element => {
            element.addEventListener('input', () => {
                clearTimeout(autoSaveTimeout);
                autoSaveTimeout = setTimeout(saveFormData, AUTOSAVE_DELAY);
            });
        });
    }

    initializeFormState() {
        // Restaurar borrador si existe
        this.restoreDraft();
        
        // Configurar estado inicial de episodios
        if (this.elements.seasonSelect && this.elements.seasonSelect.value) {
            this.updateEpisodeOptions(this.elements.seasonSelect.value);
        }

        // Validar campos que ya tienen valor (modo edición)
        if (this.isEditMode) {
            Object.values(this.elements).forEach(element => {
                if (element && element.value && element.tagName !== 'BUTTON') {
                    this.validateField(element);
                }
            });
        }
    }

    restoreDraft() {
        const draft = localStorage.getItem('eventFormDraft');
        if (draft && !this.isEditMode) {
            try {
                const { data, timestamp } = JSON.parse(draft);
                const ageInHours = (Date.now() - timestamp) / (1000 * 60 * 60);

                if (ageInHours < 24) { // Borrador válido por 24 horas
                    if (confirm('Se encontró un borrador guardado. ¿Deseas restaurarlo?')) {
                        Object.keys(data).forEach(key => {
                            const element = this.form.querySelector(`[name="${key}"]`);
                            if (element && data[key]) {
                                element.value = data[key];
                                this.validateField(element);
                            }
                        });
                        
                        this.showNotification('Borrador restaurado exitosamente', 'success');
                    }
                }
            } catch (error) {
                console.error('Error restaurando borrador:', error);
            }
        }
    }

    async handleFormSubmission(event) {
        event.preventDefault();

        // Validar formulario completo
        if (!this.validateCompleteForm()) {
            return false;
        }

        // Deshabilitar botón y mostrar loading
        this.setSubmitButtonState('loading');

        try {
            // Preparar FormData
            const formData = new FormData();
            
            // Agregar campos del formulario
            Object.values(this.elements).forEach(element => {
                if (element && element.name && element.type !== 'file') {
                    if (element.type === 'checkbox') {
                        if (element.checked) formData.append(element.name, element.value);
                    } else if (element.tagName === 'SELECT' && element.multiple) {
                        Array.from(element.selectedOptions).forEach(option => {
                            formData.append(element.name, option.value);
                        });
                    } else {
                        formData.append(element.name, element.value);
                    }
                }
            });

            // Agregar imágenes procesadas
            if (this.uploadedFiles.main) {
                formData.append('image', this.uploadedFiles.main);
            }

            this.uploadedFiles.additional.forEach((file, index) => {
                formData.append('additional_images', file);
            });

            // Enviar formulario
            const response = await fetch(this.form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                // Verificar si la respuesta tiene contenido JSON
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    try {
                        const result = await response.json();
                        
                        if (result.success) {
                            // Limpiar borrador
                            localStorage.removeItem('eventFormDraft');
                            
                            // Mostrar éxito
                            this.showNotification(
                                this.isEditMode ? 'Evento actualizado exitosamente' : 'Evento creado exitosamente',
                                'success'
                            );

                            // Redireccionar
                            setTimeout(() => {
                                window.location.href = result.redirect_url || '/events';
                            }, 1500);
                        } else {
                            throw new Error(result.message || 'Error al procesar el formulario');
                        }
                    } catch (jsonError) {
                        // Si hay error al parsear JSON pero la respuesta es exitosa, continuar
                        console.warn('Respuesta exitosa sin JSON válido, continuando...');
                        
                        // Limpiar borrador
                        localStorage.removeItem('eventFormDraft');
                        
                        // Mostrar éxito
                        this.showNotification(
                            this.isEditMode ? 'Evento actualizado exitosamente' : 'Evento creado exitosamente',
                            'success'
                        );

                        // Redireccionar después de un delay
                        setTimeout(() => {
                            window.location.href = '/events';
                        }, 1500);
                    }
                } else {
                    // Respuesta exitosa sin JSON (posible redirección HTML)
                    console.log('Respuesta exitosa sin JSON, continuando...');
                    
                    // Limpiar borrador
                    localStorage.removeItem('eventFormDraft');
                    
                    // Mostrar éxito
                    this.showNotification(
                        this.isEditMode ? 'Evento actualizado exitosamente' : 'Evento creado exitosamente',
                        'success'
                    );

                    // Redireccionar
                    setTimeout(() => {
                        window.location.href = '/events';
                    }, 1500);
                }
            } else {
                // Manejar errores HTTP
                let errorMessage = 'Error al guardar el evento';
                
                try {
                    const errorResult = await response.json();
                    errorMessage = errorResult.message || errorMessage;
                } catch {
                    errorMessage = `Error del servidor (${response.status})`;
                }
                
                throw new Error(errorMessage);
            }

        } catch (error) {
            console.error('Error enviando formulario:', error);
            
            let errorMessage = 'Error al guardar el evento';
            
            // Manejar diferentes tipos de errores
            if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
                errorMessage = 'Error de conexión. Verifica tu conexión a internet.';
            } else if (error.message) {
                errorMessage = error.message;
            }
            
            this.showNotification(errorMessage, 'error');
            this.setSubmitButtonState('normal');
        }
    }

    validateCompleteForm() {
        let isValid = true;
        const errors = [];

        // Validar todos los campos requeridos
        Object.keys(this.validationRules).forEach(fieldName => {
            const element = this.elements[fieldName + 'Input'] || 
                          this.elements[fieldName + 'Select'] || 
                          this.elements[fieldName + 'Textarea'] ||
                          this.form.querySelector(`[name="${fieldName}"]`);

            if (element && !this.validateField(element)) {
                isValid = false;
                errors.push(`${fieldName}: Campo inválido`);
            }
        });

        if (!isValid) {
            this.showNotification(`Formulario inválido:\n${errors.join('\n')}`, 'error');
            
            // Scroll al primer campo con error
            const firstError = this.form.querySelector('.invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        }

        return isValid;
    }

    setSubmitButtonState(state) {
        if (!this.elements.submitBtn) return;

        const btn = this.elements.submitBtn;
        const originalText = btn.dataset.originalText || btn.innerHTML;
        
        if (!btn.dataset.originalText) {
            btn.dataset.originalText = originalText;
        }

        switch (state) {
            case 'loading':
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
                btn.classList.add('loading');
                break;
            case 'success':
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-check"></i> ¡Éxito!';
                btn.classList.remove('loading');
                btn.classList.add('success');
                break;
            case 'normal':
            default:
                btn.disabled = false;
                btn.innerHTML = originalText;
                btn.classList.remove('loading', 'success');
                break;
        }
    }

    showNotification(message, type = 'info', duration = 4000) {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Estilos de la notificación
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: '10000',
            padding: '1rem 1.5rem',
            borderRadius: '10px',
            color: 'white',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1rem',
            minWidth: '300px',
            maxWidth: '500px',
            opacity: '0',
            transform: 'translateX(100%)',
            transition: 'all 0.3s ease',
            background: this.getNotificationColor(type),
            border: `2px solid ${this.getNotificationBorderColor(type)}`,
            backdropFilter: 'blur(10px)'
        });

        // Agregar al DOM
        document.body.appendChild(notification);

        // Animar entrada
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 50);

        // Auto-remover
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);

        return notification;
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    getNotificationColor(type) {
        const colors = {
            success: 'linear-gradient(135deg, #28a745, #20c997)',
            error: 'linear-gradient(135deg, #dc3545, #fd7e14)',
            warning: 'linear-gradient(135deg, #ffc107, #fd7e14)',
            info: 'linear-gradient(135deg, #17a2b8, #6f42c1)'
        };
        return colors[type] || colors.info;
    }

    getNotificationBorderColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        return colors[type] || colors.info;
    }
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🐉 Iniciando sistema épico de eventos...');
    
    try {
        window.eventFormManager = new EventFormManager();
    } catch (error) {
        console.error('Error inicializando EventFormManager:', error);
    }
});

// Funciones de utilidad globales
window.removeAdditionalImagePreview = function(button) {
    const preview = button.closest('.additional-image-preview');
    if (preview) {
        preview.style.opacity = '0';
        preview.style.transform = 'scale(0.8)';
        setTimeout(() => preview.remove(), 300);
    }
};

// Funciones de compatibilidad para el template existente
document.addEventListener('DOMContentLoaded', function() {
    // Get template data from HTML data attributes
    const formContainer = document.querySelector('.form-container');
    const isEditMode = formContainer.dataset.editMode === 'true';
    const currentEventName = formContainer.dataset.eventName || '';
    
    const form = document.getElementById('eventForm');
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
        
        if (count > 2000) {
            charCount.style.color = '#dc3545';
        } else if (count > 1600) {
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
            fetch(`/events/api/check-name?name=${encodeURIComponent(name)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.exists && (!isEditMode || name !== currentEventName)) {
                        feedback.textContent = 'Este nombre de evento ya está en uso';
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
        
        if (files.length > 4) {
            alert('Máximo 4 imágenes adicionales permitidas');
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
    form.addEventListener('submit', function(e) {
        const name = nameInput.value.trim();
        const season = document.getElementById('season').value;
        const episode = document.getElementById('episode').value;
        const importance = document.getElementById('importance_rating').value;
        const description = descTextarea.value.trim();
        
        let isValid = true;
        let errorMessage = '';
        
        if (name.length < 2) {
            errorMessage = 'El nombre del evento debe tener al menos 2 caracteres';
            isValid = false;
        } else if (!season) {
            errorMessage = 'Debes seleccionar una temporada';
            isValid = false;
        } else if (!episode) {
            errorMessage = 'Debes seleccionar un episodio';
            isValid = false;
        } else if (!importance) {
            errorMessage = 'Debes seleccionar un rating de importancia';
            isValid = false;
        } else if (description.length < 50) {
            errorMessage = 'La descripción debe tener al menos 50 caracteres';
            isValid = false;
        } else if (description.length > 2000) {
            errorMessage = 'La descripción no puede superar los 2000 caracteres';
            isValid = false;
        }
        
        if (!isValid) {
            e.preventDefault();
            alert(errorMessage);
            return false;
        }
        
        // Deshabilitar botón durante envío
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    });
});