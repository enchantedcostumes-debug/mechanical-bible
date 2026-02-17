/**
 * Grammar View - Mechanical Bible
 * Color-codes Hebrew words by part of speech.
 *
 * Uses words.json data (part_of_speech field if present)
 * and heuristic analysis for Hebrew morphology.
 *
 * Copyright (c) 2026 Tammy L Casey. All rights reserved.
 */

let grammarMode = false;

const POS_COLORS = {
    'noun':        { color: '#5bb8f0', label: 'Noun',        bg: 'rgba(91,184,240,0.15)' },
    'verb':        { color: '#f06060', label: 'Verb',        bg: 'rgba(240,96,96,0.15)' },
    'adjective':   { color: '#60d060', label: 'Adjective',   bg: 'rgba(96,208,96,0.15)' },
    'adverb':      { color: '#d0a040', label: 'Adverb',      bg: 'rgba(208,160,64,0.15)' },
    'preposition': { color: '#c080e0', label: 'Preposition', bg: 'rgba(192,128,224,0.15)' },
    'conjunction': { color: '#e0a060', label: 'Conjunction', bg: 'rgba(224,160,96,0.15)' },
    'pronoun':     { color: '#60c0c0', label: 'Pronoun',     bg: 'rgba(96,192,192,0.15)' },
    'proper':      { color: '#f0c040', label: 'Proper Noun', bg: 'rgba(240,192,64,0.15)' },
    'particle':    { color: '#a0a0a0', label: 'Particle',    bg: 'rgba(160,160,160,0.15)' },
    'number':      { color: '#e070b0', label: 'Number',      bg: 'rgba(224,112,176,0.15)' },
    'divine':      { color: '#ffd700', label: 'Divine Name', bg: 'rgba(255,215,0,0.15)' },
};

// Hebrew morphological patterns for heuristic POS detection
const HEBREW_POS_HINTS = {
    // Divine names
    '\u05D0\u05DC\u05D4\u05D9\u05DD': 'divine',  // Elohim
    '\u05D9\u05D4\u05D5\u05D4': 'divine',          // YHVH
    '\u05D0\u05D3\u05E0\u05D9': 'divine',          // Adonai
    '\u05D0\u05DC': 'divine',                        // El

    // Common conjunctions/particles
    '\u05D5': 'conjunction',   // ve (and)
    '\u05DB\u05D9': 'conjunction', // ki (because/that)
    '\u05D0\u05EA': 'particle',    // et (direct object marker)
    '\u05D0\u05DC': 'preposition', // el (to/toward)
    '\u05E2\u05DC': 'preposition', // al (upon)
    '\u05DE\u05DF': 'preposition', // min (from)
    '\u05D1': 'preposition',       // be (in)
    '\u05DC': 'preposition',       // le (to)
    '\u05D0\u05E9\u05E8': 'pronoun', // asher (which/who)
};


function getWordPOS(hebrewWord) {
    // Check words data for POS if available
    if (typeof wordData !== 'undefined' && wordData && wordData[hebrewWord]) {
        const d = wordData[hebrewWord];
        if (d.part_of_speech) return d.part_of_speech.toLowerCase();

        // Heuristic from definition
        const def = (d.definition || '').toLowerCase();
        if (def.match(/^(to |he |she |they |it )/)) return 'verb';
        if (def.match(/god|lord|yhwh|elohim/)) return 'divine';
    }

    // Check known words
    if (HEBREW_POS_HINTS[hebrewWord]) return HEBREW_POS_HINTS[hebrewWord];

    // Prefix heuristics
    if (hebrewWord.startsWith('\u05D5')) {
        // Starts with vav (and) - check rest
        const rest = hebrewWord.substring(1);
        if (rest.startsWith('\u05D9')) return 'verb'; // vav + yod prefix = imperfect verb
    }
    if (hebrewWord.startsWith('\u05D4')) {
        // Starts with he - could be article + noun
        if (hebrewWord.length > 2) return 'noun';
    }

    return '';
}


function toggleGrammar() {
    grammarMode = !grammarMode;

    const btn = document.getElementById('grammar-toggle');
    if (btn) {
        btn.textContent = grammarMode ? 'Normal Colors' : 'Grammar View';
        btn.classList.toggle('active', grammarMode);
    }

    // Build legend
    if (grammarMode) {
        buildGrammarLegend();
    }
    const legend = document.getElementById('grammar-legend');
    if (legend) legend.style.display = grammarMode ? 'flex' : 'none';

    const verses = document.querySelectorAll('.verse');
    verses.forEach(function(verse) {
        if (grammarMode) {
            enableGrammar(verse);
        } else {
            disableGrammar(verse);
        }
    });
}


function enableGrammar(verse) {
    const textDiv = verse.querySelector('.original-text.hebrew') || verse.querySelector('.original-text.greek');
    if (!textDiv) return;
    const words = textDiv.querySelectorAll('.word');
    words.forEach(function(span) {
        const hebrewWord = span.textContent.trim();
        const pos = getWordPOS(hebrewWord);
        if (pos && POS_COLORS[pos]) {
            const c = POS_COLORS[pos];
            span.style.color = c.color;
            span.style.backgroundColor = c.bg;
            span.style.borderBottom = '2px solid ' + c.color;
            span.title = c.label + ': ' + hebrewWord;
        }
    });
}


function disableGrammar(verse) {
    const textDiv = verse.querySelector('.original-text.hebrew') || verse.querySelector('.original-text.greek');
    if (!textDiv) return;
    const words = textDiv.querySelectorAll('.word');
    words.forEach(function(span) {
        span.style.color = '';
        span.style.backgroundColor = '';
        span.style.borderBottom = '';
        span.title = '';
    });
}


function buildGrammarLegend() {
    if (document.getElementById('grammar-legend')) return;

    const toolbar = document.querySelector('.view-toolbar');
    if (!toolbar) return;

    const legend = document.createElement('div');
    legend.id = 'grammar-legend';
    legend.className = 'grammar-legend';

    for (const [key, info] of Object.entries(POS_COLORS)) {
        const item = document.createElement('div');
        item.className = 'grammar-legend-item';

        const swatch = document.createElement('span');
        swatch.className = 'grammar-legend-swatch';
        swatch.style.backgroundColor = info.color;

        const label = document.createElement('span');
        label.textContent = info.label;

        item.appendChild(swatch);
        item.appendChild(label);
        legend.appendChild(item);
    }

    toolbar.parentNode.insertBefore(legend, toolbar.nextSibling);
}
