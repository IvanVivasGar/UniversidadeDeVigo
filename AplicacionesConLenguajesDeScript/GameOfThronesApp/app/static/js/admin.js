// Admin functionality for WesterosTracker
class AdminManager {
    constructor() {
        this.init();
    }

    init() {
        this.attachDeleteListeners();
        this.attachAdminToggleListeners();
    }

    // Attach event listeners to delete buttons
    attachDeleteListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.admin-delete-btn, .admin-delete-btn *')) {
                e.preventDefault();
                e.stopPropagation();
                
                const button = e.target.closest('.admin-delete-btn');
                if (button && !button.classList.contains('loading')) {
                    this.handleDelete(button);
                }
            }
        });
    }

    // Attach event listeners for admin toggle buttons
    attachAdminToggleListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.admin-make-admin-btn, .admin-make-admin-btn *')) {
                e.preventDefault();
                e.stopPropagation();
                
                const button = e.target.closest('.admin-make-admin-btn');
                if (button && !button.classList.contains('loading')) {
                    this.handleMakeAdmin(button);
                }
            }
            
            if (e.target.matches('.admin-remove-admin-btn, .admin-remove-admin-btn *')) {
                e.preventDefault();
                e.stopPropagation();
                
                const button = e.target.closest('.admin-remove-admin-btn');
                if (button && !button.classList.contains('loading')) {
                    this.handleRemoveAdmin(button);
                }
            }
        });
    }

    // Handle delete action
    handleDelete(button) {
        const entityType = button.dataset.entityType;
        const entityId = button.dataset.entityId;
        const entityName = button.dataset.entityName || 'este elemento';

        this.showConfirmModal(
            '🗡️ Confirmar Eliminación',
            `¿Estás seguro de que quieres eliminar "${entityName}" del reino? Esta acción no se puede deshacer.`,
            () => this.performDelete(button, entityType, entityId, entityName),
            () => console.log('Eliminación cancelada')
        );
    }

    // Handle make admin action
    handleMakeAdmin(button) {
        const userId = button.dataset.userId;
        const username = button.dataset.username || 'este usuario';

        this.showConfirmModal(
            '👑 Otorgar Poder Real',
            `¿Confirmas que quieres otorgar privilegios de administrador a "${username}"?`,
            () => this.performAdminToggle(button, userId, 'make-admin', username),
            () => console.log('Acción cancelada')
        );
    }

    // Handle remove admin action
    handleRemoveAdmin(button) {
        const userId = button.dataset.userId;
        const username = button.dataset.username || 'este usuario';

        this.showConfirmModal(
            '⚔️ Revocar Poder Real',
            `¿Confirmas que quieres remover los privilegios de administrador de "${username}"?`,
            () => this.performAdminToggle(button, userId, 'remove-admin', username),
            () => console.log('Acción cancelada')
        );
    }

    // Perform the actual delete operation
    async performDelete(button, entityType, entityId, entityName) {
        button.classList.add('loading');
        const originalIcon = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            const response = await fetch(`/admin/delete/${entityType}/${entityId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'  // Incluir cookies de sesión
            });

            // Verificar si la respuesta es una redirección a login
            if (response.status === 302 || response.url.includes('/auth/login')) {
                this.showNotification('Sesión expirada. Por favor, inicia sesión nuevamente.', 'error');
                setTimeout(() => {
                    window.location.href = '/auth/login';
                }, 2000);
                return;
            }

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                
                // Remove the element from the DOM with animation
                const cardElement = button.closest('.card, .character-card, .house-card, .event-card, .discussion-card, .post, .showcase-card, .access-card');
                if (cardElement) {
                    cardElement.style.transition = 'all 0.5s ease';
                    cardElement.style.transform = 'scale(0)';
                    cardElement.style.opacity = '0';
                    
                    setTimeout(() => {
                        cardElement.remove();
                    }, 500);
                }
            } else {
                this.showNotification(data.message || 'Error al eliminar el elemento', 'error');
                button.classList.remove('loading');
                button.innerHTML = originalIcon;
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Error de conexión. Inténtalo de nuevo.', 'error');
            button.classList.remove('loading');
            button.innerHTML = originalIcon;
        }
    }

    // Perform admin toggle operation
    async performAdminToggle(button, userId, action, username) {
        button.classList.add('loading');
        const originalText = button.textContent;
        button.textContent = 'Procesando...';

        try {
            const response = await fetch(`/admin/${action}/${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'  // Incluir cookies de sesión
            });

            // Verificar si la respuesta es una redirección a login
            if (response.status === 302 || response.url.includes('/auth/login')) {
                this.showNotification('Sesión expirada. Por favor, inicia sesión nuevamente.', 'error');
                setTimeout(() => {
                    window.location.href = '/auth/login';
                }, 2000);
                return;
            }

            const data = await response.json();

            if (data.success) {
                this.showNotification(data.message, 'success');
                
                // Refresh the page to reflect changes
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                this.showNotification(data.message || 'Error al cambiar privilegios', 'error');
                button.classList.remove('loading');
                button.textContent = originalText;
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Error de conexión. Inténtalo de nuevo.', 'error');
            button.classList.remove('loading');
            button.textContent = originalText;
        }
    }

    // Show confirmation modal
    showConfirmModal(title, message, onConfirm, onCancel) {
        // Remove existing modal if any
        const existingModal = document.querySelector('.admin-modal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create modal
        const modal = document.createElement('div');
        modal.className = 'admin-modal';
        modal.innerHTML = `
            <div class="admin-modal-content">
                <h3>${title}</h3>
                <p>${message}</p>
                <div class="admin-modal-actions">
                    <button class="admin-modal-btn cancel">
                        <i class="fas fa-times"></i>
                        Cancelar
                    </button>
                    <button class="admin-modal-btn confirm">
                        <i class="fas fa-check"></i>
                        Confirmar
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Show modal with animation
        setTimeout(() => {
            modal.classList.add('show');
        }, 10);

        // Handle modal actions
        const confirmBtn = modal.querySelector('.confirm');
        const cancelBtn = modal.querySelector('.cancel');

        confirmBtn.addEventListener('click', () => {
            this.closeModal(modal);
            if (onConfirm) onConfirm();
        });

        cancelBtn.addEventListener('click', () => {
            this.closeModal(modal);
            if (onCancel) onCancel();
        });

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
                if (onCancel) onCancel();
            }
        });

        // Close on Escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                this.closeModal(modal);
                if (onCancel) onCancel();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }

    // Close modal
    closeModal(modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 300);
    }

    // Show notification
    showNotification(message, type = 'info') {
        // Use existing notification system if available
        if (window.showNotification) {
            window.showNotification(message, type);
            return;
        }

        // Fallback notification system
        const notification = document.createElement('div');
        notification.className = `admin-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '100px',
            right: '20px',
            zIndex: '10000',
            background: type === 'success' ? 'rgba(40, 167, 69, 0.9)' : 
                       type === 'error' ? 'rgba(139, 0, 0, 0.9)' : 'rgba(255, 215, 0, 0.9)',
            color: 'white',
            padding: '1rem 1.5rem',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
            transform: 'translateX(100%)',
            transition: 'transform 0.3s ease',
            maxWidth: '400px',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem'
        });

        document.body.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    // Create delete button for any entity
    static createDeleteButton(entityType, entityId, entityName) {
        return `
            <div class="admin-controls">
                <button class="admin-delete-btn" 
                        data-entity-type="${entityType}" 
                        data-entity-id="${entityId}" 
                        data-entity-name="${entityName}"
                        title="Eliminar ${entityName}">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </div>
        `;
    }

    // Create admin badge
    static createAdminBadge() {
        return `<span class="admin-badge"><i class="fas fa-crown"></i>Admin</span>`;
    }

    // Create admin toggle buttons for users
    static createAdminToggleButtons(userId, username, isAdmin) {
        if (isAdmin) {
            return `
                <button class="admin-remove-admin-btn btn btn-outline-danger btn-sm" 
                        data-user-id="${userId}" 
                        data-username="${username}"
                        title="Remover privilegios de administrador">
                    <i class="fas fa-user-minus"></i>
                    Quitar Admin
                </button>
            `;
        } else {
            return `
                <button class="admin-make-admin-btn btn btn-outline-warning btn-sm" 
                        data-user-id="${userId}" 
                        data-username="${username}"
                        title="Otorgar privilegios de administrador">
                    <i class="fas fa-crown"></i>
                    Hacer Admin
                </button>
            `;
        }
    }
}

// Initialize admin manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if user is admin
    if (window.currentUserIsAdmin) {
        window.adminManager = new AdminManager();
        console.log('🛡️ Sistema de administración iniciado');
    }
});

// Global helper functions
window.AdminManager = AdminManager;