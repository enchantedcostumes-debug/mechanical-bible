/**
 * Translation Layers - Mechanical Bible
 * =======================================
 * Manages dynamic translation layers:
 *   Layer 1: MECH (baked in HTML)
 *   Layer 2: RMT (baked in HTML)
 *   Layer 3: ORACLE (loaded from data/oracle/<book>.json)
 *   Layer 4: TOGGLE (user picks: JPS default, KJV, WEB, ASV, etc. via bible-api.com)
 *
 * Copyright (c) 2026 Tammy L Casey. All rights reserved.
 */

(function() {
    'use strict';

    // Available toggle translations
    const TRANSLATIONS = [
        { id: 'jps',   label: 'JPS: ',   name: 'Jewish Publication Society' },
        { id: 'kjv',   label: 'KJV: ',   name: 'King James Version' },
        { id: 'web',   label: 'WEB: ',   name: 'World English Bible' },
        { id: 'bbe',   label: 'BBE: ',   name: 'Bible in Basic English' },
        { id: 'darby', label: 'DARBY: ', name: 'Darby Translation' },
        { id: 'ylt',   label: 'YLT: ',   name: "Young's Literal Translation" },
        { id: 'asv',   label: 'ASV: ',   name: 'American Standard Version' }
    ];

    // JPS text cache (extracted from baked HTML before converting)
    const jpsCache = {};
    // Oracle data cache per book
    const oracleCache = {};
    // Toggle translation cache
    const toggleCache = {};

    let bookFolder = '';
    let chapterNum = 0;

    // Detect base path (works for both subdirectory and root)
    const BASE = (function() {
        const path = window.location.pathname;
        const parts = path.split('/').filter(Boolean);
        if (parts.length >= 2 && parts[parts.length - 1].endsWith('.html')) {
            return '../';
        }
        return '';
    })();

    // Map folder names to bible-api.com names
    const API_BOOK_MAP = {
        'genesis': 'genesis', 'exodus': 'exodus', 'leviticus': 'leviticus',
        'numbers': 'numbers', 'deuteronomy': 'deuteronomy', 'joshua': 'joshua',
        'judges': 'judges', 'ruth': 'ruth', '1_samuel': '1samuel',
        '2_samuel': '2samuel', '1_kings': '1kings', '2_kings': '2kings',
        '1_chronicles': '1chronicles', '2_chronicles': '2chronicles',
        'ezra': 'ezra', 'nehemiah': 'nehemiah', 'esther': 'esther',
        'job': 'job', 'psalms': 'psalms', 'proverbs': 'proverbs',
        'ecclesiastes': 'ecclesiastes', 'song_of_songs': 'songofsolomon',
        'isaiah': 'isaiah', 'jeremiah': 'jeremiah', 'lamentations': 'lamentations',
        'ezekiel': 'ezekiel', 'daniel': 'daniel', 'hosea': 'hosea',
        'joel': 'joel', 'amos': 'amos', 'obadiah': 'obadiah',
        'jonah': 'jonah', 'micah': 'micah', 'nahum': 'nahum',
        'habakkuk': 'habakkuk', 'zephaniah': 'zephaniah', 'haggai': 'haggai',
        'zechariah': 'zechariah', 'malachi': 'malachi',
        'matthew': 'matthew', 'mark': 'mark', 'luke': 'luke', 'john': 'john',
        'acts': 'acts', 'romans': 'romans', '1_corinthians': '1corinthians',
        '2_corinthians': '2corinthians', 'galatians': 'galatians',
        'ephesians': 'ephesians', 'philippians': 'philippians',
        'colossians': 'colossians', '1_thessalonians': '1thessalonians',
        '2_thessalonians': '2thessalonians', '1_timothy': '1timothy',
        '2_timothy': '2timothy', 'titus': 'titus', 'philemon': 'philemon',
        'hebrews': 'hebrews', 'james': 'james', '1_peter': '1peter',
        '2_peter': '2peter', '1_john': '1john', '2_john': '2john',
        '3_john': '3john', 'jude': 'jude', 'revelation': 'revelation'
    };

    function init() {
        // Detect book folder and chapter from URL path
        const path = window.location.pathname;
        const parts = path.split('/').filter(Boolean);
        if (parts.length >= 2) {
            bookFolder = parts[parts.length - 2];
            const filename = parts[parts.length - 1];
            const m = filename.match(/^(\d+)\.html$/);
            if (m) chapterNum = parseInt(m[1]);
        }

        if (!bookFolder || !chapterNum) return;

        // 1. Extract JPS text from baked spans, cache it
        document.querySelectorAll('.translation .jps').forEach(function(span) {
            var verse = span.closest('.verse');
            if (verse) {
                var vnum = verse.id.replace(/^v\d+-/, '');
                jpsCache[vnum] = span.textContent.replace(/^\.?"?\s*/, '').trim();
            }
        });

        // 2. Convert JPS spans to toggle-translation spans
        document.querySelectorAll('.translation .jps').forEach(function(span) {
            span.className = 'toggle-translation';
            span.setAttribute('data-label', 'JPS: ');
        });

        // 3. Load Oracle data and inject
        loadOracle();

        // 4. Build toggle dropdown in toolbar
        buildSelector();
    }

    function loadOracle() {
        var url = BASE + 'data/oracle/' + bookFolder + '.json?v=' + Date.now();
        fetch(url)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                oracleCache[bookFolder] = data;
                var chData = data[String(chapterNum)];
                if (!chData) return;

                document.querySelectorAll('.translation').forEach(function(div) {
                    var verse = div.closest('.verse');
                    if (!verse) return;
                    var vnum = verse.id.replace(/^v\d+-/, '');
                    var vd = chData[vnum];
                    if (!vd) return;

                    // Get or create oracle span, then MOVE it to first position
                    var rs = div.querySelector('.oracle');
                    if (!rs) {
                        rs = document.createElement('span');
                        rs.className = 'oracle';
                    }
                    // Always insert as FIRST child (moves existing or places new)
                    div.insertBefore(rs, div.firstChild);
                    rs.textContent = vd.text || '';
                });
            })
            .catch(function() {
                // Oracle data not available for this book (e.g. NT books)
            });
    }

    function buildSelector() {
        var toolbar = document.querySelector('.view-toolbar');
        if (!toolbar) return;

        var div = document.createElement('div');
        div.className = 'translation-selector';
        var lbl = document.createElement('label');
        lbl.textContent = '5th:';
        var sel = document.createElement('select');
        sel.id = 'translationSelect';

        TRANSLATIONS.forEach(function(t) {
            var opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = t.name;
            if (t.id === 'jps') opt.selected = true;
            sel.appendChild(opt);
        });

        sel.addEventListener('change', function() {
            switchToggle(this.value);
        });

        div.appendChild(lbl);
        div.appendChild(sel);
        toolbar.appendChild(div);
    }

    function switchToggle(translationId) {
        var t = TRANSLATIONS.find(function(x) { return x.id === translationId; });
        if (!t) return;

        // Update labels
        document.querySelectorAll('.toggle-translation').forEach(function(span) {
            span.setAttribute('data-label', t.label);
            span.textContent = 'Loading...';
        });

        // JPS from cache
        if (translationId === 'jps') {
            document.querySelectorAll('.toggle-translation').forEach(function(span) {
                var verse = span.closest('.verse');
                if (verse) {
                    var vnum = verse.id.replace(/^v\d+-/, '');
                    span.textContent = jpsCache[vnum] || '';
                }
            });
            return;
        }

        // Check cache
        var cacheKey = bookFolder + '_' + chapterNum + '_' + translationId;
        if (toggleCache[cacheKey]) {
            applyToggleData(toggleCache[cacheKey]);
            return;
        }

        // Fetch from bible-api.com
        var apiBook = API_BOOK_MAP[bookFolder] || bookFolder;
        var url = 'https://bible-api.com/' + apiBook + '+' + chapterNum + '?translation=' + translationId;

        fetch(url)
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.verses) {
                    var verseMap = {};
                    data.verses.forEach(function(v) {
                        verseMap[v.verse] = v.text.trim();
                    });
                    toggleCache[cacheKey] = verseMap;
                    applyToggleData(verseMap);
                }
            })
            .catch(function() {
                document.querySelectorAll('.toggle-translation').forEach(function(span) {
                    span.textContent = '[unavailable for this translation]';
                });
            });
    }

    function applyToggleData(verseMap) {
        document.querySelectorAll('.toggle-translation').forEach(function(span) {
            var verse = span.closest('.verse');
            if (verse) {
                var vnum = verse.id.replace(/^v\d+-/, '');
                span.textContent = verseMap[vnum] || '';
            }
        });
    }

    // Init on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
