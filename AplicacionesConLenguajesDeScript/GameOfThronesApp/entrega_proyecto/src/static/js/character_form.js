/**
 * Character Creation Form - Multi-Step Handler
 * Maneja la navegación, validación y envío del formulario de creación de personajes
 */

class CharacterCreationForm {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 3;
        this.formData = {};
        this.houses = [];
        
        this.init();
    }
    
    init() {
        this.setupElements();
        this.loadHouses();
        this.setupEventListeners();
        this.updateStepDisplay();
        this.setupValidation();
        this.initializeEditMode();
    }
    
    setupElements() {
        // Form elements
        this.form = document.getElementById('characterForm');
        this.steps = document.querySelectorAll('.form-step');
        this.stepIndicators = document.querySelectorAll('.step');
        this.progressFill = document.querySelector('.progress-fill');
        
        // Navigation buttons
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.submitBtn = document.getElementById('submitBtn');
        
        // Form inputs
        this.nameInput = document.getElementById('name');
        this.statusSelect = document.getElementById('status');
        this.houseSelect = document.getElementById('house_affiliation');
        this.descriptionTextarea = document.getElementById('description');
        this.imageInput = document.getElementById('image');
        
        // UI elements
        this.descCounter = document.getElementById('desc-count');
        this.nameValidation = document.getElementById('name-validation');
        this.imageUploadArea = document.getElementById('imageUploadArea');
        this.imagePreview = document.getElementById('image-preview');
        this.previewImg = document.getElementById('preview-img');
        this.removePreview = document.getElementById('removePreview');
        
        // Review elements
        this.reviewName = document.getElementById('review-name');
        this.reviewStatus = document.getElementById('review-status');
        this.reviewHouse = document.getElementById('review-house');
        this.reviewDescription = document.getElementById('review-description');
        this.reviewImage = document.getElementById('review-image');
        
        // Loading modal
        this.loadingModal = document.getElementById('loadingModal');
    }
    
    async loadHouses() {
        try {
            const response = await fetch('/api/houses');
            this.houses = await response.json();
        } catch (error) {
            console.error('Error loading houses:', error);
            this.showNotification('Error cargando las casas', 'error');
        }
    }
    
    setupEventListeners() {
        // Navigation buttons
        this.prevBtn.addEventListener('click', () => this.previousStep());
        this.nextBtn.addEventListener('click', () => this.nextStep());
        this.submitBtn.addEventListener('click', (e) => this.handleSubmit(e));
        
        // Step indicators (allow clicking)
        this.stepIndicators.forEach((step, index) => {
            step.addEventListener('click', () => {
                if (index + 1 <= this.currentStep || this.canNavigateToStep(index + 1)) {
                    this.goToStep(index + 1);
                }
            });
        });
        
        // Form inputs
        this.nameInput.addEventListener('input', () => this.validateName());
        this.statusSelect.addEventListener('change', () => this.validateStep1());
        this.houseSelect.addEventListener('change', () => this.validateStep1());
        this.descriptionTextarea.addEventListener('input', () => this.handleDescriptionChange());
        this.imageInput.addEventListener('change', (e) => this.handleImageChange(e));
        
        // Image upload area
        this.setupImageUpload();
        
        // Remove image preview
        this.removePreview.addEventListener('click', () => this.removeImagePreview());
        
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeyNavigation(e));
    }
    
    setupImageUpload() {
        // Drag and drop functionality
        this.imageUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.imageUploadArea.classList.add('dragover');
        });
        
        this.imageUploadArea.addEventListener('dragleave', () => {
            this.imageUploadArea.classList.remove('dragover');
        });
        
        this.imageUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.imageUploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleImageFile(files[0]);
            }
        });
        
        // Click to upload
        this.imageUploadArea.addEventListener('click', () => {
            this.imageInput.click();
        });
    }
    
    setupValidation() {
        // Real-time validation setup
        this.nameTimeout = null;
    }
    
    // === NAVIGATION METHODS ===
    
    nextStep() {
        if (this.validateCurrentStep()) {
            if (this.currentStep < this.totalSteps) {
                this.currentStep++;
                this.updateStepDisplay();
                this.updateReviewData();
            }
        }
    }
    
    previousStep() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.updateStepDisplay();
        }
    }
    
    goToStep(step) {
        if (step >= 1 && step <= this.totalSteps) {
            this.currentStep = step;
            this.updateStepDisplay();
            if (step === 3) {
                this.updateReviewData();
            }
        }
    }
    
    canNavigateToStep(step) {
        // Allow navigation to previous steps or next step if current is valid
        return step < this.currentStep || (step === this.currentStep + 1 && this.validateCurrentStep());
    }
    
    updateStepDisplay() {
        // Update step visibility
        this.steps.forEach((step, index) => {
            step.classList.toggle('active', index + 1 === this.currentStep);
        });
        
        // Update step indicators
        this.stepIndicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index + 1 === this.currentStep);
        });
        
        // Update progress bar
        const progressPercentage = (this.currentStep / this.totalSteps) * 100;
        this.progressFill.style.width = `${progressPercentage}%`;
        
        // Update navigation buttons
        this.prevBtn.style.display = this.currentStep > 1 ? 'flex' : 'none';
        this.nextBtn.style.display = this.currentStep < this.totalSteps ? 'flex' : 'none';
        this.submitBtn.style.display = this.currentStep === this.totalSteps ? 'flex' : 'none';
        
        // Update button text
        if (this.currentStep === this.totalSteps - 1) {
            this.nextBtn.innerHTML = '<i class="fas fa-eye"></i> Revisar';
        } else {
            this.nextBtn.innerHTML = 'Siguiente <i class="fas fa-arrow-right"></i>';
        }
        
        // Scroll to top of form
        document.querySelector('.creation-panel').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    // === VALIDATION METHODS ===
    
    validateCurrentStep() {
        switch (this.currentStep) {
            case 1:
                return this.validateStep1();
            case 2:
                return this.validateStep2();
            case 3:
                return true; // Review step doesn't need validation
            default:
                return false;
        }
    }
    
    validateStep1() {
        const name = this.nameInput.value.trim();
        const status = this.statusSelect.value;
        
        let isValid = true;
        let errors = [];
        
        // Validate name
        if (name.length < 2) {
            errors.push('El nombre debe tener al menos 2 caracteres');
            isValid = false;
        } else if (name.length > 100) {
            errors.push('El nombre no puede superar los 100 caracteres');
            isValid = false;
        }
        
        // Validate status
        if (!status) {
            errors.push('Debes seleccionar un estado');
            isValid = false;
        }
        
        // Show validation feedback
        this.showStepValidation(1, isValid, errors);
        
        return isValid;
    }
    
    validateStep2() {
        const description = this.descriptionTextarea.value.trim();
        
        let isValid = true;
        let errors = [];
        
        // Validate description
        if (description.length < 30) {
            errors.push('La descripción debe tener al menos 30 caracteres');
            isValid = false;
        } else if (description.length > 1500) {
            errors.push('La descripción no puede superar los 1500 caracteres');
            isValid = false;
        }
        
        // Show validation feedback
        this.showStepValidation(2, isValid, errors);
        
        return isValid;
    }
    
    async validateName() {
        const name = this.nameInput.value.trim();
        
        // Clear previous timeout
        if (this.nameTimeout) {
            clearTimeout(this.nameTimeout);
        }
        
        // Clear validation if name is too short
        if (name.length < 2) {
            this.nameValidation.textContent = '';
            this.nameValidation.className = 'validation-message';
            return;
        }
        
        // Set new timeout for API call
        this.nameTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`/api/characters/check-name?name=${encodeURIComponent(name)}`);
                const data = await response.json();
                
                if (data.exists) {
                    this.nameValidation.textContent = 'Este nombre ya está en uso';
                    this.nameValidation.className = 'validation-message error';
                } else {
                    this.nameValidation.textContent = 'Nombre disponible';
                    this.nameValidation.className = 'validation-message success';
                }
            } catch (error) {
                console.error('Error validating name:', error);
                this.nameValidation.textContent = '';
                this.nameValidation.className = 'validation-message';
            }
        }, 500);
    }
    
    showStepValidation(step, isValid, errors = []) {
        // This could be expanded to show step-specific validation
        if (!isValid && errors.length > 0) {
            this.showNotification(errors[0], 'error');
        }
    }
    
    // === INPUT HANDLERS ===
    
    handleDescriptionChange() {
        const description = this.descriptionTextarea.value;
        const count = description.length;
        
        // Update character counter
        this.descCounter.textContent = count;
        
        // Update counter color based on length
        if (count > 1500) {
            this.descCounter.style.color = '#ff6b6b';
        } else if (count > 1200) {
            this.descCounter.style.color = '#f59e0b';
        } else {
            this.descCounter.style.color = '#b8b8b8';
        }
        
        // Validate step 2 if we're on it
        if (this.currentStep === 2) {
            this.validateStep2();
        }
    }
    
    handleImageChange(e) {
        const file = e.target.files[0];
        if (file) {
            this.handleImageFile(file);
        }
    }
    
    handleImageFile(file) {
        // Validate file size
        if (file.size > 5 * 1024 * 1024) {
            this.showNotification('La imagen no puede superar los 5MB', 'error');
            this.imageInput.value = '';
            return;
        }
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showNotification('Solo se permiten archivos de imagen', 'error');
            this.imageInput.value = '';
            return;
        }
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            this.previewImg.src = e.target.result;
            this.imagePreview.style.display = 'block';
            this.imageUploadArea.style.display = 'none';
        };
        reader.readAsDataURL(file);
    }
    
    removeImagePreview() {
        this.imageInput.value = '';
        this.imagePreview.style.display = 'none';
        this.imageUploadArea.style.display = 'flex';
        this.previewImg.src = '';
    }
    
    // === REVIEW METHODS ===
    
    updateReviewData() {
        if (this.currentStep !== 3) return;
        
        // Update review information
        const name = this.nameInput.value.trim();
        const status = this.statusSelect.value;
        const houseId = this.houseSelect.value;
        const description = this.descriptionTextarea.value.trim();
        
        // Update review display
        this.reviewName.textContent = name || 'Sin nombre';
        this.reviewStatus.textContent = this.getStatusText(status);
        this.reviewHouse.textContent = this.getHouseText(houseId);
        this.reviewDescription.textContent = description || 'Sin descripción';
        
        // Update review image
        if (this.previewImg.src && this.previewImg.src !== window.location.href) {
            this.reviewImage.src = this.previewImg.src;
        } else {
            this.reviewImage.src = '/static/images/default-character.jpg';
        }
    }
    
    getStatusText(status) {
        const statusMap = {
            'Vivo': '🟢 Vivo',
            'Muerto': '🔴 Muerto',
            'Desconocido': '❓ Desconocido'
        };
        return statusMap[status] || 'Sin especificar';
    }
    
    getHouseText(houseId) {
        if (!houseId) return 'Sin afiliación';
        
        const house = this.houses.find(h => h.id === houseId);
        return house ? house.name : 'Casa no encontrada';
    }
    
    // === FORM SUBMISSION ===
    
    async handleSubmit(e) {
        e.preventDefault();
        
        // Final validation
        if (!this.validateStep1() || !this.validateStep2()) {
            this.showNotification('Por favor, completa todos los campos requeridos correctamente', 'error');
            return;
        }
        
        // Show loading
        this.showLoading(true);
        
        try {
            // Prepare form data
            const formData = new FormData(this.form);
            
            // Determine if we're editing or creating
            const isEditing = window.location.pathname.includes('/edit');
            const submitUrl = this.form.action || window.location.pathname;
            
            // Submit form
            const response = await fetch(submitUrl, {
                method: 'POST',
                body: formData
            });
            
            // Check if response is JSON or HTML
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                // Handle JSON response (for creation)
                const result = await response.json();
                
                if (result.success) {
                    const successMessage = (result.message && result.message.trim()) ? 
                        result.message : 
                        (isEditing ? '¡Personaje actualizado exitosamente!' : '¡Personaje creado exitosamente!');
                    
                    this.showNotification(successMessage, 'success');
                    
                    // Redirect to character detail or list
                    setTimeout(() => {
                        if (result.redirect) {
                            window.location.href = result.redirect;
                        } else if (result.character_id) {
                            window.location.href = `/characters/${result.character_id}`;
                        } else {
                            window.location.href = '/characters';
                        }
                    }, 1500);
                } else {
                    const errorMessage = (result.message && result.message.trim()) ? 
                        result.message : 
                        'Error al procesar el personaje';
                    throw new Error(errorMessage);
                }
            } else {
                // Handle HTML response (for editing - redirect)
                if (response.ok) {
                    this.showNotification('¡Personaje actualizado exitosamente!', 'success');
                    
                    // Follow the redirect
                    setTimeout(() => {
                        window.location.href = response.url || '/characters';
                    }, 1500);
                } else {
                    // Parse error from HTML if possible
                    const htmlText = await response.text();
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(htmlText, 'text/html');
                    const errorElement = doc.querySelector('.alert-danger, .error-message');
                    const errorMessage = (errorElement && errorElement.textContent.trim()) ? 
                        errorElement.textContent.trim() : 
                        'Error al procesar el personaje';
                    throw new Error(errorMessage);
                }
            }
            
        } catch (error) {
            console.error('Submission error:', error);
            const errorMessage = (error.message && error.message.trim()) ? 
                error.message : 
                'Error inesperado al procesar el personaje';
            this.showNotification(errorMessage, 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    initializeEditMode() {
        // Check if we're in edit mode
        const isEditing = window.location.pathname.includes('/edit');
        
        if (isEditing) {
            // Initialize image preview if there's a current image
            const currentImageDiv = document.querySelector('.current-image-preview');
            if (currentImageDiv) {
                const currentImg = currentImageDiv.querySelector('.current-image');
                if (currentImg && currentImg.src) {
                    // Set the preview image for the review section
                    if (this.reviewImage) {
                        this.reviewImage.src = currentImg.src;
                    }
                }
            }
            
            // Update character counter for existing description
            if (this.descriptionTextarea && this.descCounter) {
                const count = this.descriptionTextarea.value.length;
                this.descCounter.textContent = count;
                this.updateCounterColor(count);
            }
            
            // Update review data with existing information
            this.updateReviewData();
        }
    }
    
    updateCounterColor(count) {
        if (count > 1500) {
            this.descCounter.style.color = '#ff6b6b';
        } else if (count > 1200) {
            this.descCounter.style.color = '#f59e0b';
        } else {
            this.descCounter.style.color = '#b8b8b8';
        }
    }
    
    // === UTILITY METHODS ===
    
    handleKeyNavigation(e) {
        // Allow navigation with arrow keys
        if (e.ctrlKey || e.metaKey) {
            if (e.key === 'ArrowLeft' && this.currentStep > 1) {
                e.preventDefault();
                this.previousStep();
            } else if (e.key === 'ArrowRight' && this.currentStep < this.totalSteps) {
                e.preventDefault();
                this.nextStep();
            }
        }
    }
    
    showLoading(show) {
        if (show) {
            this.loadingModal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        } else {
            this.loadingModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
    
    showNotification(message, type = 'info') {
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
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }
    
    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CharacterCreationForm();
});

// Add notification styles if not already present
if (!document.querySelector('#notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(20, 20, 20, 0.95);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transform: translateX(400px);
            transition: all 0.3s ease;
            z-index: 10000;
            max-width: 400px;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }
        
        .notification-success {
            border-left: 4px solid #22c55e;
        }
        
        .notification-error {
            border-left: 4px solid #ef4444;
        }
        
        .notification-warning {
            border-left: 4px solid #f59e0b;
        }
        
        .notification-info {
            border-left: 4px solid #3b82f6;
        }
        
        .notification i {
            font-size: 1.2rem;
        }
        
        .notification-success i {
            color: #22c55e;
        }
        
        .notification-error i {
            color: #ef4444;
        }
        
        .notification-warning i {
            color: #f59e0b;
        }
        
        .notification-info i {
            color: #3b82f6;
        }
    `;
    document.head.appendChild(style);
}