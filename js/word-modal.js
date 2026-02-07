/**
 * Word Evolution Modal - Mechanical Bible
 * Loads word data and displays evolution report in modal
 */

// Word data cache
let wordData = null;
let wordDataLoading = false;
let wordDataPromise = null;

/**
 * Load word data from JSON file (once, cached)
 */
function loadWordData() {
    if (wordData) {
        return Promise.resolve(wordData);
    }

    if (wordDataPromise) {
        return wordDataPromise;
    }

    wordDataLoading = true;

    // Show loading indicator
    const modal = document.getElementById('wordModal');
    if (modal) {
        modal.querySelector('.word-modal-body').innerHTML = `
            <div class="word-modal-loading">
                Loading word database (58,400 words)...<br>
                <small>This only happens once - data is cached.</small>
            </div>
        `;
        modal.classList.add('show');
    }

    wordDataPromise = fetch('/words.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load word data');
            }
            return response.json();
        })
        .then(data => {
            wordData = data;
            wordDataLoading = false;
            console.log('[OK] Loaded ' + Object.keys(data).length + ' Hebrew words');
            return data;
        })
        .catch(error => {
            wordDataLoading = false;
            console.error('[FAIL] Error loading word data:', error);
            throw error;
        });

    return wordDataPromise;
}

/**
 * Show word evolution modal
 * @param {string} hebrew - The Hebrew word to display
 */
function showWordEvolution(hebrew) {
    const modal = document.getElementById('wordModal');
    if (!modal) {
        console.error('[FAIL] Modal element not found');
        return;
    }

    const body = modal.querySelector('.word-modal-body');

    // Show loading
    body.innerHTML = '<div class="word-modal-loading">Loading...</div>';
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';

    // Load data and display
    loadWordData()
        .then(data => {
            const word = data[hebrew];
            if (!word) {
                body.innerHTML = `
                    <div class="word-modal-loading">
                        Word not found: ${hebrew}<br>
                        <small>This word may not be in our database yet.</small>
                    </div>
                `;
                return;
            }

            body.innerHTML = buildWordHTML(word);
        })
        .catch(error => {
            body.innerHTML = `
                <div class="word-modal-loading">
                    Error loading word data.<br>
                    <small>${error.message}</small>
                </div>
            `;
        });
}

/**
 * Build HTML for word evolution display
 * @param {object} word - Word data object
 * @returns {string} HTML string
 */
function buildWordHTML(word) {
    // Build letter table rows
    let letterRows = '';
    if (word.letters && word.letters.length > 0) {
        for (const letter of word.letters) {
            letterRows += `
                <tr>
                    <td style="font-size:1.5rem">${letter.char}</td>
                    <td>${letter.name}</td>
                    <td>${letter.value}</td>
                    <td>${letter.pictograph}</td>
                    <td>${letter.concrete}</td>
                    <td>${letter.abstract}</td>
                </tr>
            `;
        }
    }

    // Build timeline
    const timeline = word.timeline || {};

    return `
        <div class="word-hebrew-large">${word.hebrew}</div>

        <div class="word-stats-row">
            <div class="word-stat-box">
                <div class="word-stat-value">${word.strongs || 'N/A'}</div>
                <div class="word-stat-label">Strong's #</div>
            </div>
            <div class="word-stat-box">
                <div class="word-stat-value">${word.gematria}</div>
                <div class="word-stat-label">Gematria</div>
            </div>
            <div class="word-stat-box">
                <div class="word-stat-value">${word.digital_root}</div>
                <div class="word-stat-label">Digital Root</div>
            </div>
            <div class="word-stat-box">
                <div class="word-stat-value">${word.frequency}</div>
                <div class="word-stat-label">Occurrences</div>
            </div>
        </div>

        <h3 class="word-section-header">Pictographic Meaning</h3>
        <div class="word-pictographic">${word.pictographic}</div>

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

        <p><strong>First Occurrence:</strong> ${word.first_occurrence}</p>

        <h3 class="word-section-header">6-Stage Corruption Timeline</h3>
        <div class="word-timeline">
            <div class="word-timeline-stage">
                <div class="word-timeline-num">1</div>
                <div class="word-timeline-content">
                    <strong>Hebrew Original</strong>
                    <span class="word-timeline-period">(Ancient)</span><br>
                    <span class="word-timeline-hebrew">${word.hebrew}</span><br>
                    ${timeline.hebrew || word.pictographic}
                </div>
            </div>
            <div class="word-timeline-stage">
                <div class="word-timeline-num">2</div>
                <div class="word-timeline-content">
                    <strong>Septuagint (LXX)</strong>
                    <span class="word-timeline-period">(280 BCE)</span><br>
                    <em>${timeline.septuagint || '(Research in progress)'}</em>
                </div>
            </div>
            <div class="word-timeline-stage">
                <div class="word-timeline-num">3</div>
                <div class="word-timeline-content">
                    <strong>New Testament Greek</strong>
                    <span class="word-timeline-period">(100 CE)</span><br>
                    <em>${timeline.nt_greek || '(Research in progress)'}</em>
                </div>
            </div>
            <div class="word-timeline-stage">
                <div class="word-timeline-num">4</div>
                <div class="word-timeline-content">
                    <strong>Latin Vulgate</strong>
                    <span class="word-timeline-period">(400 CE)</span><br>
                    <em>${timeline.vulgate || '(Research in progress)'}</em>
                </div>
            </div>
            <div class="word-timeline-stage">
                <div class="word-timeline-num">5</div>
                <div class="word-timeline-content">
                    <strong>King James Version</strong>
                    <span class="word-timeline-period">(1611 CE)</span><br>
                    <em>${timeline.kjv || '(Research in progress)'}</em>
                </div>
            </div>
            <div class="word-timeline-stage">
                <div class="word-timeline-num">6</div>
                <div class="word-timeline-content">
                    <strong>Modern English</strong>
                    <span class="word-timeline-period">(Today)</span><br>
                    ${timeline.modern || 'See pictographic meaning'}
                </div>
            </div>
        </div>

        <div class="word-sources">
            <strong>Sources:</strong><br>
            - Strong's Concordance (${word.strongs || 'N/A'})<br>
            - Ancient Hebrew Lexicon of the Bible (AHLB, Jeff Benner)<br>
            - Proto-Sinaitic pictograph analysis<br>
            - Masoretic Text concordance
        </div>
    `;
}

/**
 * Close the word modal
 */
function closeWordModal() {
    const modal = document.getElementById('wordModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

/**
 * Initialize modal - call this on page load
 */
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

    // Preload word data in background
    setTimeout(() => {
        loadWordData().catch(() => {}); // Silent preload
    }, 1000);
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initWordModal);
} else {
    initWordModal();
}
