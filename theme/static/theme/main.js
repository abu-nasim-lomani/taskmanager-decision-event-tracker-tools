// Simple JavaScript for interactive elements
        document.addEventListener('DOMContentLoaded', function() {
            // Add active state to current page in sidebar
            const currentPage = window.location.pathname;
            const navLinks = document.querySelectorAll('nav a');
            
            navLinks.forEach(link => {
                if (link.getAttribute('href') === currentPage) {
                    link.classList.add('bg-indigo-700', 'text-white');
                    link.classList.remove('text-indigo-100', 'hover:bg-indigo-600/50', 'hover:text-white');
                }
            });
        });