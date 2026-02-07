/**
 * Oracle Bible Helper
 * Floating Oracle button + context-aware Bible study assistant
 * Integrates all 16 Mathematical Bible study tools
 */

(function() {
    'use strict';

    // Inject floating button CSS
    const style = document.createElement('style');
    style.textContent = `
        /* GLOWING PINKISH-PURPLE ORACLE BALL */
        #oracle-float-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%,
                #ff6ec7 0%,
                #d946ef 20%,
                #a855f7 40%,
                #7c3aed 60%,
                #6366f1 80%,
                #4f46e5 100%);
            border: 2px solid rgba(255, 255, 255, 0.3);
            cursor: pointer;
            box-shadow:
                0 0 20px rgba(217, 70, 239, 0.6),
                0 0 40px rgba(168, 85, 247, 0.4),
                0 0 60px rgba(124, 58, 237, 0.3),
                inset 0 0 20px rgba(255, 255, 255, 0.2);
            z-index: 9999;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: float 3s ease-in-out infinite, glow 2s ease-in-out infinite alternate;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        @keyframes glow {
            0% {
                box-shadow:
                    0 0 20px rgba(217, 70, 239, 0.6),
                    0 0 40px rgba(168, 85, 247, 0.4),
                    0 0 60px rgba(124, 58, 237, 0.3),
                    inset 0 0 20px rgba(255, 255, 255, 0.2);
            }
            100% {
                box-shadow:
                    0 0 30px rgba(255, 110, 199, 0.8),
                    0 0 60px rgba(217, 70, 239, 0.6),
                    0 0 90px rgba(168, 85, 247, 0.4),
                    inset 0 0 30px rgba(255, 255, 255, 0.3);
            }
        }
        #oracle-float-btn:hover {
            transform: scale(1.15) translateY(-5px);
            box-shadow:
                0 0 40px rgba(255, 110, 199, 1),
                0 0 80px rgba(217, 70, 239, 0.8),
                0 0 120px rgba(168, 85, 247, 0.6),
                inset 0 0 40px rgba(255, 255, 255, 0.4);
            animation: none;
        }
        #oracle-float-btn svg {
            width: 32px;
            height: 32px;
            fill: white;
            filter: drop-shadow(0 0 5px rgba(255,255,255,0.8));
        }
        #oracle-float-btn .pulse {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,110,199,0.4) 0%, transparent 70%);
            animation: pulse 2s infinite;
        }
        #oracle-float-btn .pulse2 {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(168,85,247,0.3) 0%, transparent 70%);
            animation: pulse 2s infinite 0.5s;
        }
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            100% { transform: scale(2); opacity: 0; }
        }
        /* Inner sparkle effect */
        #oracle-float-btn::before {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            background: radial-gradient(circle, rgba(255,255,255,0.9) 0%, transparent 70%);
            border-radius: 50%;
            top: 15%;
            left: 20%;
            animation: sparkle 3s ease-in-out infinite;
        }
        @keyframes sparkle {
            0%, 100% { opacity: 0.6; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
        }

        /* Oracle Modal */
        #oracle-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10000;
            align-items: center;
            justify-content: center;
        }
        #oracle-modal.show {
            display: flex;
        }
        #oracle-modal-content {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 20px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        #oracle-modal-header {
            background: rgba(255, 215, 0, 0.1);
            padding: 20px;
            border-bottom: 1px solid rgba(255, 215, 0, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        #oracle-modal-header h3 {
            color: #ffd700;
            margin: 0;
            font-size: 1.3rem;
        }
        #oracle-modal-close {
            background: none;
            border: none;
            color: #888;
            font-size: 24px;
            cursor: pointer;
            padding: 0;
            line-height: 1;
        }
        #oracle-modal-close:hover {
            color: #fff;
        }
        #oracle-modal-body {
            padding: 20px;
        }
        #oracle-context {
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: #aaa;
        }
        #oracle-context strong {
            color: #ffd700;
        }
        #oracle-quick-questions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        .oracle-quick-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #e8e8e8;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.3s;
        }
        .oracle-quick-btn:hover {
            background: rgba(255, 215, 0, 0.2);
            border-color: #ffd700;
            color: #ffd700;
        }
        #oracle-input-group {
            display: flex;
            gap: 10px;
        }
        #oracle-question-input {
            flex: 1;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            padding: 12px 20px;
            color: #fff;
            font-size: 1rem;
        }
        #oracle-question-input:focus {
            outline: none;
            border-color: #ffd700;
        }
        #oracle-question-input::placeholder {
            color: #666;
        }
        #oracle-ask-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 25px;
            padding: 12px 25px;
            color: white;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            transition: all 0.3s;
        }
        #oracle-ask-btn:hover {
            transform: scale(1.05);
        }

        /* Mobile responsive */
        @media (max-width: 600px) {
            #oracle-float-btn {
                bottom: 20px;
                right: 20px;
                width: 50px;
                height: 50px;
            }
            #oracle-modal-content {
                width: 95%;
                margin: 10px;
            }
            #oracle-input-group {
                flex-direction: column;
            }
        }
    `;
    document.head.appendChild(style);

    // Create floating button
    const floatBtn = document.createElement('button');
    floatBtn.id = 'oracle-float-btn';
    floatBtn.setAttribute('aria-label', 'Ask the Oracle');
    floatBtn.innerHTML = `
        <div class="pulse"></div>
        <div class="pulse2"></div>
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" fill="none" stroke="white" stroke-width="1.5" opacity="0.6"/>
            <circle cx="12" cy="12" r="6" fill="none" stroke="white" stroke-width="1" opacity="0.8"/>
            <circle cx="12" cy="12" r="3" fill="white" opacity="0.9"/>
        </svg>
    `;
    document.body.appendChild(floatBtn);

    // Create modal
    const modal = document.createElement('div');
    modal.id = 'oracle-modal';
    modal.innerHTML = `
        <div id="oracle-modal-content">
            <div id="oracle-modal-header">
                <h3>Ask the Oracle</h3>
                <button id="oracle-modal-close">&times;</button>
            </div>
            <div id="oracle-modal-body">
                <div id="oracle-context">
                    <strong>Current Context:</strong> <span id="oracle-context-text">Mathematical Bible Study</span>
                </div>
                <div id="oracle-quick-questions"></div>
                <div id="oracle-input-group">
                    <input type="text" id="oracle-question-input" placeholder="Ask about this passage, gematria, prophecy...">
                    <button id="oracle-ask-btn">Ask</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    // Detect page context
    function getPageContext() {
        const path = window.location.pathname;
        const page = path.split('/').pop().replace('.html', '');

        const contexts = {
            'index': { name: 'Mathematical Bible Home', type: 'home' },
            'search': { name: 'Gematria Search', type: 'gematria' },
            'red-letter': { name: 'Red Letter Bible', type: 'red-letter' },
            'prophecy': { name: 'Prophecy Tracker', type: 'prophecy' },
            'parallels': { name: 'Synoptic Parallels', type: 'parallels' },
            'tsk': { name: 'Cross-References (TSK)', type: 'cross-refs' },
            'naves': { name: "Nave's Topical Index", type: 'topical' },
            'fathers': { name: 'Church Fathers Commentary', type: 'fathers' },
            'cantillation': { name: 'Hebrew Cantillation', type: 'cantillation' },
            'frequency': { name: 'Word Frequency Statistics', type: 'frequency' },
            'variants': { name: 'Manuscript Variants', type: 'manuscripts' },
            'controversies': { name: 'Biblical Controversies', type: 'controversies' },
            'reading-plans': { name: 'Reading Plans', type: 'plans' }
        };

        return contexts[page] || { name: 'Mathematical Bible', type: 'general' };
    }

    // Generate quick questions based on context
    function getQuickQuestions(context) {
        const questions = {
            'home': [
                'What book should I start with?',
                'Explain gematria to me',
                'What are the red letter verses?'
            ],
            'gematria': [
                'What does 666 mean?',
                'Why is 888 significant?',
                'Find verses with value 777'
            ],
            'red-letter': [
                'What did Jesus say about love?',
                'Summarize the Sermon on the Mount',
                'What are Jesus\' I AM statements?'
            ],
            'prophecy': [
                'Which prophecies are most significant?',
                'Explain Isaiah 53 fulfillment',
                'What about unfulfilled prophecies?'
            ],
            'parallels': [
                'Why do Gospels differ?',
                'Compare the resurrection accounts',
                'What is the Synoptic Problem?'
            ],
            'cross-refs': [
                'How do cross-references work?',
                'Find references to Psalm 23',
                'What connects OT and NT?'
            ],
            'topical': [
                'What does the Bible say about faith?',
                'Find verses about wisdom',
                'Topics on prayer'
            ],
            'fathers': [
                'Who was Augustine?',
                'What did Chrysostom teach?',
                'Early church on baptism'
            ],
            'cantillation': [
                'How was Scripture sung?',
                'What is an Atnach?',
                'Explain the music of Torah'
            ],
            'frequency': [
                'Most common word in Bible?',
                'How often is love mentioned?',
                'Count of God vs LORD'
            ],
            'manuscripts': [
                'What is the Comma Johanneum?',
                'Are there missing verses?',
                'Which manuscripts are oldest?'
            ],
            'controversies': [
                'Mark 16:9-20 authentic?',
                'Woman caught in adultery?',
                'Trinity in 1 John 5:7?'
            ],
            'plans': [
                'Which plan for beginners?',
                'How to read Bible in a year?',
                'Best Lent reading plan'
            ],
            'general': [
                'How do I use this Bible?',
                'Explain the study tools',
                'Where should I start?'
            ]
        };

        return questions[context.type] || questions['general'];
    }

    // Update modal with context
    function updateModalContext() {
        const context = getPageContext();
        document.getElementById('oracle-context-text').textContent = context.name;

        const quickQuestionsDiv = document.getElementById('oracle-quick-questions');
        quickQuestionsDiv.innerHTML = '';

        const questions = getQuickQuestions(context);
        questions.forEach(q => {
            const btn = document.createElement('button');
            btn.className = 'oracle-quick-btn';
            btn.textContent = q;
            btn.onclick = () => askOracle(q);
            quickQuestionsDiv.appendChild(btn);
        });
    }

    // Ask Oracle
    function askOracle(question) {
        const context = getPageContext();
        const fullQuestion = `[Bible Study Context: ${context.name}] ${question}`;
        const encodedQ = encodeURIComponent(fullQuestion);
        window.location.href = `/oracle?q=${encodedQ}`;
    }

    // Event listeners
    floatBtn.onclick = () => {
        updateModalContext();
        modal.classList.add('show');
        document.getElementById('oracle-question-input').focus();
    };

    document.getElementById('oracle-modal-close').onclick = () => {
        modal.classList.remove('show');
    };

    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    };

    document.getElementById('oracle-ask-btn').onclick = () => {
        const input = document.getElementById('oracle-question-input');
        if (input.value.trim()) {
            askOracle(input.value.trim());
        }
    };

    document.getElementById('oracle-question-input').onkeypress = (e) => {
        if (e.key === 'Enter') {
            const input = document.getElementById('oracle-question-input');
            if (input.value.trim()) {
                askOracle(input.value.trim());
            }
        }
    };

    // Keyboard shortcut: Press 'O' to open Oracle
    document.addEventListener('keydown', (e) => {
        if (e.key === 'o' && !e.ctrlKey && !e.metaKey &&
            document.activeElement.tagName !== 'INPUT' &&
            document.activeElement.tagName !== 'TEXTAREA') {
            updateModalContext();
            modal.classList.add('show');
            document.getElementById('oracle-question-input').focus();
        }
        if (e.key === 'Escape') {
            modal.classList.remove('show');
        }
    });

    console.log('[OK] Oracle Helper loaded - Press O or click floating button to ask the Oracle');
})();
