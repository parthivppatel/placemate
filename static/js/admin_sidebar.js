document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname.replace(/\/+$/, ''); // remove trailing slash
    const navLinks = document.querySelectorAll('.nav-link');
  
    navLinks.forEach(link => {
      const href = link.getAttribute('href').replace(/\/+$/, ''); // remove trailing slash
  
      if (href === currentPath || (href === '' && currentPath === '/')) {
        link.classList.add('active');
      }
    });
  
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content') || document.getElementById('content') || document.querySelector('main');
  
    if (mainContent && sidebar) {
      sidebar.addEventListener('mouseenter', () => {
        mainContent.style.marginLeft = 'var(--sidebar-width)';
      });
  
      sidebar.addEventListener('mouseleave', () => {
        mainContent.style.marginLeft = 'var(--sidebar-collapsed-width)';
      });
    }
  });
  