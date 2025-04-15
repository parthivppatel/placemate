document.addEventListener('DOMContentLoaded', function() {
    const page = window.location.pathname.split('/').pop();
    const linkMap = {
        'dashboard': 'dashboard-link',
        'students': 'students-link',
        'companies': 'companies-link',
        'drives': 'drives-link',
        'reports': 'reports-link',
    };

    for (const [key, id] of Object.entries(linkMap)) {
        if (page.includes(key)) {
            document.getElementById(id)?.classList.add('active');
        }
    }
});
