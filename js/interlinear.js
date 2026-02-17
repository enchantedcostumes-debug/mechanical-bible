/**
 * Interlinear View - Mechanical Bible
 * Shows Hebrew / transliteration / English aligned word-by-word.
 *
 * Adapted from Dead Sea Scrolls (Ge'ez) interlinear for Hebrew Bible.
 * Uses words.json (or words-priority.json) for transliteration + definition.
 *
 * Copyright (c) 2026 Tammy L Casey. All rights reserved.
 */

let interlinearMode = false;

// Hebrew transliteration table (standard academic)
const HEBREW_TRANSLIT = {
    '\u05D0': "'",    // Aleph
    '\u05D1': 'b',    // Beth
    '\u05D2': 'g',    // Gimel
    '\u05D3': 'd',    // Daleth
    '\u05D4': 'h',    // He
    '\u05D5': 'v',    // Vav
    '\u05D6': 'z',    // Zayin
    '\u05D7': 'ch',   // Cheth
    '\u05D8': 'ṭ',    // Teth
    '\u05D9': 'y',    // Yod
    '\u05DA': 'k',    // Kaf final
    '\u05DB': 'k',    // Kaf
    '\u05DC': 'l',    // Lamed
    '\u05DD': 'm',    // Mem final
    '\u05DE': 'm',    // Mem
    '\u05DF': 'n',    // Nun final
    '\u05E0': 'n',    // Nun
    '\u05E1': 's',    // Samekh
    '\u05E2': "'",    // Ayin
    '\u05E3': 'p',    // Pe final
    '\u05E4': 'p',    // Pe
    '\u05E5': 'ts',   // Tsade final
    '\u05E6': 'ts',   // Tsade
    '\u05E7': 'q',    // Qoph
    '\u05E8': 'r',    // Resh
    '\u05E9': 'sh',   // Shin
    '\u05EA': 't',    // Tav
};


function hebrewToTranslit(text) {
    let result = '';
    for (const ch of text) {
        result += HEBREW_TRANSLIT[ch] || ch;
    }
    return result;
}


function getWordGloss(hebrewWord) {
    // Try word data sources (loaded by word-modal.js)
    if (typeof wordData !== 'undefined' && wordData && wordData[hebrewWord]) {
        const d = wordData[hebrewWord];
        const def = d.definition || '';
        // Shorten to first phrase/clause
        if (def.length > 40) {
            const short = def.split(/[,;.]/)[0].trim();
            return short || def.substring(0, 35) + '...';
        }
        return def;
    }
    return '';
}


function getWordTranslit(hebrewWord) {
    if (typeof wordData !== 'undefined' && wordData && wordData[hebrewWord]) {
        const t = wordData[hebrewWord].transliteration;
        if (t) return t;
    }
    return hebrewToTranslit(hebrewWord);
}


function toggleInterlinear() {
    interlinearMode = !interlinearMode;

    const btn = document.getElementById('interlinear-toggle');
    if (btn) {
        btn.textContent = interlinearMode ? 'Normal View' : 'Interlinear View';
        btn.classList.toggle('active', interlinearMode);
    }

    // Disable parallel if active
    if (interlinearMode && typeof parallelMode !== 'undefined' && parallelMode) {
        toggleParallel();
    }

    const pBtn = document.getElementById('parallel-toggle');
    if (pBtn) {
        pBtn.disabled = interlinearMode;
        pBtn.style.opacity = interlinearMode ? '0.4' : '1';
    }

    const verses = document.querySelectorAll('.verse');
    verses.forEach(function(verse) {
        if (interlinearMode) {
            enableInterlinear(verse);
        } else {
            disableInterlinear(verse);
        }
    });
}


function enableInterlinear(verse) {
    if (verse.dataset.interlinearApplied === 'true') return;

    const textDiv = verse.querySelector('.original-text.hebrew') || verse.querySelector('.original-text.greek');
    if (!textDiv) return;

    const isGreek = textDiv.classList.contains('greek');
    const words = textDiv.querySelectorAll('.word');
    if (words.length === 0) return;

    verse.dataset.interlinearApplied = 'true';

    // Create interlinear container
    const ilContainer = document.createElement('div');
    ilContainer.className = 'interlinear-container';
    if (isGreek) ilContainer.style.direction = 'ltr';

    words.forEach(function(wordSpan) {
        const hebrewWord = wordSpan.textContent.trim();
        const translit = getWordTranslit(hebrewWord);
        const gloss = getWordGloss(hebrewWord);

        const ilWord = document.createElement('div');
        ilWord.className = 'interlinear-word';
        ilWord.onclick = function() { showWordEvolution(hebrewWord); };

        const hebrewDiv = document.createElement('div');
        hebrewDiv.className = 'il-hebrew';
        hebrewDiv.textContent = hebrewWord;

        const translitDiv = document.createElement('div');
        translitDiv.className = 'il-translit';
        translitDiv.textContent = translit;

        const glossDiv = document.createElement('div');
        glossDiv.className = 'il-gloss';
        glossDiv.textContent = gloss;

        ilWord.appendChild(hebrewDiv);
        ilWord.appendChild(translitDiv);
        ilWord.appendChild(glossDiv);
        ilContainer.appendChild(ilWord);
    });

    textDiv.style.display = 'none';
    textDiv.parentNode.insertBefore(ilContainer, textDiv.nextSibling);
    verse.classList.add('interlinear-active');
}


function disableInterlinear(verse) {
    if (verse.dataset.interlinearApplied !== 'true') return;

    const ilContainer = verse.querySelector('.interlinear-container');
    if (ilContainer) ilContainer.remove();

    const textDiv = verse.querySelector('.original-text.hebrew') || verse.querySelector('.original-text.greek');
    if (textDiv) textDiv.style.display = '';

    verse.dataset.interlinearApplied = 'false';
    verse.classList.remove('interlinear-active');

    const pBtn = document.getElementById('parallel-toggle');
    if (pBtn) {
        pBtn.disabled = false;
        pBtn.style.opacity = '1';
    }
}
