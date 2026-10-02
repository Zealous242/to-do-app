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