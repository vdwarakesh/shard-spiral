// ========== Help & FAQ Modal Engine ========== //
const FAQ_ITEMS = [
    {
        id: 'dataStructures',
        category: 'Workspace & Panels',
        question: 'What is the Data Structures & Canvas panel?',
        title: 'Data Structures & Canvas',
        answer: 'The interactive visualization canvas is where data structures and algorithm steps are animated in real time. You can pan by dragging, zoom with the scroll wheel or pinch gesture, double-click to recenter, and right-click the canvas or header to modify elements or export PNG images.'
    },
    {
        id: 'codeAndNotes',
        category: 'Workspace & Panels',
        question: 'How do the Code, Notes, and Practice tabs work?',
        title: 'Code, Notes & Practice',
        answer: 'View the syntax-highlighted code implementation with real-time execution line highlights, switch to Notes to read detailed conceptual explanations and complexity breakdowns, or use Practice to write and trace your own custom Python visualization code.'
    },
    {
        id: 'stateAndExplanation',
        category: 'Workspace & Panels',
        question: 'What are State Variables and Explanation?',
        title: 'State Variables & Explanation',
        answer: 'Inspect live pointer values, local variables, console stdout, and interactive prompts at each step in the State Variables tab, or switch to the Explanation tab to view the full step-by-step execution trace all at once.'
    },
    {
        id: 'createMenu',
        category: 'Data Structures & Settings',
        question: 'How do I create a data structure or pick an algorithm?',
        title: 'Create & Settings',
        answer: 'Click the Create & Settings button in the top bar to open the Data Structures & Settings window, where you can create new data structure containers, browse algorithms, and configure input parameters.'
    },
    {
        id: 'algorithms',
        category: 'Data Structures & Settings',
        question: 'How do I browse and search data structures and algorithms?',
        title: 'Explorer & Search',
        answer: 'Browse data structures and algorithms like a file system using folder navigation and breadcrumbs, or use the search bar to find items by name, acronym, or tag across full paths.'
    },
    {
        id: 'favourites',
        category: 'Data Structures & Settings',
        question: 'How do I save and filter my Favourite items?',
        title: 'Favourites Filter',
        answer: 'Click the star icon next to any data structure or algorithm to favourite it, then toggle the Favourites filter button next to the search bar to show only your starred items.'
    },
    {
        id: 'syllabus',
        category: 'Data Structures & Settings',
        question: 'What does the Syllabus filter button do?',
        title: 'Syllabus Filter',
        answer: 'Filters the Explorer list to show only the data structures and algorithms included in your institution\'s curriculum syllabus.'
    },
    {
        id: 'filterByCompatible',
        category: 'Data Structures & Settings',
        question: 'How do I see only algorithms compatible with my active data structure?',
        title: 'Compatible Algorithms Filter',
        answer: 'Toggle the Compatible Algorithms filter button to show only the algorithms that can run on your currently active data structure container.'
    },
    {
        id: 'algorithmSettings',
        category: 'Data Structures & Settings',
        question: 'How do I configure parameters or randomize inputs?',
        title: 'Settings & Randomization',
        answer: 'When a data structure is selected, use the Settings pane to name your container, enter custom values, or generate randomized inputs. When an algorithm is selected, fill in the function signature parameters and click Run.'
    },
    {
        id: 'metadata',
        category: 'Metadata & History',
        question: 'Where can I view Metadata for my active data structure?',
        title: 'Metadata',
        answer: 'Displays key structural properties about the active data structure-such as length, whether elements are sorted or unique, and min/max values. On desktop, expand the left sidebar strip; on mobile, tap the History button in the top bar.'
    },
    {
        id: 'history',
        category: 'Metadata & History',
        question: 'How do I switch between previously created data structures?',
        title: 'Container History',
        answer: 'The History panel tracks all data structure containers created during your session so you can switch back and forth between them at any time without losing your work.'
    },
    {
        id: 'grid',
        category: 'Toolbar & Customization',
        question: 'How do I change or hide the canvas background grid?',
        title: 'Grid Varieties',
        answer: 'Use the Grid dropdown in the top bar to switch between Grid Dots, Grid Lines, Ruled Paper, Crosses, Isometric grid, or No Grid.'
    },
    {
        id: 'annotations',
        category: 'Toolbar & Customization',
        question: 'How do I draw annotations or use the laser pointer on screen?',
        title: 'Screen Annotations',
        answer: 'Click the Annotations button in the top bar to draw over the workspace. Use the dropdown arrow next to it to pick between the Laser Pointer, Pen, Rectangle, Circle, Text tool, Eraser, Select tool, or Clear Board.'
    },
    {
        id: 'toggleAnnotations',
        category: 'Toolbar & Customization',
        question: 'How can I temporarily hide or show my drawn annotations?',
        title: 'Toggle Annotations Visibility',
        answer: 'Click the Hide/Show Annotations button right next to the annotation tool menu to toggle the visibility of your drawings without erasing them.'
    },
    {
        id: 'zenMode',
        category: 'Toolbar & Customization',
        question: 'What is Zen Mode?',
        title: 'Zen Mode',
        answer: 'Automatically hides any collapsed panels and splitters so the remaining open panels expand to fill 100% of the workspace for a clean, distraction-free view.'
    },
    {
        id: 'resetLayout',
        category: 'Toolbar & Customization',
        question: 'How do I restore the panels to their default layout?',
        title: 'Reset Layout',
        answer: 'Click the Reset Layout button in the top-right bar to restore all resized or collapsed panels back to their default proportions with a single click.'
    },
    {
        id: 'fullscreen',
        category: 'Toolbar & Customization',
        question: 'How do I toggle Fullscreen mode?',
        title: 'Fullscreen Mode',
        answer: 'Click the Fullscreen button in the top-left bar (or press F11) to maximize your workspace while visualizing complex structures.'
    }
];

(function initHelpFaqModal() {
    const btnHelp = document.getElementById('btnHelp');
    const helpBackdrop = document.getElementById('help-modal-backdrop');
    const closeHelpBtn = document.getElementById('close-help-modal');
    const searchInput = document.getElementById('faq-search-input');
    const searchClearBtn = document.getElementById('faq-search-clear-btn');
    const listContainer = document.getElementById('faq-list-container');
    const answerContent = document.getElementById('faq-answer-content');

    let selectedFaqId = FAQ_ITEMS[0]?.id || null;

    function setHelpModalOpen(open) {
        if (!helpBackdrop) return;
        helpBackdrop.classList.toggle('open', Boolean(open));
        if (open) {
            renderFaqList();
            renderFaqAnswer();
        }
    }

    function renderFaqAnswer() {
        if (!answerContent) return;
        const item = FAQ_ITEMS.find(q => q.id === selectedFaqId);
        if (!item) {
            answerContent.innerHTML = `
            <span class="card-body-text" style="color: var(--text-muted);">
              Select a question on the left to view its answer.
            </span>
          `;
            return;
        }

        answerContent.innerHTML = `
          <div class="faq-answer-badge">${item.category}</div>
          <h3 class="faq-answer-heading">${item.question}</h3>
          <p class="faq-answer-text">${item.answer}</p>
        `;
    }

    function renderFaqList() {
        if (!listContainer) return;
        const query = (searchInput ? searchInput.value : '').trim().toLowerCase();
        listContainer.innerHTML = '';

        const filtered = FAQ_ITEMS.filter(item => {
            if (!query) return true;
            return (
                item.question.toLowerCase().includes(query) ||
                item.title.toLowerCase().includes(query) ||
                item.answer.toLowerCase().includes(query) ||
                item.category.toLowerCase().includes(query)
            );
        });

        if (filtered.length === 0) {
            const emptyEl = document.createElement('div');
            emptyEl.className = 'algo-empty-msg';
            emptyEl.textContent = 'No matching questions found.';
            listContainer.appendChild(emptyEl);
            return;
        }

        const grouped = {};
        filtered.forEach(item => {
            if (!grouped[item.category]) grouped[item.category] = [];
            grouped[item.category].push(item);
        });

        for (const [category, items] of Object.entries(grouped)) {
            const catHeader = document.createElement('div');
            catHeader.className = 'faq-category-header';
            catHeader.textContent = category;
            listContainer.appendChild(catHeader);

            items.forEach(item => {
                const row = document.createElement('div');
                row.className = `tree-row faq-question-row${item.id === selectedFaqId ? ' selected' : ''}`;

                const dot = document.createElement('span');
                dot.className = 'algo-dot';
                row.appendChild(dot);

                const label = document.createElement('span');
                label.className = 'tree-label faq-question-label';
                label.textContent = item.question;
                row.appendChild(label);

                row.addEventListener('click', () => {
                    selectedFaqId = item.id;
                    renderFaqList();
                    renderFaqAnswer();
                });

                listContainer.appendChild(row);
            });
        }
    }

    if (btnHelp) {
        btnHelp.addEventListener('click', () => {
            setHelpModalOpen(!helpBackdrop.classList.contains('open'));
        });
    }

    if (closeHelpBtn) {
        closeHelpBtn.addEventListener('click', () => setHelpModalOpen(false));
    }

    if (helpBackdrop) {
        helpBackdrop.addEventListener('mousedown', (e) => {
            if (e.target === helpBackdrop) setHelpModalOpen(false);
        });
    }

    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && helpBackdrop?.classList.contains('open')) {
            setHelpModalOpen(false);
        }
    });

    if (searchInput) {
        searchInput.addEventListener('input', () => {
            if (searchClearBtn) {
                searchClearBtn.style.display = searchInput.value.length > 0 ? 'flex' : 'none';
            }
            renderFaqList();
        });
    }

    if (searchClearBtn) {
        searchClearBtn.addEventListener('click', () => {
            searchInput.value = '';
            searchClearBtn.style.display = 'none';
            searchInput.focus();
            renderFaqList();
        });
    }

    renderFaqList();
    renderFaqAnswer();
})();