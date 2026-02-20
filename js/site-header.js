/**
 * LOGOS - Unified Site Header
 * Injected dynamically on all pages
 */

(function() {
    // Skip injection if header already exists in the HTML (e.g. oracle.html)
    var existing = document.querySelector('header.site-header');
    var header;

    if (existing) {
        header = existing;
    } else {
        // Create header element
        header = document.createElement('header');
        header.className = 'site-header';
        header.innerHTML = `
            <div class="site-header-inner">
                <a href="/" class="site-logo">LOGOS</a>
                <nav class="site-nav">
                    <a href="/">Mechanical Bible</a>
                    <a href="/sacred-library/">Sacred Library</a>
                    <a href="/search.html">Search</a>
                    <a href="/tsk.html">Cross-References</a>
                    <a href="/names.html">Names</a>
                    <a href="/donate.html">Support</a>
                    <a href="https://ozark-oracle.com/" target="_blank" class="red-letter">Apokalypsis</a>
                </nav>
                <button class="mobile-menu-toggle" aria-label="Toggle menu">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
            </div>
        `;

        // Insert at the very beginning of body
        document.body.insertBefore(header, document.body.firstChild);
    }

    // Mobile menu toggle
    const menuToggle = header.querySelector('.mobile-menu-toggle');
    const nav = header.querySelector('.site-nav');

    if (menuToggle && nav) {
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });
    }

    // Highlight current page in nav
    const currentPath = window.location.pathname;
    const navLinks = header.querySelectorAll('.site-nav a');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath ||
            (href === '/' && currentPath === '/index.html') ||
            (currentPath.startsWith('/sacred-library') && href === '/sacred-library/') ||
            (currentPath === '/names.html' && href === '/names.html')) {
            link.classList.add('active');
        }
    });
})();
