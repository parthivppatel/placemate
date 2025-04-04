// sidebar.js
document.addEventListener('DOMContentLoaded', function() {
    // Set active page based on current URL
    const currentPage = getCurrentPage();
    setActivePage(currentPage);
    
    // Add event listeners to nav items
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const page = this.getAttribute('data-page');
            setActivePage(page);
        });
    });
});

// Helper function to get current page from URL
function getCurrentPage() {
    const path = window.location.pathname;
    if (path.includes('students')) return 'students';
    if (path.includes('drives')) return 'drives';
    if (path.includes('reports')) return 'reports';
    return 'dashboard'; // Default
}

// Helper function to set active page
function setActivePage(page) {
    // Remove active class from all items
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    
    // Add active class to current page
    const activeItem = document.querySelector(`.nav-item[data-page="${page}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
}
