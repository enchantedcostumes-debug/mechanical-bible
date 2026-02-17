/**
 * Parallel View - Mechanical Bible
 * Side-by-side Hebrew original | English translation.
 *
 * Copyright (c) 2026 Tammy L Casey. All rights reserved.
 */

let parallelMode = false;

function toggleParallel() {
    parallelMode = !parallelMode;

    const btn = document.getElementById('parallel-toggle');
    if (btn) {
        btn.textContent = parallelMode ? 'Normal View' : 'Parallel View';
        btn.classList.toggle('active', parallelMode);
    }

    // Disable interlinear if active
    if (parallelMode && typeof interlinearMode !== 'undefined' && interlinearMode) {
        toggleInterlinear();
    }

    const ilBtn = document.getElementById('interlinear-toggle');
    if (ilBtn) {
        ilBtn.disabled = parallelMode;
        ilBtn.style.opacity = parallelMode ? '0.4' : '1';
    }

    const verses = document.querySelectorAll('.verse');
    verses.forEach(function(verse) {
        if (parallelMode) {
            enableParallel(verse);
        } else {
            disableParallel(verse);
        }
    });
}


function enableParallel(verse) {
    if (verse.dataset.parallelApplied === 'true') return;

    const textDiv = verse.querySelector('.original-text.hebrew') || verse.querySelector('.original-text.greek');
    const transDiv = verse.querySelector('.translation');
    if (!textDiv || !transDiv) return;

    verse.dataset.parallelApplied = 'true';

    const verseRef = verse.querySelector('.verse-ref');

    // Create parallel wrapper
    const wrapper = document.createElement('div');
    wrapper.className = 'parallel-verse';

    // Left column: Hebrew/Greek
    const isGreek = textDiv.classList.contains('greek');
    const hebCol = document.createElement('div');
    hebCol.className = 'parallel-hebrew';
    const hebLabel = document.createElement('div');
    hebLabel.className = 'parallel-label';
    hebLabel.textContent = isGreek ? 'Greek' : 'Hebrew';
    hebCol.appendChild(hebLabel);
    hebCol.appendChild(textDiv.cloneNode(true));

    // Right column: English
    const engCol = document.createElement('div');
    engCol.className = 'parallel-english';
    const engLabel = document.createElement('div');
    engLabel.className = 'parallel-label';
    engLabel.textContent = 'English';
    engCol.appendChild(engLabel);
    const engContent = document.createElement('div');
    engContent.className = 'parallel-english-text';
    engContent.textContent = transDiv.textContent;
    engCol.appendChild(engContent);

    wrapper.appendChild(hebCol);
    wrapper.appendChild(engCol);

    textDiv.style.display = 'none';
    transDiv.style.display = 'none';

    if (verseRef && verseRef.nextSibling) {
        verse.insertBefore(wrapper, verseRef.nextSibling);
    } else {
        verse.appendChild(wrapper);
    }

    verse.classList.add('parallel-active');
}


function disableParallel(verse) {
    if (verse.dataset.parallelApplied !== 'true') return;

    const wrapper = verse.querySelector('.parallel-verse');
    if (wrapper) wrapper.remove();

    const textDiv = verse.querySelector('.original-text.hebrew') || verse.querySelector('.original-text.greek');
    const transDiv = verse.querySelector('.translation');
    if (textDiv) textDiv.style.display = '';
    if (transDiv) transDiv.style.display = '';

    verse.dataset.parallelApplied = 'false';
    verse.classList.remove('parallel-active');

    const ilBtn = document.getElementById('interlinear-toggle');
    if (ilBtn) {
        ilBtn.disabled = false;
        ilBtn.style.opacity = '1';
    }
}
