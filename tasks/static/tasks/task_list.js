const editDialog = document.querySelector('#task-edit-dialog');

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