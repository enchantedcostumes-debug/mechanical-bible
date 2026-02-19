/**
 * LOGOS - Unified Site Footer
 * Injected dynamically on all pages
 */

(function() {
    // Create footer element
    const footer = document.createElement('footer');
    footer.className = 'site-footer';
    footer.innerHTML = `
        <div class="site-footer-inner">
            <nav class="footer-nav">
                <a href="/">Mechanical Bible</a>
                <span class="divider">|</span>
                <a href="/sacred-library/">Sacred Library</a>
                <span class="divider">|</span>
                <a href="https://ozark-oracle.com/" target="_blank">Apokalypsis</a>
            </nav>
            <p class="copyright">Copyright 2026 Tammy L Casey. All rights reserved.</p>
            <p class="tagline">LOGOS - The Word Made Visible</p>
        </div>
    `;

    // Append to body
    document.body.appendChild(footer);
})();
