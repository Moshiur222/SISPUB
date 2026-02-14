// Header and Navigation Functionality

class HeaderManager {
    constructor() {
        this.header = document.querySelector('.main-nav');
        this.menuToggle = document.querySelector('.menu-toggle');
        this.mobileNav = document.querySelector('.mobile-nav');
        this.mobileOverlay = document.querySelector('.mobile-nav-overlay');
        this.mobileClose = document.querySelector('.mobile-close');
        this.searchToggle = document.querySelector('.btn-search');
        this.searchOverlay = document.querySelector('.search-overlay');
        this.searchClose = document.querySelector('.search-close');
        this.dropdowns = document.querySelectorAll('.dropdown');
        this.navItems = document.querySelectorAll('.nav-item');
        this.scrollProgress = null;
        
        this.init();
    }
    
    init() {
        // Initialize all functionality
        this.setupMobileMenu();
        this.setupSearch();
        this.setupDropdowns();
        this.setupStickyHeader();
        this.setupScrollProgress();
        this.setupActiveLinks();
        this.setupKeyboardNavigation();
        this.setupResizeHandler();
        this.setupMobileDropdowns();
        
        console.log('Header Manager initialized');
    }
    
    setupMobileMenu() {
        // Mobile menu toggle
        this.menuToggle?.addEventListener('click', () => {
            this.toggleMobileMenu(true);
        });
        
        // Close mobile menu
        this.mobileClose?.addEventListener('click', () => {
            this.toggleMobileMenu(false);
        });
        
        // Close mobile menu when clicking overlay
        this.mobileOverlay?.addEventListener('click', () => {
            this.toggleMobileMenu(false);
        });
        
        // Close mobile menu with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.mobileNav?.classList.contains('active')) {
                this.toggleMobileMenu(false);
            }
        });
    }
    
    setupMobileDropdowns() {
        // Generate mobile menu from desktop menu
        this.generateMobileMenu();
        
        // Mobile dropdown functionality
        document.addEventListener('click', (e) => {
            const toggleBtn = e.target.closest('.mobile-dropdown-toggle');
            if (toggleBtn) {
                e.preventDefault();
                const dropdown = toggleBtn.nextElementSibling;
                const icon = toggleBtn.querySelector('.mobile-dropdown-icon');
                
                dropdown.classList.toggle('active');
                icon?.classList.toggle('active');
            }
        });
    }
    
    generateMobileMenu() {
        const mobileContent = document.querySelector('.mobile-nav-content');
        if (!mobileContent) return;
        
        // Get all navigation items
        const navItems = Array.from(document.querySelectorAll('.nav-item'));
        
        // Clear existing content
        mobileContent.innerHTML = '';
        
        // Create mobile menu items
        navItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            const dropdown = item.querySelector('.dropdown-menu');
            
            if (!link) return;
            
            const mobileItem = document.createElement('div');
            mobileItem.className = 'mobile-nav-item';
            
            if (dropdown) {
                // Create dropdown item
                const toggle = link.cloneNode(true);
                toggle.classList.add('mobile-nav-link', 'mobile-dropdown-toggle');
                toggle.innerHTML += '<i class="fas fa-chevron-down mobile-dropdown-icon"></i>';
                
                const dropdownContent = dropdown.cloneNode(true);
                dropdownContent.classList.add('mobile-dropdown-menu');
                
                // Convert dropdown items
                const dropdownItems = dropdownContent.querySelectorAll('.dropdown-item');
                dropdownItems.forEach(dropItem => {
                    dropItem.classList.add('mobile-nav-link');
                });
                
                mobileItem.appendChild(toggle);
                mobileItem.appendChild(dropdownContent);
            } else {
                // Create regular item
                const mobileLink = link.cloneNode(true);
                mobileLink.classList.add('mobile-nav-link');
                mobileItem.appendChild(mobileLink);
            }
            
            mobileContent.appendChild(mobileItem);
        });
    }
    
    toggleMobileMenu(show) {
        if (show) {
            this.mobileNav?.classList.add('active');
            this.mobileOverlay?.classList.add('active');
            document.body.style.overflow = 'hidden';
        } else {
            this.mobileNav?.classList.remove('active');
            this.mobileOverlay?.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    setupSearch() {
        // Search toggle
        this.searchToggle?.addEventListener('click', () => {
            this.toggleSearch(true);
        });
        
        // Close search
        this.searchClose?.addEventListener('click', () => {
            this.toggleSearch(false);
        });
        
        // Close search with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.searchOverlay?.classList.contains('active')) {
                this.toggleSearch(false);
            }
        });
        
        // Close search when clicking outside
        this.searchOverlay?.addEventListener('click', (e) => {
            if (e.target === this.searchOverlay) {
                this.toggleSearch(false);
            }
        });
        
        // Search form submission
        const searchForm = document.querySelector('.search-form form');
        searchForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = searchForm.querySelector('.search-input');
            if (input.value.trim()) {
                this.performSearch(input.value);
            }
        });
    }
    
    toggleSearch(show) {
        if (show) {
            this.searchOverlay?.classList.add('active');
            const searchInput = this.searchOverlay?.querySelector('.search-input');
            searchInput?.focus();
            document.body.style.overflow = 'hidden';
        } else {
            this.searchOverlay?.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    performSearch(query) {
        console.log('Searching for:', query);
        // Implement actual search functionality here
        // This could be an AJAX call to your search endpoint
        alert(`Search functionality would search for: "${query}"`);
        this.toggleSearch(false);
    }
    
    setupDropdowns() {
        // Desktop dropdown hover functionality
        this.dropdowns.forEach(dropdown => {
            dropdown.addEventListener('mouseenter', () => {
                if (window.innerWidth > 1024) {
                    dropdown.classList.add('hover');
                }
            });
            
            dropdown.addEventListener('mouseleave', () => {
                if (window.innerWidth > 1024) {
                    dropdown.classList.remove('hover');
                }
            });
            
            // Touch devices
            dropdown.addEventListener('touchstart', (e) => {
                if (window.innerWidth <= 1024) {
                    e.preventDefault();
                    dropdown.classList.toggle('hover');
                }
            });
        });
    }
    
    setupStickyHeader() {
        let lastScroll = 0;
        
        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;
            
            // Sticky header
            if (currentScroll > 100) {
                this.header?.classList.add('sticky');
            } else {
                this.header?.classList.remove('sticky');
            }
            
            // Hide/show on scroll direction
            if (currentScroll > 200) {
                if (currentScroll > lastScroll) {
                    // Scrolling down
                    this.header?.style.transform = 'translateY(-100%)';
                } else {
                    // Scrolling up
                    this.header?.style.transform = 'translateY(0)';
                }
            }
            
            lastScroll = currentScroll;
            
            // Update scroll progress
            this.updateScrollProgress(currentScroll);
        });
    }
    
    setupScrollProgress() {
        // Create scroll progress bar
        this.scrollProgress = document.createElement('div');
        this.scrollProgress.className = 'scroll-progress';
        document.body.appendChild(this.scrollProgress);
    }
    
    updateScrollProgress(scrollPosition) {
        if (!this.scrollProgress) return;
        
        const windowHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrolled = (scrollPosition / windowHeight) * 100;
        
        this.scrollProgress.style.width = scrolled + '%';
    }
    
    setupActiveLinks() {
        // Set active link based on current page
        const currentPath = window.location.pathname;
        
        this.navItems.forEach(item => {
            const link = item.querySelector('.nav-link');
            if (link) {
                const linkPath = new URL(link.href).pathname;
                
                if (currentPath === linkPath || 
                    (currentPath.includes(linkPath) && linkPath !== '/')) {
                    item.classList.add('active');
                    
                    // Also update mobile menu
                    const mobileLink = document.querySelector(`.mobile-nav-link[href="${link.href}"]`);
                    if (mobileLink) {
                        mobileLink.classList.add('active');
                    }
                }
            }
        });
    }
    
    setupKeyboardNavigation() {
        // Keyboard navigation for accessibility
        document.addEventListener('keydown', (e) => {
            // Tab navigation within mobile menu
            if (this.mobileNav?.classList.contains('active')) {
                const focusableElements = this.mobileNav.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                
                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        // Shift + Tab
                        if (document.activeElement === focusableElements[0]) {
                            e.preventDefault();
                            focusableElements[focusableElements.length - 1].focus();
                        }
                    } else {
                        // Tab
                        if (document.activeElement === focusableElements[focusableElements.length - 1]) {
                            e.preventDefault();
                            focusableElements[0].focus();
                        }
                    }
                }
            }
            
            // Arrow key navigation for dropdowns
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                const activeDropdown = document.querySelector('.dropdown.hover');
                if (activeDropdown && window.innerWidth > 1024) {
                    e.preventDefault();
                    const items = activeDropdown.querySelectorAll('.dropdown-item');
                    const currentIndex = Array.from(items).findIndex(item => 
                        item === document.activeElement
                    );
                    
                    if (e.key === 'ArrowDown') {
                        const nextIndex = (currentIndex + 1) % items.length;
                        items[nextIndex]?.focus();
                    } else if (e.key === 'ArrowUp') {
                        const prevIndex = (currentIndex - 1 + items.length) % items.length;
                        items[prevIndex]?.focus();
                    }
                }
            }
        });
    }
    
    setupResizeHandler() {
        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
    }
    
    handleResize() {
        // Close mobile menu on desktop
        if (window.innerWidth > 1024 && this.mobileNav?.classList.contains('active')) {
            this.toggleMobileMenu(false);
        }
        
        // Close search overlay
        if (this.searchOverlay?.classList.contains('active')) {
            this.toggleSearch(false);
        }
        
        // Regenerate mobile menu on resize
        this.generateMobileMenu();
    }
    
    // Public methods
    openSearch() {
        this.toggleSearch(true);
    }
    
    closeSearch() {
        this.toggleSearch(false);
    }
    
    openMobileMenu() {
        this.toggleMobileMenu(true);
    }
    
    closeMobileMenu() {
        this.toggleMobileMenu(false);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.headerManager = new HeaderManager();
    
    // Add animation on scroll for hero section
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    }, observerOptions);
    
    // Observe hero elements
    document.querySelectorAll('.hero-title, .hero-subtitle, .hero-description, .stat-item').forEach(el => {
        observer.observe(el);
    });
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const headerOffset = 100;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                if (window.headerManager.mobileNav?.classList.contains('active')) {
                    window.headerManager.closeMobileMenu();
                }
            }
        });
    });
    
    // Add hover effects to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HeaderManager;
}