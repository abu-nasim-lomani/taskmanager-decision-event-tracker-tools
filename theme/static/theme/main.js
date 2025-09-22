// theme/static/theme/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Logic to highlight the active sidebar link
    const currentPage = window.location.pathname;
    // Query for both desktop and mobile links
    const navLinks = document.querySelectorAll('a.sidebar-item, a.mobile-nav-item');
    
    navLinks.forEach(link => {
        // Use startsWith for detail pages like /meeting/1/ to match with /
        if (currentPage.startsWith(link.getAttribute('href'))) {
            // Add active classes
            if(link.classList.contains('sidebar-item')) {
                 link.classList.add('bg-slate-900/80', 'text-white');
                 link.classList.remove('text-slate-300', 'hover:bg-slate-700/50');
            }
            if(link.classList.contains('mobile-nav-item')) {
                link.classList.add('bg-gray-100', 'border-indigo-600');
                link.classList.remove('text-gray-500', 'border-transparent');
            }
        }
    });
});