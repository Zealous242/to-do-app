const editDialog = document.querySelector('#task-edit-dialog');
const mobileNavToggle = document.querySelector('.mobile-nav-toggle');
const taskFilterForm = document.querySelector('.task-filter-form');
const scrollKeyForPath = (path) => `task-list-scroll:${path}`;
const savedScroll = sessionStorage.getItem(scrollKeyForPath(window.location.pathname));

if (savedScroll !== null) {
    const restoreScroll = () => window.setTimeout(() => {
        window.scrollTo(0, Number(savedScroll));
        sessionStorage.removeItem(scrollKeyForPath(window.location.pathname));
    }, 0);
    if (document.readyState === 'complete') {
        restoreScroll();
    } else {
        window.addEventListener('load', restoreScroll, {
            once: true
        });
    }
}

const rememberScroll = (element) => {
    const returnPath = element.dataset.scrollReturnPath || window.location.pathname;
    sessionStorage.setItem(scrollKeyForPath(returnPath), String(window.scrollY));
};

document.querySelectorAll('[data-toggle-password]').forEach((button) => {
    const passwordInput = button.closest('.password-input-wrap').querySelector('input');
    const eyeIcon = button.querySelector('i');

    button.addEventListener('click', () => {
        const showPassword = passwordInput.type === 'password';
        passwordInput.type = showPassword ? 'text' : 'password';
        button.setAttribute('aria-label', showPassword ? 'Hide password' : 'Show password');
        button.setAttribute('aria-pressed', String(showPassword));
        eyeIcon.classList.toggle('fa-eye', !showPassword);
        eyeIcon.classList.toggle('fa-eye-slash', showPassword);
        passwordInput.focus({
            preventScroll: true
        });
    });
});

if (taskFilterForm) {
    taskFilterForm.addEventListener('submit', () => rememberScroll(taskFilterForm));
    document.querySelectorAll('.filter-chip-remove, .filter-reset').forEach((link) => {
        link.addEventListener('click', () => rememberScroll(link));
    });
}

document.querySelectorAll('[data-preserve-scroll]').forEach((form) => {
    form.addEventListener('submit', () => rememberScroll(form));
});

document.querySelectorAll('[data-confirm-delete]').forEach((form) => {
    form.addEventListener('submit', (event) => {
        if (!window.confirm(form.dataset.confirmDelete)) {
            event.preventDefault();
        }
    });
});

if (mobileNavToggle) {
    const header = mobileNavToggle.closest('.topbar');
    const headerMenu = document.getElementById(mobileNavToggle.getAttribute('aria-controls'));

    const closeMobileMenu = () => {
        header.classList.remove('menu-open');
        mobileNavToggle.setAttribute('aria-expanded', 'false');
    };

    mobileNavToggle.addEventListener('click', () => {
        const isOpen = mobileNavToggle.getAttribute('aria-expanded') === 'true';
        header.classList.toggle('menu-open', !isOpen);
        mobileNavToggle.setAttribute('aria-expanded', String(!isOpen));
    });

    headerMenu.querySelectorAll('a, [data-open-dialog]').forEach((control) => {
        control.addEventListener('click', closeMobileMenu);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && mobileNavToggle.getAttribute('aria-expanded') === 'true') {
            closeMobileMenu();
            mobileNavToggle.focus();
        }
    });
}

document.querySelectorAll('[data-open-dialog]').forEach((button) => {
    const dialog = document.getElementById(button.dataset.openDialog);

    if (dialog) {
        button.addEventListener('click', () => {
            dialog.showModal();
            const input = dialog.querySelector('input:not([type="hidden"])');
            if (input) {
                input.focus();
            }
        });
    }
});

document.querySelectorAll('dialog').forEach((dialog) => {
    dialog.querySelectorAll('[data-close-dialog]').forEach((button) => {
        button.addEventListener('click', () => dialog.close());
    });

    dialog.addEventListener('click', (event) => {
        if (event.target === dialog) {
            dialog.close();
        }
    });
});

if (editDialog) {
    const editForm = editDialog.querySelector('#task-edit-form');

    document.querySelectorAll('[data-edit-task]').forEach((button) => {
        button.addEventListener('click', () => {
            editForm.action = button.dataset.editUrl;
            editForm.elements.title.value = button.dataset.title;
            editForm.elements.description.value = button.dataset.description;
            editForm.elements.category.value = button.dataset.category;
            editForm.elements.priority.value = button.dataset.priority;
            editDialog.showModal();
            editForm.elements.title.focus();
        });
    });

}