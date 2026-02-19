/**
 * Word Evolution Modal - Mechanical Bible
 * Priority Loading + IndexedDB Caching
 *
 * Loading Strategy:
 * 1. Check IndexedDB for cached full lexicon (instant)
 * 2. If not cached, load priority words first (~1MB, 923 words)
 * 3. Background load full lexicon (~78MB, 58,400 words)
 * 4. Store in IndexedDB for future visits
 *
 * Copyright (c) 2026 Tammy L Casey. All rights reserved.
 */

// ============================================================================
// BASE PATH - resolves relative paths for both root and subdirectory pages
// ============================================================================

const WORD_MODAL_BASE = (function() {
    // For http/https: use root-relative paths (works on web servers)
    if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
        return '/';
    }
    // For file:// protocol: detect base from script src
    const scripts = document.getElementsByTagName('script');
    for (let i = 0; i < scripts.length; i++) {
        const src = scripts[i].src || '';
        if (src.includes('/js/word-modal.js')) {
            const idx = src.indexOf('/js/word-modal.js');
            return src.substring(0, idx + 1);
        }
    }
    // Fallback for file:// when script detection fails
    const path = window.location.pathname;
    const parts = path.split('/').filter(Boolean);
    if (parts.length >= 2 && parts[parts.length - 1].endsWith('.html')) {
        return '../';
    }
    return '';
})();

// ============================================================================
// STATE
// ============================================================================

let wordData = null;
let hebrewDefs = null;  // Hebrew definitions keyed by Hebrew word
let greekMapping = null; // Hebrew to Greek Septuagint mapping
let timelineData = null; // Separate timeline data for all 58,400 words
let priorityLoaded = false;
let fullLoaded = false;
let defsLoaded = false;
let greekLoaded = false;
let timelinesLoaded = false;
let loadingStatus = 'idle'; // 'idle', 'priority', 'full', 'cached'

const DB_NAME = 'MechanicalBibleDB';
const DB_VERSION = 7;  // v7: Load timelines immediately with words (parallel loading)
const STORE_NAME = 'wordData';

// Hebrew prefix characters that can be stripped for root lookup
const HEBREW_PREFIXES = ['ה', 'ב', 'כ', 'ל', 'מ', 'ו', 'ש'];

// ============================================================================
// INDEXEDDB FUNCTIONS
// ============================================================================

function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains(STORE_NAME)) {
                db.createObjectStore(STORE_NAME);
            }
        };
    });
}

async function getFromIndexedDB(key) {
    try {
        const db = await openDatabase();
        return new Promise((resolve, reject) => {
            const tx = db.transaction(STORE_NAME, 'readonly');
            const store = tx.objectStore(STORE_NAME);
            const request = store.get(key);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    } catch (e) {
        console.warn('[WARN] IndexedDB not available:', e.message);
        return null;
    }
}

async function saveToIndexedDB(key, value) {
    try {
        const db = await openDatabase();
        return new Promise((resolve, reject) => {
            const tx = db.transaction(STORE_NAME, 'readwrite');
            const store = tx.objectStore(STORE_NAME);
            const request = store.put(value, key);
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    } catch (e) {
        console.warn('[WARN] Could not save to IndexedDB:', e.message);
    }
}

// ============================================================================
// LOADING FUNCTIONS
// ============================================================================

async function loadHebrewDefinitions() {
    if (defsLoaded && hebrewDefs) return hebrewDefs;

    try {
        const response = await fetch(WORD_MODAL_BASE + 'data/hebrew_definitions.json');
        if (response.ok) {
            hebrewDefs = await response.json();
            defsLoaded = true;
            console.log('[OK] Hebrew definitions loaded: ' + Object.keys(hebrewDefs).length + ' entries');
        }
    } catch (e) {
        console.warn('[WARN] Could not load Hebrew definitions:', e.message);
    }
    return hebrewDefs;
}

async function loadGreekMapping() {
    if (greekLoaded && greekMapping) return greekMapping;

    try {
        const response = await fetch(WORD_MODAL_BASE + 'data/hebrew_greek_mapping.json');
        if (response.ok) {
            greekMapping = await response.json();
            greekLoaded = true;
            console.log('[OK] Hebrew-Greek mapping loaded: ' + Object.keys(greekMapping).length + ' entries');
        }
    } catch (e) {
        console.warn('[WARN] Could not load Greek mapping:', e.message);
    }
    return greekMapping;
}

async function loadWordData() {
    // Already have full data
    if (fullLoaded && wordData) {
        // Make sure timelines are also loading
        if (!timelinesLoaded) loadTimelinesInBackground();
        return wordData;
    }

    // Check IndexedDB first (instant if cached)
    if (loadingStatus === 'idle') {
        loadingStatus = 'checking';

        // Load cached words and timelines in parallel
        const [cachedWords, cachedTimelines] = await Promise.all([
            getFromIndexedDB('fullLexicon'),
            getFromIndexedDB('timelines')
        ]);

        if (cachedWords && Object.keys(cachedWords).length > 50000) {
            wordData = cachedWords;
            fullLoaded = true;
            priorityLoaded = true;
            loadingStatus = 'cached';
            console.log('[OK] Loaded ' + Object.keys(cachedWords).length + ' words from IndexedDB cache');
        }

        if (cachedTimelines && Object.keys(cachedTimelines).length > 50000) {
            timelineData = cachedTimelines;
            timelinesLoaded = true;
            console.log('[OK] Loaded ' + Object.keys(cachedTimelines).length + ' timelines from IndexedDB cache');
        }

        if (wordData) {
            // Start background loading for anything not cached
            if (!timelinesLoaded) loadTimelinesInBackground();
            return wordData;
        }
    }

    // Load priority words first (fast, ~1MB)
    if (!priorityLoaded) {
        loadingStatus = 'priority';
        try {
            const response = await fetch(WORD_MODAL_BASE + 'words-priority.json');
            if (response.ok) {
                const priority = await response.json();
                wordData = priority;
                priorityLoaded = true;
                console.log('[OK] Priority words loaded: ' + Object.keys(priority).length + ' words (modal ready)');

                // Start background load of full lexicon AND timelines
                loadFullLexiconInBackground();
                loadTimelinesInBackground();
            }
        } catch (e) {
            console.warn('[WARN] Priority words failed, loading full lexicon:', e.message);
        }
    }

    // If priority failed, fall back to full load
    if (!wordData) {
        return loadFullLexicon();
    }

    return wordData;
}

async function loadFullLexicon() {
    loadingStatus = 'full';
    updateLoadingIndicator('Loading complete lexicon (58,400 words)...');

    const response = await fetch(WORD_MODAL_BASE + 'words.json');
    if (!response.ok) {
        throw new Error('Failed to load word data');
    }

    const data = await response.json();
    wordData = data;
    fullLoaded = true;
    loadingStatus = 'cached';

    console.log('[OK] Full lexicon loaded: ' + Object.keys(data).length + ' words');

    // Save to IndexedDB for future visits
    saveToIndexedDB('fullLexicon', data)
        .then(() => console.log('[OK] Lexicon cached in IndexedDB'))
        .catch(e => console.warn('[WARN] IndexedDB save failed:', e.message));

    return data;
}

function loadFullLexiconInBackground() {
    // Don't block - load in background after priority is ready
    setTimeout(async () => {
        if (fullLoaded) return;

        console.log('[INFO] Background loading full lexicon...');
        loadingStatus = 'full';

        try {
            const response = await fetch(WORD_MODAL_BASE + 'words.json');
            if (response.ok) {
                const data = await response.json();
                wordData = data;
                fullLoaded = true;
                loadingStatus = 'cached';

                console.log('[OK] Full lexicon loaded in background: ' + Object.keys(data).length + ' words');

                // Save to IndexedDB
                saveToIndexedDB('fullLexicon', data)
                    .then(() => console.log('[OK] Lexicon cached in IndexedDB'))
                    .catch(e => console.warn('[WARN] IndexedDB save failed:', e.message));
            }
        } catch (e) {
            console.warn('[WARN] Background load failed:', e.message);
        }

        // Also load timelines in background
        loadTimelinesInBackground();
    }, 2000); // Start after 2 seconds
}

async function loadTimelinesInBackground() {
    if (timelinesLoaded) return;

    // Check IndexedDB first
    const cached = await getFromIndexedDB('timelines');
    if (cached && Object.keys(cached).length > 50000) {
        timelineData = cached;
        timelinesLoaded = true;
        console.log('[OK] Loaded ' + Object.keys(cached).length + ' timelines from IndexedDB cache');
        return;
    }

    console.log('[INFO] Background loading timelines...');

    try {
        const response = await fetch(WORD_MODAL_BASE + 'timelines.json');
        if (response.ok) {
            const data = await response.json();
            timelineData = data;
            timelinesLoaded = true;

            console.log('[OK] Timelines loaded: ' + Object.keys(data).length + ' timelines');

            // Save to IndexedDB
            saveToIndexedDB('timelines', data)
                .then(() => console.log('[OK] Timelines cached in IndexedDB'))
                .catch(e => console.warn('[WARN] Timelines IndexedDB save failed:', e.message));
        }
    } catch (e) {
        console.warn('[WARN] Timelines load failed:', e.message);
    }
}

function getTimelineForWord(hebrew) {
    // First check if word has embedded timeline (Genesis 1:1 scholarly words)
    const word = wordData?.[hebrew];
    if (word?.corruption_timeline?.stage_1?.scholarly_debate) {
        return word.corruption_timeline;
    }

    // Then check separate timelines data
    if (timelineData?.[hebrew]) {
        return timelineData[hebrew];
    }

    return null;
}

function updateLoadingIndicator(message) {
    const body = document.querySelector('.word-modal-body');
    if (body) {
        body.innerHTML = `
            <div class="word-modal-loading">
                ${message}<br>
                <small>This only happens once - data is cached for instant access.</small>
            </div>
        `;
    }
}

// ============================================================================
// DEFINITION LOOKUP FUNCTIONS
// ============================================================================

/**
 * Look up definition for a Hebrew word
 * Tries exact match first, then strips prefixes to find root word
 */
function lookupDefinition(hebrew) {
    if (!hebrewDefs) return null;

    // Try exact match first
    if (hebrewDefs[hebrew]) {
        return hebrewDefs[hebrew];
    }

    // Try stripping common prefixes
    for (const prefix of HEBREW_PREFIXES) {
        if (hebrew.startsWith(prefix) && hebrew.length > 1) {
            const stripped = hebrew.substring(1);
            if (hebrewDefs[stripped]) {
                // Return with note about prefix
                const def = { ...hebrewDefs[stripped] };
                def.hasPrefix = true;
                def.prefixNote = `(with prefix ${prefix})`;
                return def;
            }
        }
    }

    // Try stripping two prefixes (e.g., וה = and + the)
    if (hebrew.length > 2) {
        for (const prefix1 of HEBREW_PREFIXES) {
            for (const prefix2 of HEBREW_PREFIXES) {
                if (hebrew.startsWith(prefix1 + prefix2)) {
                    const stripped = hebrew.substring(2);
                    if (hebrewDefs[stripped]) {
                        const def = { ...hebrewDefs[stripped] };
                        def.hasPrefix = true;
                        def.prefixNote = `(with prefixes ${prefix1}${prefix2})`;
                        return def;
                    }
                }
            }
        }
    }

    return null;
}

/**
 * Look up Greek Septuagint translation for a Hebrew word
 */
function lookupGreek(hebrew) {
    if (!greekMapping) return null;

    // Try exact match
    if (greekMapping[hebrew]) {
        return greekMapping[hebrew];
    }

    // Try stripping prefixes
    for (const prefix of HEBREW_PREFIXES) {
        if (hebrew.startsWith(prefix) && hebrew.length > 1) {
            const stripped = hebrew.substring(1);
            if (greekMapping[stripped]) {
                return greekMapping[stripped];
            }
        }
    }

    return null;
}

// ============================================================================
// TIMELINE BUILDER
// ============================================================================

function buildTimelineStages(word, pictographic, septuagintDisplay, ntGreekDisplay, vulgateDisplay, kjvDisplay, definition, timeline) {
    // Get timeline from separate timelines.json or embedded in word
    const ct = getTimelineForWord(word.hebrew) || word.corruption_timeline;

    if (ct) {
        // Handle both formats: full (stage_1) and compact (1)
        const s1 = ct.stage_1 || ct['1'] || {};
        const s2 = ct.stage_2 || ct['2'] || {};
        const s3 = ct.stage_3 || ct['3'] || {};
        const s4 = ct.stage_4 || ct['4'] || {};
        const s5 = ct.stage_5 || ct['5'] || {};
        const s6 = ct.stage_6 || ct['6'] || {};

        // Get values with fallbacks (n=name, p=period, t=text, m=meaning, d=scholarly_debate, tr=transliteration)
        const getName = (s, def) => s.name || s.n || def;
        const getPeriod = (s, def) => s.period || s.p || def;
        const getText = (s, def) => s.text || s.t || def;
        const getMeaning = (s, def) => s.meaning || s.m || def;
        const getDebate = (s) => s.scholarly_debate || s.d || s.mechanism || '';
        const getTranslit = (s) => s.transliteration || s.tr || '';

        // Use detailed corruption timeline
        return `
            <div class="word-timeline-stage">
                <div class="word-timeline-num">1</div>
                <div class="word-timeline-content">
                    <strong>${getName(s1, 'Original Hebrew')}</strong>
                    <span class="word-timeline-period">(${getPeriod(s1, 'Ancient')})</span><br>
                    <span class="word-timeline-hebrew">${word.hebrew}</span><br>
                    <em class="original-meaning">${getMeaning(s1, pictographic)}</em><br>
                    <small class="mechanism">${getDebate(s1)}</small>
                </div>
            </div>
            <div class="word-timeline-stage">
                <div class="word-timeline-num">2</div>
                <div class="word-timeline-content">
                    <strong>${getName(s2, 'Septuagint Greek')}</strong>
                    <span class="word-timeline-period">(${getPeriod(s2, '280 BCE')})</span><br>
                    ${getText(s2, '') ? `<span class="greek-word">${getText(s2, '')}</span>` : ''}
                    ${getTranslit(s2) ? ` (${getTranslit(s2)})` : ''}<br>
                    <em>${getMeaning(s2, septuagintDisplay)}</em><br>
                    <small class="mechanism decay">${getDebate(s2)}</small>
                </div>
            </div>
            <div class="word-timeline-stage">
                <div class="word-timeline-num">3</div>
                <div class="word-timeline-content">
                    <strong>${getName(s3, 'NT Greek')}</strong>
                    <span class="word-timeline-period">(${getPeriod(s3, '100 CE')})</span><br>
                    ${getText(s3, '') ? `<span class="greek-word">${getText(s3, '')}</span>` : ''}<br>
                    <em>${getMeaning(s3, ntGreekDisplay)}</em><br>
                    <small class="mechanism decay">${getDebate(s3)}</small>
                </div>
            </div>
            <div class="word-timeline-stage">
                <div class="word-timeline-num">4</div>
                <div class="word-timeline-content">
                    <strong>${getName(s4, 'Latin Vulgate')}</strong>
                    <span class="word-timeline-period">(${getPeriod(s4, '400 CE')})</span><br>
                    <em>${getText(s4, '(Latin)')}</em><br>
                    <em>${getMeaning(s4, vulgateDisplay)}</em><br>
                    <small class="mechanism decay">${getDebate(s4)}</small>
                </div>
            </div>
            <div class="word-timeline-stage">
                <div class="word-timeline-num">5</div>
                <div class="word-timeline-content">
                    <strong>${getName(s5, 'King James')}</strong>
                    <span class="word-timeline-period">(${getPeriod(s5, '1611 CE')})</span><br>
                    <em>${getText(s5, kjvDisplay)}</em><br>
                    <small class="mechanism decay">${getDebate(s5)}</small>
                </div>
            </div>
            <div class="word-timeline-stage corrupted">
                <div class="word-timeline-num">6</div>
                <div class="word-timeline-content">
                    <strong>${getName(s6, 'Modern English')}</strong>
                    <span class="word-timeline-period">(${getPeriod(s6, 'Today')})</span><br>
                    <em class="corrupted-meaning">${getMeaning(s6, definition)}</em><br>
                    <small class="mechanism decay final">${getDebate(s6)}</small>
                </div>
            </div>
        `;
    }

    // Default timeline for non-control words
    return `
        <div class="word-timeline-stage">
            <div class="word-timeline-num">1</div>
            <div class="word-timeline-content">
                <strong>Hebrew Original</strong>
                <span class="word-timeline-period">(Ancient)</span><br>
                <span class="word-timeline-hebrew">${word.hebrew}</span><br>
                ${pictographic || 'Pictographic meaning from letters'}
            </div>
        </div>
        <div class="word-timeline-stage">
            <div class="word-timeline-num">2</div>
            <div class="word-timeline-content">
                <strong>Septuagint (LXX)</strong>
                <span class="word-timeline-period">(280 BCE)</span><br>
                <em>${septuagintDisplay}</em>
            </div>
        </div>
        <div class="word-timeline-stage">
            <div class="word-timeline-num">3</div>
            <div class="word-timeline-content">
                <strong>New Testament Greek</strong>
                <span class="word-timeline-period">(100 CE)</span><br>
                <em>${ntGreekDisplay}</em>
            </div>
        </div>
        <div class="word-timeline-stage">
            <div class="word-timeline-num">4</div>
            <div class="word-timeline-content">
                <strong>Latin Vulgate</strong>
                <span class="word-timeline-period">(400 CE)</span><br>
                <em>${vulgateDisplay}</em>
            </div>
        </div>
        <div class="word-timeline-stage">
            <div class="word-timeline-num">5</div>
            <div class="word-timeline-content">
                <strong>King James Version</strong>
                <span class="word-timeline-period">(1611 CE)</span><br>
                <em>${kjvDisplay}</em>
            </div>
        </div>
        <div class="word-timeline-stage">
            <div class="word-timeline-num">6</div>
            <div class="word-timeline-content">
                <strong>Modern English</strong>
                <span class="word-timeline-period">(Today)</span><br>
                ${definition || timeline.modern || 'See pictographic meaning'}
            </div>
        </div>
    `;
}

// ============================================================================
// MODAL FUNCTIONS
// ============================================================================

async function showWordEvolution(hebrew) {
    const modal = document.getElementById('wordModal');
    if (!modal) {
        console.error('[FAIL] Modal element not found');
        return;
    }

    const body = modal.querySelector('.word-modal-body');

    // Show modal with loading
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';

    // Check if we already have the word
    if (wordData && wordData[hebrew]) {
        body.innerHTML = buildWordHTML(wordData[hebrew]);
        return;
    }

    // Show loading
    if (loadingStatus === 'cached') {
        body.innerHTML = '<div class="word-modal-loading">Looking up word...</div>';
    } else if (loadingStatus === 'priority') {
        body.innerHTML = '<div class="word-modal-loading">Loading priority words...</div>';
    } else {
        body.innerHTML = '<div class="word-modal-loading">Loading word database...</div>';
    }

    // Load data
    try {
        const data = await loadWordData();
        const word = data[hebrew];

        if (!word) {
            // Word not in priority - try waiting for full load
            if (!fullLoaded) {
                body.innerHTML = `
                    <div class="word-modal-loading">
                        Loading complete lexicon for: ${hebrew}<br>
                        <small>This word is not in the priority set. Loading full database...</small>
                    </div>
                `;

                // Wait for full lexicon
                await loadFullLexicon();
                const fullWord = wordData[hebrew];
                if (fullWord) {
                    body.innerHTML = buildWordHTML(fullWord);
                    return;
                }
            }

            body.innerHTML = `
                <div class="word-modal-loading">
                    Word not found: ${hebrew}<br>
                    <small>This word may not be in our database yet.</small>
                </div>
            `;
            return;
        }

        body.innerHTML = buildWordHTML(word);
    } catch (error) {
        body.innerHTML = `
            <div class="word-modal-loading">
                Error loading word data.<br>
                <small>${error.message}</small>
            </div>
        `;
    }
}

function buildWordHTML(word) {
    // Look up definition from Hebrew definitions database (secondary source)
    const def = lookupDefinition(word.hebrew);

    // Primary: Use data from words.json (now has all 58,400 definitions)
    // Secondary: Fall back to hebrew_definitions.json lookup
    const translit = word.transliteration || def?.transliteration || '';
    const definition = word.definition || def?.definition || '';
    const strongs = word.strongs || def?.strongs || '';
    const prefixNote = def?.prefixNote || '';

    // Build letter table rows
    let letterRows = '';
    const letters = def?.letters || word.letters || [];
    if (letters && letters.length > 0) {
        for (const letter of letters) {
            // Handle both formats (from word.letters and def.letters)
            const char = letter.char || letter.letter || '';
            const name = letter.name || '';
            const value = letter.value || '';
            const pictograph = letter.pictograph || letter.proto_sinaitic || '';
            const concrete = letter.concrete || '';
            const abstract = letter.abstract || '';

            letterRows += `
                <tr>
                    <td style="font-size:1.5rem">${char}</td>
                    <td>${name}</td>
                    <td>${value}</td>
                    <td>${pictograph}</td>
                    <td>${concrete}</td>
                    <td>${abstract}</td>
                </tr>
            `;
        }
    }

    // Build timeline - get Greek from mapping if available
    const timeline = word.timeline || {};
    const greek = lookupGreek(word.hebrew);

    // Build Septuagint display
    let septuagintDisplay = timeline.septuagint || '';
    if (greek) {
        septuagintDisplay = `<span class="greek-word">${greek.greek}</span> (${greek.translit}) - "${greek.meaning}"`;
    } else if (!septuagintDisplay) {
        septuagintDisplay = '(Research in progress)';
    }

    // NT Greek - often same as LXX for theological terms
    let ntGreekDisplay = timeline.nt_greek || '';
    if (greek && !ntGreekDisplay) {
        ntGreekDisplay = `<span class="greek-word">${greek.greek}</span> (${greek.translit})`;
    } else if (!ntGreekDisplay) {
        ntGreekDisplay = '(Research in progress)';
    }

    // Latin Vulgate
    const vulgateDisplay = def?.vulgate_translation || timeline.vulgate || '(Research in progress)';

    // KJV
    const kjvDisplay = def?.kjv_translation || timeline.kjv || '(Research in progress)';

    // Pictographic meaning - prefer from definitions if available
    const pictographic = def?.pictographic_meaning || word.pictographic || '';

    return `
        <div class="word-header-section">
            <div class="word-language-badge">Hebrew</div>
            <div class="word-hebrew-large">${word.hebrew}</div>
            ${translit ? `<div class="word-translit">(${translit}) ${prefixNote}</div>` : ''}
            ${definition ? `<div class="word-definition"><strong>Meaning:</strong> ${definition}</div>` : ''}
        </div>

        <div class="word-stats-row">
            <div class="word-stat-box">
                <div class="word-stat-value">${strongs || 'N/A'}</div>
                <div class="word-stat-label">Strong's #</div>
            </div>
            <div class="word-stat-box">
                <div class="word-stat-value">${word.gematria || def?.gematria || 'N/A'}</div>
                <div class="word-stat-label">Gematria</div>
            </div>
            <div class="word-stat-box">
                <div class="word-stat-value">${word.digital_root || def?.digital_root || 'N/A'}</div>
                <div class="word-stat-label">Digital Root</div>
            </div>
            <div class="word-stat-box">
                <div class="word-stat-value">${word.frequency || def?.frequency || 'N/A'}</div>
                <div class="word-stat-label">Occurrences</div>
            </div>
        </div>

        <h3 class="word-section-header">Pictographic Meaning</h3>
        <div class="word-pictographic">${pictographic || 'See letter analysis below'}</div>

        <h3 class="word-section-header">Letter-by-Letter Analysis</h3>
        <table class="word-letter-table">
            <tr>
                <th>Hebrew</th>
                <th>Name</th>
                <th>Value</th>
                <th>Pictograph</th>
                <th>Concrete</th>
                <th>Abstract</th>
            </tr>
            ${letterRows}
        </table>

        <p><strong>First Occurrence:</strong> ${word.first_occurrence || def?.first_occurrence || 'N/A'}</p>

        <h3 class="word-section-header">6-Stage Corruption Timeline</h3>
        ${word.is_control_word ? `<div class="control-word-badge">[!] CONTROL WORD - Meaning deliberately altered</div>` : ''}
        ${word.control_mechanism ? `<div class="control-mechanism"><strong>Decay:</strong> ${word.control_mechanism}</div>` : ''}
        <div class="word-timeline">
            ${buildTimelineStages(word, pictographic, septuagintDisplay, ntGreekDisplay, vulgateDisplay, kjvDisplay, definition, timeline)}
        </div>

        <div class="word-sources">
            <strong>Sources:</strong><br>
            - Strong's Concordance (${strongs || 'N/A'})<br>
            - Ancient Hebrew Lexicon of the Bible (AHLB, Jeff Benner)<br>
            - Proto-Sinaitic pictograph analysis<br>
            - Masoretic Text concordance
        </div>
    `;
}

function closeWordModal() {
    const modal = document.getElementById('wordModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

function initWordModal() {
    // Create modal if it doesn't exist
    if (!document.getElementById('wordModal')) {
        const modalHTML = `
            <div id="wordModal" class="word-modal">
                <div class="word-modal-content">
                    <button class="word-modal-close" onclick="closeWordModal()">&times;</button>
                    <div class="word-modal-body"></div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }

    // Close on overlay click
    const modal = document.getElementById('wordModal');
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeWordModal();
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeWordModal();
        }
    });

    // Load Hebrew definitions (2.2 MB - has all 1,640 words with definitions)
    loadHebrewDefinitions().catch(() => {});

    // Load Hebrew-Greek mapping for timeline
    loadGreekMapping().catch(() => {});

    // Start loading immediately (check IndexedDB, then priority, then background full)
    loadWordData().catch(() => {});
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWordModal);
} else {
    initWordModal();
}
