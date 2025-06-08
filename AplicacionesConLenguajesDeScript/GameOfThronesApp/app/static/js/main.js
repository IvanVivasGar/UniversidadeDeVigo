// ===== MAIN JAVASCRIPT FUNCTIONS =====

// Variables globales
let notifications = [];

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', function() {
    initializeNavbar();
    initializeAnimations();
    initializeFormValidations();
    initializeNotifications();
    initializeEpicFooter(); // Nueva función del footer
    initializeFooterScrollEffects();
    initializeSocialLinks();
});

// ===== NAVBAR FUNCTIONALITY =====
function initializeNavbar() {
    const navbar = document.querySelector('.navbar');
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const navAuth = document.querySelector('.nav-auth');
    
    // Crear el botón toggle móvil si no existe
    if (!navToggle && window.innerWidth <= 768) {
        createMobileToggle();
    }
    
    // Funcionalidad del toggle móvil
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            navMenu.classList.toggle('active');
            navAuth.classList.toggle('active');
            
            // Prevenir scroll del body cuando el menú está abierto
            document.body.style.overflow = this.classList.contains('active') ? 'hidden' : '';
        });
    }
    
    // Cerrar menú móvil al hacer clic en un enlace
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (navToggle && navToggle.classList.contains('active')) {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
                navAuth.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });
    
    // Efecto de scroll en el navbar
    let lastScrollTop = 0;
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Agregar clase 'scrolled' cuando se hace scroll
        if (scrollTop > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        
        lastScrollTop = scrollTop;
    });
    
    // Cerrar menú móvil al redimensionar ventana
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            if (navToggle) {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
                navAuth.classList.remove('active');
                document.body.style.overflow = '';
            }
        } else if (!navToggle) {
            createMobileToggle();
        }
    });
    
    // Cerrar menú móvil al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (navToggle && navToggle.classList.contains('active')) {
            if (!navbar.contains(e.target)) {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
                navAuth.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    });
}

function createMobileToggle() {
    const navContainer = document.querySelector('.nav-container');
    const navAuth = document.querySelector('.nav-auth');
    
    if (!navContainer || document.querySelector('.nav-toggle')) return;
    
    const toggle = document.createElement('button');
    toggle.className = 'nav-toggle';
    toggle.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    
    // Insertar el toggle antes de nav-auth
    navContainer.insertBefore(toggle, navAuth);
    
    // Reinicializar la funcionalidad
    initializeNavbar();
}

// ===== ANIMATIONS =====
function initializeAnimations() {
    // Animaciones de entrada para elementos
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observar elementos animables
    document.querySelectorAll('.quick-access-card, .entity-card, .section-title').forEach(el => {
        observer.observe(el);
    });
    
    // Parallax suave para hero
    const hero = document.querySelector('.hero-section');
    if (hero) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            hero.style.transform = `translateY(${rate}px)`;
        });
    }
}

// ===== NOTIFICATIONS SYSTEM =====
function showNotification(message, type = 'info', duration = 5000) {
    const notificationId = Date.now();
    const notification = createNotificationElement(message, type, notificationId);
    
    // Agregar al contenedor
    let container = document.querySelector('.flash-messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Auto-eliminar
    setTimeout(() => {
        removeNotification(notificationId);
    }, duration);
    
    return notificationId;
}

function createNotificationElement(message, type, id) {
    const notification = document.createElement('div');
    notification.className = `flash-message flash-${type}`;
    notification.dataset.id = id;
    
    const icon = getNotificationIcon(type);
    
    notification.innerHTML = `
        <div class="notification-content">
            <i class="${icon}"></i>
            <span>${message}</span>
        </div>
        <button class="flash-close" onclick="removeNotification(${id})">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    return notification;
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'fas fa-check-circle';
        case 'error': return 'fas fa-exclamation-circle';
        case 'warning': return 'fas fa-exclamation-triangle';
        case 'info': return 'fas fa-info-circle';
        default: return 'fas fa-info-circle';
    }
}

function removeNotification(id) {
    const notification = document.querySelector(`[data-id="${id}"]`);
    if (notification) {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }
}

function initializeNotifications() {
    // Agregar estilos para animaciones de notificaciones
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOut {
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .flash-message.show {
            animation: slideIn 0.3s ease forwards;
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .navbar.scrolled {
            background: rgba(15, 15, 15, 0.98);
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
        }
        
        .animate-in {
            animation: fadeInUp 0.6s ease forwards;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// ===== SEARCH FUNCTIONALITY =====
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            const section = this.dataset.section;
            
            searchTimeout = setTimeout(() => {
                performSearch(query, section);
            }, 300);
        });
    });
}

async function performSearch(query, section) {
    const container = document.querySelector(`#${section}-results`);
    if (!container) return;
    
    try {
        // Mostrar loading
        container.innerHTML = '<div class="loading-spinner"><i class="fas fa-spinner fa-spin"></i></div>';
        
        const response = await fetch(`/search/${section}?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            renderSearchResults(data.results, container, section);
        } else {
            container.innerHTML = '<div class="no-results">No se encontraron resultados</div>';
        }
    } catch (error) {
        console.error('Error en búsqueda:', error);
        container.innerHTML = '<div class="error-message">Error al buscar. Inténtalo de nuevo.</div>';
    }
}

function renderSearchResults(results, container, section) {
    if (results.length === 0) {
        container.innerHTML = '<div class="no-results">No se encontraron resultados</div>';
        return;
    }
    
    const html = results.map(item => {
        switch(section) {
            case 'characters':
                return renderCharacterCard(item);
            case 'houses':
                return renderHouseCard(item);
            case 'events':
                return renderEventCard(item);
            case 'posts':
                return renderPostCard(item);
            default:
                return '';
        }
    }).join('');
    
    container.innerHTML = html;
}

// ===== RATING SYSTEM =====
function initializeRatings() {
    document.querySelectorAll('.rating-input').forEach(ratingContainer => {
        const stars = ratingContainer.querySelectorAll('.star');
        const input = ratingContainer.querySelector('input[type="hidden"]');
        
        stars.forEach((star, index) => {
            star.addEventListener('click', function() {
                const rating = index + 1;
                input.value = rating;
                updateStarDisplay(stars, rating);
                submitRating(ratingContainer.dataset.entityId, ratingContainer.dataset.entityType, rating);
            });
            
            star.addEventListener('mouseenter', function() {
                updateStarDisplay(stars, index + 1);
            });
        });
        
        ratingContainer.addEventListener('mouseleave', function() {
            updateStarDisplay(stars, input.value || 0);
        });
    });
}

function updateStarDisplay(stars, rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

async function submitRating(entityId, entityType, rating) {
    try {
        const response = await fetch('/api/rate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                entity_id: entityId,
                entity_type: entityType,
                rating: rating
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('¡Calificación guardada!', 'success');
            updateAverageRating(entityId, data.new_average);
        } else {
            showNotification(data.message || 'Error al guardar calificación', 'error');
        }
    } catch (error) {
        showNotification('Error de conexión', 'error');
    }
}

function updateAverageRating(entityId, newAverage) {
    const avgElement = document.querySelector(`[data-entity-id="${entityId}"] .average-rating`);
    if (avgElement) {
        avgElement.textContent = `(${newAverage.toFixed(1)})`;
    }
}

// ===== FORM VALIDATION =====
function initializeFormValidations() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => clearFieldError(input));
        });
        
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    const rules = field.dataset.rules ? field.dataset.rules.split('|') : [];
    let isValid = true;
    let errorMessage = '';
    
    // Validación required
    if (rules.includes('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo es obligatorio';
    }
    
    // Validación email
    if (rules.includes('email') && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Formato de email inválido';
        }
    }
    
    // Validación min length
    const minLength = rules.find(rule => rule.startsWith('min:'));
    if (minLength && value) {
        const min = parseInt(minLength.split(':')[1]);
        if (value.length < min) {
            isValid = false;
            errorMessage = `Mínimo ${min} caracteres`;
        }
    }
    
    // Mostrar/ocultar error
    showFieldValidation(field, isValid, errorMessage);
    return isValid;
}

function showFieldValidation(field, isValid, message) {
    const errorElement = field.parentNode.querySelector('.field-error');
    
    if (!isValid) {
        field.classList.add('invalid');
        field.classList.remove('valid');
        
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
    } else {
        field.classList.remove('invalid');
        field.classList.add('valid');
        
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
}

function clearFieldError(field) {
    field.classList.remove('invalid');
    const errorElement = field.parentNode.querySelector('.field-error');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

function validateForm(form) {
    const fields = form.querySelectorAll('input[data-rules], textarea[data-rules], select[data-rules]');
    let isFormValid = true;
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isFormValid = false;
        }
    });
    
    return isFormValid;
}

// ===== FOOTER ÉPICO FUNCTIONALITY =====
function initializeEpicFooter() {
    initializeFooterQuotes();
    initializeFooterStats();
    initializeFooterSymbols();
    initializeFooterParticles();
}

// Función para rotar las citas épicas del footer
function initializeFooterQuotes() {
    const quotes = [
        {
            text: "When you play the game of thrones, you win or you die.",
            author: "Cersei Lannister"
        },
        {
            text: "Winter is coming.",
            author: "House Stark"
        },
        {
            text: "A Lannister always pays his debts.",
            author: "House Lannister"
        },
        {
            text: "Fire and Blood.",
            author: "House Targaryen"
        },
        {
            text: "The night is dark and full of terrors.",
            author: "Melisandre"
        },
        {
            text: "Valar Morghulis - All men must die.",
            author: "Faceless Men"
        },
        {
            text: "A mind needs books as a sword needs a whetstone.",
            author: "Tyrion Lannister"
        }
    ];

    const quotesContainer = document.querySelector('.footer-quotes');
    if (!quotesContainer) return;

    // Crear las cartas de citas
    quotes.forEach((quote, index) => {
        const quoteCard = document.createElement('div');
        quoteCard.className = `quote-card ${index === 0 ? 'active' : ''}`;
        quoteCard.innerHTML = `
            <div class="quote-text">"${quote.text}"</div>
            <div class="quote-author">— ${quote.author}</div>
        `;
        quotesContainer.appendChild(quoteCard);
    });

    // Rotar citas cada 4 segundos
    let currentQuote = 0;
    setInterval(() => {
        const cards = quotesContainer.querySelectorAll('.quote-card');
        cards[currentQuote].classList.remove('active');
        
        currentQuote = (currentQuote + 1) % quotes.length;
        cards[currentQuote].classList.add('active');
    }, 4000);
}

// Animar las estadísticas del footer
function initializeFooterStats() {
    const statNumbers = document.querySelectorAll('.footer-stat .stat-number');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateStatNumber(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(stat => {
        observer.observe(stat);
    });
}

function animateStatNumber(element) {
    const finalValue = parseInt(element.textContent);
    const duration = 2000; // 2 segundos
    const steps = 60;
    const increment = finalValue / steps;
    const stepDuration = duration / steps;
    
    let currentValue = 0;
    
    const timer = setInterval(() => {
        currentValue += increment;
        
        if (currentValue >= finalValue) {
            currentValue = finalValue;
            clearInterval(timer);
        }
        
        element.textContent = Math.floor(currentValue);
    }, stepDuration);
}

// Efectos interactivos para los símbolos de las casas
function initializeFooterSymbols() {
    const symbols = document.querySelectorAll('.symbol-item');
    const houseInfo = {
        '🐺': { name: 'House Stark', motto: 'Winter is Coming' },
        '🦁': { name: 'House Lannister', motto: 'Hear Me Roar' },
        '🐉': { name: 'House Targaryen', motto: 'Fire and Blood' },
        '🌹': { name: 'House Tyrell', motto: 'Growing Strong' },
        '🦅': { name: 'House Arryn', motto: 'As High as Honor' },
        '🐙': { name: 'House Greyjoy', motto: 'We Do Not Sow' },
        '🔥': { name: 'R\'hllor', motto: 'The Night is Dark and Full of Terrors' }
    };

    symbols.forEach(symbol => {
        symbol.addEventListener('mouseenter', function() {
            const emoji = this.textContent.trim();
            const info = houseInfo[emoji];
            
            if (info) {
                showHouseTooltip(this, info);
            }
        });

        symbol.addEventListener('mouseleave', function() {
            hideHouseTooltip();
        });

        symbol.addEventListener('click', function() {
            const emoji = this.textContent.trim();
            const info = houseInfo[emoji];
            
            if (info) {
                showNotification(`${info.name}: "${info.motto}"`, 'info', 3000);
            }
        });
    });
}

function showHouseTooltip(element, info) {
    // Remover tooltip existente
    hideHouseTooltip();
    
    const tooltip = document.createElement('div');
    tooltip.className = 'house-tooltip';
    tooltip.innerHTML = `
        <div class="tooltip-title">${info.name}</div>
        <div class="tooltip-motto">"${info.motto}"</div>
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.position = 'fixed';
    tooltip.style.left = rect.left + rect.width / 2 + 'px';
    tooltip.style.top = rect.top - 10 + 'px';
    tooltip.style.transform = 'translate(-50%, -100%)';
    tooltip.style.zIndex = '10000';
    
    // Estilos del tooltip
    tooltip.style.background = 'rgba(0, 0, 0, 0.9)';
    tooltip.style.color = '#ffd700';
    tooltip.style.padding = '0.8rem 1rem';
    tooltip.style.borderRadius = '8px';
    tooltip.style.fontSize = '0.9rem';
    tooltip.style.border = '1px solid #ffd700';
    tooltip.style.boxShadow = '0 0 20px rgba(255, 215, 0, 0.3)';
    tooltip.style.opacity = '0';
    tooltip.style.transition = 'opacity 0.3s ease';
    
    // Animar entrada
    setTimeout(() => {
        tooltip.style.opacity = '1';
    }, 10);
}

function hideHouseTooltip() {
    const tooltip = document.querySelector('.house-tooltip');
    if (tooltip) {
        tooltip.style.opacity = '0';
        setTimeout(() => {
            tooltip.remove();
        }, 300);
    }
}

// Sistema de partículas mejorado para el footer
function initializeFooterParticles() {
    const particlesContainer = document.querySelector('.footer-particles');
    if (!particlesContainer) return;

    // Crear partículas de fuego
    for (let i = 0; i < 5; i++) {
        const ember = document.createElement('div');
        ember.className = 'footer-ember';
        particlesContainer.appendChild(ember);
    }

    // Efecto de hover en el footer para más partículas
    const footer = document.querySelector('.footer-epic');
    if (footer) {
        footer.addEventListener('mouseenter', () => {
            createTemporaryEmbers();
        });
    }
}

function createTemporaryEmbers() {
    const particlesContainer = document.querySelector('.footer-particles');
    if (!particlesContainer) return;

    for (let i = 0; i < 3; i++) {
        const ember = document.createElement('div');
        ember.className = 'footer-ember temporary';
        ember.style.left = Math.random() * 100 + '%';
        ember.style.top = Math.random() * 100 + '%';
        ember.style.animationDuration = (Math.random() * 3 + 2) + 's';
        
        particlesContainer.appendChild(ember);
        
        // Remover después de la animación
        setTimeout(() => {
            ember.remove();
        }, 5000);
    }
}

// Efectos de scroll para el footer
function initializeFooterScrollEffects() {
    const footer = document.querySelector('.footer-epic');
    if (!footer) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                footer.classList.add('footer-visible');
                triggerFooterAnimations();
            }
        });
    }, { threshold: 0.1 });

    observer.observe(footer);
}

function triggerFooterAnimations() {
    // Animar dragones
    const dragons = document.querySelectorAll('.dragon-footer-left, .dragon-footer-right');
    dragons.forEach((dragon, index) => {
        setTimeout(() => {
            dragon.style.animation = `dragonFloat 12s ease-in-out infinite ${index === 1 ? 'reverse' : ''}`;
        }, index * 500);
    });

    // Animar secciones del footer
    const sections = document.querySelectorAll('.footer-section');
    sections.forEach((section, index) => {
        setTimeout(() => {
            section.style.animation = 'fadeInUp 0.6s ease forwards';
        }, index * 200);
    });
}

// Funcionalidad para las redes sociales
function initializeSocialLinks() {
    const socialLinks = document.querySelectorAll('.social-link');
    
    socialLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const platform = this.querySelector('i').className;
            let message = '';
            
            if (platform.includes('facebook')) {
                message = '¡Síguenos en Facebook para más contenido épico!';
            } else if (platform.includes('twitter')) {
                message = '¡Síguenos en Twitter para actualizaciones!';
            } else if (platform.includes('instagram')) {
                message = '¡Síguenos en Instagram para imágenes épicas!';
            } else if (platform.includes('youtube')) {
                message = '¡Suscríbete a nuestro canal de YouTube!';
            } else {
                message = '¡Próximamente disponible!';
            }
            
            showNotification(message, 'info', 3000);
        });
    });
}

// ===== MODAL FUNCTIONALITY =====
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        
        // Agregar listener para cerrar con ESC
        document.addEventListener('keydown', closeModalOnEsc);
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }, 300);
        
        // Remover listener de ESC
        document.removeEventListener('keydown', closeModalOnEsc);
    }
}

function closeModalOnEsc(e) {
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            closeModal(modal.id);
        });
    }
}

// Cerrar modal al hacer clic en el fondo
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        closeModal(e.target.id);
    }
});

// ===== EXPORT FUNCTIONS =====
window.showNotification = showNotification;
window.removeNotification = removeNotification;
window.openModal = openModal;
window.closeModal = closeModal;