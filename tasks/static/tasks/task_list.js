const editDialog = document.querySelector('#task-edit-dialog');
const mobileNavToggle = document.querySelector('.mobile-nav-toggle');

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