// Dashboard JavaScript

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all dashboard components
    initializeChart();
    initializeDropdowns();
    initializeMobileMenu();
    initializeNotifications();
    updateRealTimeData();
    
    // Set up real-time updates
    setInterval(updateRealTimeData, 30000); // Update every 30 seconds
});

// Chart Initialization
function initializeChart() {
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;

    const chartData = {
        labels: ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
        datasets: [{
            label: 'Fee Collection',
            data: [65400, 72800, 68200, 85400, 78600, 85400],
            borderColor: '#214888',
            backgroundColor: 'rgba(33, 72, 136, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointRadius: 6,
            pointBackgroundColor: '#214888',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointHoverRadius: 8
        }, {
            label: 'Expenses',
            data: [45200, 48600, 42800, 52300, 49800, 51200],
            borderColor: '#D54395',
            backgroundColor: 'rgba(213, 67, 149, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            pointRadius: 6,
            pointBackgroundColor: '#D54395',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointHoverRadius: 8
        }]
    };

    const config = {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            family: 'Poppins',
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleFont: {
                        family: 'Poppins',
                        size: 14,
                        weight: '600'
                    },
                    bodyFont: {
                        family: 'Poppins',
                        size: 12
                    },
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ₹${context.parsed.y.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            family: 'Poppins',
                            size: 12
                        },
                        color: '#453F4E'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: 'Poppins',
                            size: 12
                        },
                        color: '#453F4E',
                        callback: function(value) {
                            return '₹' + (value / 1000) + 'K';
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            elements: {
                point: {
                    hoverRadius: 8
                }
            }
        }
    };

    new Chart(ctx, config);
}

// Dropdown Functionality
function initializeDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (!toggle || !menu) return;
        
        // Toggle dropdown on click
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Close other dropdowns
            closeAllDropdowns();
            
            // Toggle current dropdown
            dropdown.classList.toggle('active');
            menu.style.opacity = dropdown.classList.contains('active') ? '1' : '0';
            menu.style.visibility = dropdown.classList.contains('active') ? 'visible' : 'hidden';
            menu.style.transform = dropdown.classList.contains('active') ? 'translateY(0)' : 'translateY(-10px)';
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
                menu.style.opacity = '0';
                menu.style.visibility = 'hidden';
                menu.style.transform = 'translateY(-10px)';
            }
        });
    });
}

function closeAllDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const menu = dropdown.querySelector('.dropdown-menu');
        dropdown.classList.remove('active');
        if (menu) {
            menu.style.opacity = '0';
            menu.style.visibility = 'hidden';
            menu.style.transform = 'translateY(-10px)';
        }
    });
}

// Mobile Menu Functionality - Fixed
function initializeMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            navMenu.classList.toggle('mobile-active');
            const icon = mobileToggle.querySelector('i');
            
            if (navMenu.classList.contains('mobile-active')) {
                icon.className = 'fas fa-times';
                document.body.style.overflow = 'hidden';
            } else {
                icon.className = 'fas fa-bars';
                document.body.style.overflow = '';
            }
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!mobileToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('mobile-active');
                const icon = mobileToggle.querySelector('i');
                icon.className = 'fas fa-bars';
                document.body.style.overflow = '';
            }
        });
        
        // Close mobile menu on window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                navMenu.classList.remove('mobile-active');
                const icon = mobileToggle.querySelector('i');
                icon.className = 'fas fa-bars';
                document.body.style.overflow = '';
            }
        });
    }
}

// Notification System
function initializeNotifications() {
    const notificationBell = document.querySelector('.notification-link');
    
    if (notificationBell) {
        notificationBell.addEventListener('click', function(e) {
            e.preventDefault();
            showNotifications();
        });
    }
}

function showNotifications() {
    // Create notification dropdown
    const notificationDropdown = document.createElement('div');
    notificationDropdown.className = 'notification-dropdown';
    notificationDropdown.innerHTML = `
        <div class="notification-header">
            <h4>Notifications</h4>
            <button class="mark-all-read">Mark all as read</button>
        </div>
        <div class="notification-list">
            <div class="notification-item unread">
                <div class="notification-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="notification-content">
                    <p>Fee reminder for 3 students pending</p>
                    <span class="notification-time">2 hours ago</span>
                </div>
            </div>
            <div class="notification-item unread">
                <div class="notification-icon">
                    <i class="fas fa-user-plus"></i>
                </div>
                <div class="notification-content">
                    <p>New admission application received</p>
                    <span class="notification-time">4 hours ago</span>
                </div>
            </div>
            <div class="notification-item">
                <div class="notification-icon">
                    <i class="fas fa-credit-card"></i>
                </div>
                <div class="notification-content">
                    <p>Monthly fee collection completed</p>
                    <span class="notification-time">1 day ago</span>
                </div>
            </div>
        </div>
        <div class="notification-footer">
            <a href="#">View all notifications</a>
        </div>
    `;
    
    // Add styles for notification dropdown
    const style = document.createElement('style');
    style.textContent = `
        .notification-dropdown {
            position: absolute;
            top: 100%;
            right: 0;
            width: 320px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
            z-index: 1001;
            overflow: hidden;
        }
        
        .notification-header {
            padding: 16px 20px;
            border-bottom: 1px solid #F0F0F0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .notification-header h4 {
            font-size: 16px;
            font-weight: 600;
            color: #453F4E;
        }
        
        .mark-all-read {
            background: none;
            border: none;
            color: #214888;
            font-size: 12px;
            cursor: pointer;
            font-weight: 500;
        }
        
        .notification-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .notification-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 20px;
            border-bottom: 1px solid #F0F0F0;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        
        .notification-item:hover {
            background-color: #F3EBFF;
        }
        
        .notification-item.unread {
            background-color: #FBF8FF;
            position: relative;
        }
        
        .notification-item.unread::before {
            content: '';
            position: absolute;
            left: 8px;
            top: 50%;
            transform: translateY(-50%);
            width: 6px;
            height: 6px;
            background-color: #214888;
            border-radius: 50%;
        }
        
        .notification-icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #F3EBFF;
            color: #214888;
            font-size: 14px;
            flex-shrink: 0;
        }
        
        .notification-content p {
            font-size: 14px;
            color: #453F4E;
            margin-bottom: 4px;
        }
        
        .notification-time {
            font-size: 12px;
            color: #453F4E;
            opacity: 0.6;
        }
        
        .notification-footer {
            padding: 12px 20px;
            text-align: center;
            border-top: 1px solid #F0F0F0;
        }
        
        .notification-footer a {
            color: #214888;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
        }
    `;
    
    document.head.appendChild(style);
    
    // Position dropdown
    const notificationLink = document.querySelector('.notification-link');
    const navItem = notificationLink.closest('.nav-item');
    
    navItem.style.position = 'relative';
    navItem.appendChild(notificationDropdown);
    
    // Close dropdown when clicking outside
    setTimeout(() => {
        document.addEventListener('click', function closeNotifications(e) {
            if (!navItem.contains(e.target)) {
                notificationDropdown.remove();
                style.remove();
                document.removeEventListener('click', closeNotifications);
            }
        });
    }, 100);
}

// Real-time Data Updates
function updateRealTimeData() {
    // Simulate real-time data updates
    updateStatistics();
    updateActivities();
    updateNotificationCount();
}

function updateStatistics() {
    // Simulate dynamic statistics update
    const stats = [
        { selector: '.stat-card.primary h3', value: Math.floor(Math.random() * 50) + 220 },
        { selector: '.stat-card.secondary h3', value: Math.floor(Math.random() * 10) + 15 },
        { selector: '.stat-card.accent h3', value: '₹' + (Math.floor(Math.random() * 20000) + 75000).toLocaleString() },
        { selector: '.stat-card.warning h3', value: Math.floor(Math.random() * 8) + 8 }
    ];
    
    stats.forEach(stat => {
        const element = document.querySelector(stat.selector);
        if (element) {
            // Animate number change
            animateNumberChange(element, stat.value);
        }
    });
}

function animateNumberChange(element, newValue) {
    const currentValue = element.textContent;
    const isNumber = !isNaN(parseFloat(currentValue.replace(/[^\d.-]/g, '')));
    
    if (isNumber) {
        const current = parseFloat(currentValue.replace(/[^\d.-]/g, ''));
        const target = parseFloat(newValue.toString().replace(/[^\d.-]/g, ''));
        const prefix = currentValue.match(/[^\d.-]/g) ? currentValue.match(/[^\d.-]/g).join('') : '';
        
        const duration = 1000;
        const steps = 30;
        const stepValue = (target - current) / steps;
        const stepDuration = duration / steps;
        
        let currentStep = 0;
        
        const timer = setInterval(() => {
            currentStep++;
            const value = Math.floor(current + (stepValue * currentStep));
            element.textContent = prefix + value.toLocaleString();
            
            if (currentStep >= steps) {
                clearInterval(timer);
                element.textContent = newValue;
            }
        }, stepDuration);
    }
}

function updateActivities() {
    // Add new activity items occasionally
    if (Math.random() > 0.7) {
        const activityList = document.querySelector('.activity-list');
        if (activityList) {
            const activities = [
                {
                    icon: 'user-plus',
                    iconClass: 'new',
                    text: '<strong>New Student</strong> enrolled in Pre-KG',
                    time: 'Just now'
                },
                {
                    icon: 'credit-card',
                    iconClass: 'payment',
                    text: '<strong>Payment</strong> received for transport fee',
                    time: 'Few minutes ago'
                },
                {
                    icon: 'bell',
                    iconClass: 'warning',
                    text: 'Reminder sent for <strong>pending fees</strong>',
                    time: 'An hour ago'
                }
            ];
            
            const randomActivity = activities[Math.floor(Math.random() * activities.length)];
            
            const newActivity = document.createElement('div');
            newActivity.className = 'activity-item';
            newActivity.innerHTML = `
                <div class="activity-icon ${randomActivity.iconClass}">
                    <i class="fas fa-${randomActivity.icon}"></i>
                </div>
                <div class="activity-content">
                    <p>${randomActivity.text}</p>
                    <span class="activity-time">${randomActivity.time}</span>
                </div>
            `;
            
            activityList.insertBefore(newActivity, activityList.firstChild);
            
            // Remove oldest activity if more than 5
            const activities_elements = activityList.querySelectorAll('.activity-item');
            if (activities_elements.length > 4) {
                activityList.removeChild(activities_elements[activities_elements.length - 1]);
            }
        }
    }
}

function updateNotificationCount() {
    const notificationBadge = document.querySelector('.notification-badge');
    if (notificationBadge && Math.random() > 0.8) {
        const currentCount = parseInt(notificationBadge.textContent);
        const newCount = Math.max(0, currentCount + (Math.random() > 0.5 ? 1 : -1));
        notificationBadge.textContent = newCount;
        
        if (newCount === 0) {
            notificationBadge.style.display = 'none';
        } else {
            notificationBadge.style.display = 'block';
        }
    }
}

// Utility Functions
function formatCurrency(amount) {
    return '₹' + amount.toLocaleString('en-IN');
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    const style = document.createElement('style');
    style.textContent = `
        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            font-family: 'Poppins', sans-serif;
            font-size: 14px;
            font-weight: 500;
            animation: slideInRight 0.3s ease;
            max-width: 300px;
        }
        
        .toast-success {
            border-left: 4px solid #43A574;
            color: #43A574;
        }
        
        .toast-error {
            border-left: 4px solid #FF9587;
            color: #FF9587;
        }
        
        .toast-warning {
            border-left: 4px solid #FFB804;
            color: #FFB804;
        }
        
        .toast-info {
            border-left: 4px solid #214888;
            color: #214888;
        }
        
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            if (style.parentNode) {
                style.parentNode.removeChild(style);
            }
        }, 300);
    }, 3000);
}

// Add slideOutRight animation
const slideOutStyle = document.createElement('style');
slideOutStyle.textContent = `
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(slideOutStyle);

// Progress Animation
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-fill');
    
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });
}

// Initialize progress bar animations when page loads
setTimeout(animateProgressBars, 1000);

// Quick Action Handlers
document.addEventListener('click', function(e) {
    if (e.target.closest('.action-btn')) {
        e.preventDefault();
        const action = e.target.closest('.action-btn');
        const actionText = action.querySelector('span').textContent;
        
        // Simulate action feedback
        action.style.transform = 'scale(0.95)';
        setTimeout(() => {
            action.style.transform = 'translateY(-2px)';
        }, 150);
        
        // Show toast notification
        showToast(`${actionText} clicked - Feature coming soon!`, 'info');
    }
});

// Form Select Styling and Functionality
document.querySelectorAll('.form-select').forEach(select => {
    select.addEventListener('change', function() {
        // Add visual feedback
        this.style.borderColor = '#214888';
        setTimeout(() => {
            this.style.borderColor = '#F0F0F0';
        }, 300);
    });
});

// Card Hover Effects Enhancement
document.querySelectorAll('.dashboard-card, .stat-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-4px)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Search Functionality (for future implementation)
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            // Implement search logic here
            console.log('Searching for:', query);
        });
    }
}

// Theme Toggle (for future dark mode implementation)
function toggleTheme() {
    const body = document.body;
    const isDark = body.classList.contains('dark-theme');
    
    if (isDark) {
        body.classList.remove('dark-theme');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.add('dark-theme');
        localStorage.setItem('theme', 'dark');
    }
}

// Load saved theme preference
function loadThemePreference() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// Performance Optimization: Lazy load non-critical features
function lazyLoadFeatures() {
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe dashboard cards for scroll animations
    document.querySelectorAll('.dashboard-card').forEach(card => {
        observer.observe(card);
    });
}

// Add CSS for scroll animations
const scrollAnimationStyle = document.createElement('style');
scrollAnimationStyle.textContent = `
    .dashboard-card {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease;
    }
    
    .dashboard-card.animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    .dashboard-card:nth-child(odd).animate-in {
        animation: slideInLeft 0.6s ease;
    }
    
    .dashboard-card:nth-child(even).animate-in {
        animation: slideInRight 0.6s ease;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;

// Initialize lazy loading after DOM is loaded
setTimeout(lazyLoadFeatures, 500);

// // Error Handling
// window.addEventListener('error', function(e) {
//     console.error('Dashboard Error:', e.error);
//     showToast('Something went wrong. Please refresh the page.', 'error');
// });

// Keyboard Shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for quick search (future implementation)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        showToast('Quick search - Feature coming soon!', 'info');
    }
    
    // ESC to close dropdowns
    if (e.key === 'Escape') {
        closeAllDropdowns();
    }
});

// Export functions for potential external use
window.NurseryDashboard = {
    updateStatistics,
    showToast,
    toggleTheme,
    animateProgressBars,
    formatCurrency,
    formatDate
};

// Initialize everything when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Nursery ERP Dashboard initialized successfully!');
        showToast('Dashboard loaded successfully!', 'success');
    });
} else {
    console.log('Nursery ERP Dashboard initialized successfully!');
}

// Service Worker Registration (for future PWA implementation)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // navigator.serviceWorker.register('/sw.js')
        //     .then(registration => console.log('SW registered'))
        //     .catch(error => console.log('SW registration failed'));
    });
}

// Analytics tracking (placeholder for future implementation)
function trackEvent(eventName, eventData) {
    // Google Analytics or custom analytics implementation
    console.log('Event tracked:', eventName, eventData);
}
// ADD THESE FUNCTIONS TO YOUR EXISTING JAVASCRIPT FILE

// Toggle Main Navigation (for utility bar button)
function toggleMainNav() {
    const mainNav = document.querySelector('.top-nav');
    mainNav.classList.toggle('hidden');
}

// REPLACE YOUR EXISTING initializeMobileMenu() FUNCTION WITH THIS:
function initializeMobileMenu() {
    const mobileToggle = document.getElementById('mobileToggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            navMenu.classList.toggle('mobile-active');
            const icon = mobileToggle.querySelector('i');
            
            if (navMenu.classList.contains('mobile-active')) {
                icon.className = 'fas fa-times';
                document.body.style.overflow = 'hidden';
            } else {
                icon.className = 'fas fa-bars';
                document.body.style.overflow = '';
            }
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!mobileToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('mobile-active');
                const icon = mobileToggle.querySelector('i');
                icon.className = 'fas fa-bars';
                document.body.style.overflow = '';
            }
        });
        
        // Close mobile menu on window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                navMenu.classList.remove('mobile-active');
                const icon = mobileToggle.querySelector('i');
                icon.className = 'fas fa-bars';
                document.body.style.overflow = '';
            }
        });
    }
}

// ADD THIS TO FIX MOBILE DROPDOWNS
function initializeDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (!toggle || !menu) return;
        
        // Handle both desktop hover and mobile click
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // For mobile (when nav menu is active)
            const navMenu = document.querySelector('.nav-menu');
            if (navMenu && navMenu.classList.contains('mobile-active')) {
                // Close other mobile dropdowns
                dropdowns.forEach(otherDropdown => {
                    if (otherDropdown !== dropdown) {
                        otherDropdown.classList.remove('mobile-open');
                    }
                });
                
                // Toggle current dropdown
                dropdown.classList.toggle('mobile-open');
            } else {
                // Desktop behavior - close other dropdowns
                closeAllDropdowns();
                dropdown.classList.toggle('active');
                menu.style.opacity = dropdown.classList.contains('active') ? '1' : '0';
                menu.style.visibility = dropdown.classList.contains('active') ? 'visible' : 'hidden';
                menu.style.transform = dropdown.classList.contains('active') ? 'translateY(0)' : 'translateY(-10px)';
            }
        });
        
        // Close dropdown when clicking outside (desktop only)
        document.addEventListener('click', function(e) {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
                if (menu) {
                    menu.style.opacity = '0';
                    menu.style.visibility = 'hidden';
                    menu.style.transform = 'translateY(-10px)';
                }
            }
        });
    });
}