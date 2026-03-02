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

    // Available toggle translations (all English - via bible-api.com)
    const TRANSLATIONS = [
        { id: 'jps',    label: 'JPS: ',    name: 'Jewish Publication Society' },
        { id: 'kjv',    label: 'KJV: ',    name: 'King James Version' },
        { id: 'asv',    label: 'ASV: ',    name: 'American Standard Version' },
        { id: 'web',    label: 'WEB: ',    name: 'World English Bible' },
        { id: 'webbe',  label: 'WEBBE: ',  name: 'World English Bible (British)' },
        { id: 'bbe',    label: 'BBE: ',    name: 'Bible in Basic English' },
        { id: 'dra',    label: 'DRA: ',    name: 'Douay-Rheims 1899' },
        { id: 'darby',  label: 'DARBY: ',  name: 'Darby Translation' },
        { id: 'ylt',    label: 'YLT: ',    name: "Young's Literal Translation" },
        { id: 'oeb-us', label: 'OEB: ',    name: 'Open English Bible (US)' },
        { id: 'oeb-cw', label: 'OEB-CW: ', name: 'Open English Bible (Commonwealth)' }
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

    // Normalize HTML folder names (i_samuel etc.) to canonical names
    const FOLDER_NORMALIZE = {
        'i_samuel': '1_samuel', 'ii_samuel': '2_samuel',
        'i_kings': '1_kings', 'ii_kings': '2_kings',
        'i_chronicles': '1_chronicles', 'ii_chronicles': '2_chronicles'
    };

    // NT book set for OT/NT detection
    const NT_BOOKS = new Set([
        'matthew', 'mark', 'luke', 'john', 'acts', 'romans',
        '1_corinthians', '2_corinthians', 'galatians', 'ephesians',
        'philippians', 'colossians', '1_thessalonians', '2_thessalonians',
        '1_timothy', '2_timothy', 'titus', 'philemon',
        'hebrews', 'james', '1_peter', '2_peter',
        '1_john', '2_john', '3_john', 'jude', 'revelation'
    ]);

    let isNT = false;

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

        // Normalize folder names (i_samuel → 1_samuel, etc.)
        bookFolder = FOLDER_NORMALIZE[bookFolder] || bookFolder;

        // Detect OT vs NT
        isNT = NT_BOOKS.has(bookFolder);

        // 1. Handle toggle-translation spans
        var jpsSpans = document.querySelectorAll('.translation .jps');

        if (jpsSpans.length > 0) {
            // OT path: extract JPS text from baked spans, cache it
            jpsSpans.forEach(function(span) {
                var verse = span.closest('.verse');
                if (verse) {
                    var vnum = verse.id.replace(/^v\d+-/, '');
                    jpsCache[vnum] = span.textContent.replace(/^\.?"?\s*/, '').trim();
                }
            });
            // Convert JPS spans to toggle-translation spans
            jpsSpans.forEach(function(span) {
                span.className = 'toggle-translation';
                span.setAttribute('data-label', 'JPS: ');
            });
        } else {
            // NT path: create toggle-translation spans (no JPS text exists)
            document.querySelectorAll('.translation').forEach(function(div) {
                var span = document.createElement('span');
                span.className = 'toggle-translation';
                span.setAttribute('data-label', 'KJV: ');
                span.textContent = '';
                div.appendChild(span);
            });
        }

        // 2. Load Oracle data (OT only — no NT oracle files exist)
        if (!isNT) {
            loadOracle();
        }

        // 3. Build toggle dropdown in toolbar
        buildSelector();

        // 4. NT pages: auto-fetch default translation (KJV)
        if (isNT) {
            switchToggle('kjv');
        }
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

                    // Populate existing oracle span (CSS order handles display position)
                    var rs = div.querySelector('.oracle');
                    if (!rs) {
                        rs = document.createElement('span');
                        rs.className = 'oracle';
                        div.appendChild(rs);
                    }
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
        lbl.textContent = 'Translation:';
        var sel = document.createElement('select');
        sel.id = 'translationSelect';

        var defaultId = isNT ? 'kjv' : 'jps';
        TRANSLATIONS.forEach(function(t) {
            var opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = t.name;
            if (t.id === defaultId) opt.selected = true;
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

        // JPS from cache (OT only — NT has no baked JPS, falls through to API)
        if (translationId === 'jps' && !isNT) {
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
