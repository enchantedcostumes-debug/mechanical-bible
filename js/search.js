/**
 * Search - Mechanical Bible
 * Full-text search across all 66 books and 1,189 chapters.
 *
 * Searches Hebrew words, English definitions, transliterations,
 * Strong's numbers, gematria values, and verse translations.
 *
 * Copyright (c) 2026 Tammy L Casey. All rights reserved.
 */

let searchIndex = null;
let searchModal = null;
let searchOpen = false;

// Book order for display
const BOOK_ORDER = [
    'genesis','exodus','leviticus','numbers','deuteronomy',
    'joshua','judges','ruth','i_samuel','ii_samuel',
    'i_kings','ii_kings','i_chronicles','ii_chronicles',
    'ezra','nehemiah','esther','job','psalms','proverbs',
    'ecclesiastes','song_of_songs','isaiah','jeremiah','lamentations',
    'ezekiel','daniel','hosea','joel','amos','obadiah','jonah',
    'micah','nahum','habakkuk','zephaniah','haggai','zechariah','malachi',
    'matthew','mark','luke','john','acts','romans',
    '1_corinthians','2_corinthians','galatians','ephesians','philippians',
    'colossians','1_thessalonians','2_thessalonians','1_timothy','2_timothy',
    'titus','philemon','hebrews','james','1_peter','2_peter',
    '1_john','2_john','3_john','jude','revelation'
];


async function loadSearchIndex() {
    if (searchIndex) return searchIndex;

    try {
        // Determine base path
        const pathParts = window.location.pathname.split('/');
        const inBook = pathParts.length > 2 && !pathParts[pathParts.length - 1].match(/^(index|names|search|parallels|prophecy|topics|frequency|variants|controversies|fathers)\.html$/);
        const base = inBook ? '..' : '.';

        // Load word data
        let words = {};
        if (typeof wordData !== 'undefined' && wordData) {
            words = wordData;
        } else {
            try {
                const resp = await fetch(base + '/words-priority.json');
                words = await resp.json();
            } catch (e) {
                console.log('Priority words not available, trying full...');
            }
        }

        searchIndex = { words: words, base: base };
        return searchIndex;
    } catch (err) {
        console.error('Search index load failed:', err);
        return null;
    }
}


function buildSearchModal() {
    if (document.getElementById('search-modal')) return;

    const modal = document.createElement('div');
    modal.id = 'search-modal';
    modal.className = 'search-modal';
    modal.innerHTML =
        '<div class="search-modal-content">' +
            '<div class="search-header">' +
                '<h2 class="search-title">Search the Bible</h2>' +
                '<button class="search-close" onclick="closeSearch()">&times;</button>' +
            '</div>' +
            '<div class="search-input-wrap">' +
                '<input type="text" id="search-input" class="search-input" ' +
                    'placeholder="Search Hebrew, English, transliteration, Strong\'s, gematria..." ' +
                    'autocomplete="off" spellcheck="false">' +
                '<div class="search-hint">Search across all 66 books - ' +
                    'Hebrew words, definitions, transliterations, Strong\'s numbers</div>' +
            '</div>' +
            '<div id="search-results" class="search-results"></div>' +
        '</div>';

    document.body.appendChild(modal);
    searchModal = modal;

    const input = document.getElementById('search-input');
    let debounce = null;
    input.addEventListener('input', function() {
        clearTimeout(debounce);
        debounce = setTimeout(function() {
            performSearch(input.value.trim());
        }, 200);
    });

    modal.addEventListener('click', function(e) {
        if (e.target === modal) closeSearch();
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && searchOpen) closeSearch();
    });
}


function openSearch() {
    buildSearchModal();
    searchModal.style.display = 'flex';
    searchOpen = true;
    document.body.style.overflow = 'hidden';

    setTimeout(function() {
        var input = document.getElementById('search-input');
        if (input) {
            input.value = '';
            input.focus();
        }
        document.getElementById('search-results').innerHTML = '';
    }, 100);

    loadSearchIndex();
}


function closeSearch() {
    if (searchModal) searchModal.style.display = 'none';
    searchOpen = false;
    document.body.style.overflow = '';
}


async function performSearch(query) {
    const resultsDiv = document.getElementById('search-results');
    if (!query || query.length < 2) {
        resultsDiv.innerHTML = '<div class="search-empty">Type at least 2 characters to search</div>';
        return;
    }

    const index = await loadSearchIndex();
    if (!index) {
        resultsDiv.innerHTML = '<div class="search-empty">Search index not available</div>';
        return;
    }

    const results = [];
    const q = query.toLowerCase();
    const isHebrew = /[\u0590-\u05FF]/.test(query);
    const base = index.base;

    // Search word data
    const wordMatches = [];
    for (const [hebrew, data] of Object.entries(index.words)) {
        let matched = false;
        let matchType = '';

        if (isHebrew && hebrew.includes(query)) {
            matched = true;
            matchType = 'Hebrew match';
        } else if (!isHebrew) {
            const def = (data.definition || '').toLowerCase();
            const trans = (data.transliteration || '').toLowerCase();
            const strongs = (data.strongs || '').toLowerCase();

            if (def.includes(q)) {
                matched = true;
                matchType = 'Definition';
            } else if (trans.includes(q)) {
                matched = true;
                matchType = 'Transliteration';
            } else if (strongs && strongs.includes(q)) {
                matched = true;
                matchType = "Strong's";
            }
        }

        if (matched) {
            wordMatches.push({ hebrew: hebrew, data: data, matchType: matchType });
        }
    }

    // Gematria search
    const gematriaMatches = [];
    if (/^\d+$/.test(query)) {
        const num = parseInt(query);
        for (const [hebrew, data] of Object.entries(index.words)) {
            if (data.gematria === num) {
                gematriaMatches.push({ hebrew: hebrew, data: data });
            }
        }
    }

    // Build results HTML
    let html = '';

    if (wordMatches.length > 0) {
        html += '<div class="search-section-label">Words (' + wordMatches.length + ')</div>';
        const shown = wordMatches.slice(0, 60);
        for (const wm of shown) {
            const d = wm.data;
            const def = d.definition || '';
            const trans = d.transliteration || '';
            const occ = d.first_occurrence || '';
            const strongs = d.strongs || '';
            const gematria = d.gematria || '';

            // Build occurrence link
            let occLink = '';
            if (occ) {
                const parts = occ.match(/^(.+?)\s+(\d+):(\d+)/);
                if (parts) {
                    const bookName = parts[1].toLowerCase().replace(/\s+/g, '_');
                    const ch = parts[2];
                    occLink = '<a href="' + base + '/' + bookName + '/' + ch + '.html" class="search-verse-link">' + occ + '</a>';
                }
            }

            html += '<div class="search-result-item">' +
                '<div class="search-result-word">' +
                    '<span class="search-hebrew">' + wm.hebrew + '</span>' +
                    '<span class="search-trans">' + escapeHtml(trans) + '</span>' +
                    (strongs ? '<span class="search-strongs">' + strongs + '</span>' : '') +
                    (gematria ? '<span class="search-gematria-val">G:' + gematria + '</span>' : '') +
                    '<span class="search-match-type">' + wm.matchType + '</span>' +
                '</div>' +
                '<div class="search-result-def">' + escapeHtml(def) + '</div>' +
                (occLink ? '<div class="search-result-locations">' + occLink + '</div>' : '') +
            '</div>';
        }
        if (wordMatches.length > 60) {
            html += '<div class="search-more">... and ' +
                (wordMatches.length - 60) + ' more word matches</div>';
        }
    }

    if (gematriaMatches.length > 0) {
        html += '<div class="search-section-label">Gematria = ' + query +
            ' (' + gematriaMatches.length + ')</div>';
        for (const gm of gematriaMatches) {
            html += '<div class="search-result-item">' +
                '<span class="search-hebrew">' + gm.hebrew + '</span> ' +
                '<span class="search-trans">' + escapeHtml(gm.data.transliteration || '') + '</span> ' +
                '<span class="search-gematria-val">G:' + gm.data.gematria + '</span>' +
                '<div class="search-result-def">' + escapeHtml(gm.data.definition || '') + '</div>' +
            '</div>';
        }
    }

    if (wordMatches.length === 0 && gematriaMatches.length === 0) {
        html = '<div class="search-empty">No results for "' + escapeHtml(query) + '"</div>';
    }

    const total = wordMatches.length + gematriaMatches.length;
    if (total > 0) {
        html = '<div class="search-summary">' + total + ' result' +
            (total !== 1 ? 's' : '') + ' found</div>' + html;
    }

    resultsDiv.innerHTML = html;
}


function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


// Keyboard shortcut: Ctrl+F opens search
document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        if (document.activeElement &&
            (document.activeElement.tagName === 'INPUT' ||
             document.activeElement.tagName === 'TEXTAREA')) {
            return;
        }
        e.preventDefault();
        openSearch();
    }
});
