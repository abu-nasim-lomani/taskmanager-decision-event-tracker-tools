// theme/static/theme/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Logic to highlight the active sidebar link
    const currentPage = window.location.pathname;
    const navLinks = document.querySelectorAll('a.sidebar-item');
    
    // Find the best match for the current page
    let bestMatch = null;
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPage.startsWith(href)) {
            if (!bestMatch || href.length > bestMatch.getAttribute('href').length) {
                bestMatch = link;
            }
        }
    });

    // Apply active styles only to the best match
    if (bestMatch) {
        bestMatch.classList.add('bg-slate-900', 'text-white');
        bestMatch.classList.remove('text-slate-300', 'hover:bg-slate-700');
    }
});