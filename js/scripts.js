/**
 * Script Loader - Mechanical Bible
 * ===================================
 * Single entry point for all page scripts.
 * Change versions or add/remove scripts here instead of editing 1,189 HTML files.
 *
 * Copyright (c) 2026 Tammy L Casey. All rights reserved.
 */
(function() {
    'use strict';

    // Version string for cache-busting (change this ONE place to bust cache everywhere)
    var V = '20260219d';

    // Find our own script tag to determine base path
    // If loaded as "../js/scripts.js", base is "../js/"
    // If loaded as "js/scripts.js", base is "js/"
    // If loaded as "../../js/scripts.js", base is "../../js/"
    var me = document.currentScript;
    var base = me ? me.src.replace(/scripts\.js.*$/, '') : '';
    // Convert absolute URL back to relative path
    if (base.indexOf('://') !== -1) {
        var origin = window.location.origin;
        base = base.replace(origin, '');
    }

    // Detect if we're on a chapter page (has .verse elements or numeric filename)
    var path = window.location.pathname;
    var filename = path.split('/').pop();
    var isChapter = /^\d+\.html$/.test(filename);

    // Chapter pages: exact load order
    var chapterScripts = [
        'word-modal.js',
        'site-header.js',
        'translation-toggle.js',
        'site-footer.js',
        'interlinear.js',
        'parallel-view.js',
        'grammar-view.js',
        'search.js'
    ];

    // Non-chapter pages: just header + footer
    var defaultScripts = [
        'site-header.js',
        'site-footer.js'
    ];

    var scripts = isChapter ? chapterScripts : defaultScripts;

    scripts.forEach(function(file) {
        var s = document.createElement('script');
        s.src = base + file + '?v=' + V;
        document.body.appendChild(s);
    });
})();
