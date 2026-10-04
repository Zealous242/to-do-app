// Set data-bs-theme to ensure Bootstrap uses correct colour-mode
const root = document.documentElement;
const mq = matchMedia('(prefers-color-scheme: dark)');

const sync = () => {
    root.setAttribute(
        'data-bs-theme',
        root.dataset.theme || (mq.matches ? 'dark' : 'light'),
    );
};

sync();
mq.addEventListener('change', sync);

new MutationObserver(sync).observe(root, {
    attributes: true,
    attributeFilter: ['data-theme'],
});


// Plant graphic
function initPlantGraphics() {
    const template = document.getElementById('tend-plant');
    if (!template) return;

    const sourceSvg = template.content.firstElementChild;
    if (!sourceSvg) return;

    document.querySelectorAll('.tend-sprig').forEach(el => {
        // Fill empty containers
        if (el.children.length === 0) {
            el.append(...sourceSvg.cloneNode(true).childNodes);
        }
    });
}


// Task list
function stageFor(done, total) {
    if (!total || !done) return 0;

    const pct = done / total * 100;
    return pct <= 25 ? 1 : pct <= 50 ? 2 : pct <= 75 ? 3 : pct < 100 ? 4 : 5;
}

function refreshTaskList(taskList) {
    const boxes = [...taskList.querySelectorAll('.tend-check')];
    const done = boxes.filter(b => b.checked).length;

    taskList
        .querySelector('[data-plant]')
        ?.style.setProperty('--stage', stageFor(done, boxes.length));

    const count = taskList.querySelector('[data-tend-count]');
    if (count) count.textContent = `${done} of ${boxes.length} done`;
}

function initTaskLists() {
    document.querySelectorAll('[data-tend-tasks]').forEach(taskList => {
        // Already wired: a swap changed something inside it, so just resync
        if (taskList.dataset.tendReady) return refreshTaskList(taskList);

        taskList.dataset.tendReady = 'true';

        // Delegated, so tasks added to the list later are covered without re-binding
        taskList.addEventListener('change', e => {
            if (e.target.matches('.tend-check')) {
                refreshTaskList(taskList);
            }
        });

        // Start bare, then grow into the initial state once on load
        taskList.querySelector('[data-plant]')?.style.setProperty('--stage', 0);

        requestAnimationFrame(() =>
            requestAnimationFrame(() => refreshTaskList(taskList))
        );
    });
}


// Initialise Tend
function initTend() {
    initPlantGraphics();
    initTaskLists();
}

initTend();

document.addEventListener('htmx:afterSwap', initTend);
document.addEventListener('htmx:oobAfterSwap', initTend);

// Keep scroll position across delete / toggle round-trips
const SCROLL_KEY = 'tend-restore-scroll';

function nextTarget(urlString, form) {
    const url = new URL(urlString, location.origin);
    const fromForm = form?.querySelector('input[name="next"]')?.value;
    return fromForm || url.searchParams.get('next') || location.pathname + location.search;
}

function rememberScroll(urlString, form) {
    sessionStorage.setItem(SCROLL_KEY, JSON.stringify({
        y: window.scrollY,
        target: nextTarget(urlString, form),
        at: Date.now(),
    }));
}

function restoreScroll() {
    const raw = sessionStorage.getItem(SCROLL_KEY);
    if (!raw) return;

    const saved = JSON.parse(raw);
    if (Date.now() - saved.at > 30000) return sessionStorage.removeItem(SCROLL_KEY);
    if (saved.target !== location.pathname + location.search) return;

    sessionStorage.removeItem(SCROLL_KEY);
    history.scrollRestoration = 'manual';
    window.scrollTo(0, saved.y);
}

const ACTION_PATH = /\/task\/\d+\/(delete|toggle)\//;

document.addEventListener('click', e => {
    const link = e.target.closest('a[href]');
    if (link && ACTION_PATH.test(link.getAttribute('href'))) {
        rememberScroll(link.href);
    }
});

document.addEventListener('submit', e => {
    const form = e.target;
    if (form.method === 'post' && ACTION_PATH.test(form.getAttribute('action') || '')) {
        // Only remember when leaving a list page, not from the confirm page itself
        if (!form.closest('[aria-labelledby="delete-task-heading"]')) {
            rememberScroll(form.action, form);
        }
    }
});

restoreScroll();
