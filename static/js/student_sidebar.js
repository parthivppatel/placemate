const navItems = document.querySelectorAll('.nav-item');

navItems.forEach(item => {
  item.addEventListener('click', () => {
    // Remove active class from all items
    navItems.forEach(navItem => {
      navItem.classList.remove('active');
    });

    // Add active class to clicked item
    item.classList.add('active');
  });
});