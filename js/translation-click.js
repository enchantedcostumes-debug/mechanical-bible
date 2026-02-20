/**
 * Translation Click Handler - Mechanical Bible
 * Makes translation words clickable, linking to Hebrew word evolution.
 * Mechanical translation maps 1:1 with Hebrew words.
 * RMT/JPS map by position (approximate).
 *
 * Copyright (c) 2026 Tammy L Casey. All rights reserved.
 */
(function() {
    'use strict';

    function init() {
        var verses = document.querySelectorAll('.verse');
        if (!verses.length) return;

        verses.forEach(function(verse) {
            var hebrewWords = verse.querySelectorAll('.original-text .word');
            if (!hebrewWords.length) return;

            // Collect Hebrew text for each position
            var hebrewTexts = [];
            hebrewWords.forEach(function(w) {
                hebrewTexts.push(w.textContent.trim());
            });

            // Process each translation span
            var spans = verse.querySelectorAll('.translation .rmt, .translation .mechanical, .translation .jps, .translation .toggle-translation');
            spans.forEach(function(span) {
                var text = span.textContent.trim();
                if (!text) return;

                // Split into tokens by whitespace
                var tokens = text.split(/\s+/);
                if (!tokens.length) return;

                // Build clickable HTML
                var parts = [];
                for (var i = 0; i < tokens.length; i++) {
                    // Map to Hebrew word by position, clamp to last Hebrew word
                    var hi = Math.min(i, hebrewTexts.length - 1);
                    var hw = hebrewTexts[hi];
                    parts.push('<span class="tword" data-hebrew="' + escapeAttr(hw) + '">' + escapeHtml(tokens[i]) + '</span>');
                }
                span.innerHTML = parts.join(' ');
            });
        });

        // Single delegated click handler for all .tword elements
        document.addEventListener('click', function(e) {
            var tw = e.target.closest('.tword');
            if (tw && tw.dataset.hebrew && typeof showWordEvolution === 'function') {
                e.stopPropagation();
                showWordEvolution(tw.dataset.hebrew);
            }
        });
    }

    function escapeHtml(s) {
        var d = document.createElement('div');
        d.textContent = s;
        return d.innerHTML;
    }

    function escapeAttr(s) {
        return s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
