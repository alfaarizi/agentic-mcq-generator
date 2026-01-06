// Shared modal functions for all templates

function showModal(title, message, onConfirm = null) {
    return new Promise((resolve) => {
        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modalTitle');
        const modalMessage = document.getElementById('modalMessage');
        const modalOk = document.getElementById('modalOk');
        const modalCancel = document.getElementById('modalCancel');

        modalTitle.textContent = title;
        modalMessage.textContent = message;

        // Set button text from translations if available (check both window.translations and global translations)
        const trans = typeof translations !== 'undefined' ? translations : (typeof window.translations !== 'undefined' ? window.translations : null);
        if (trans) {
            modalOk.textContent = trans.ok || 'OK';
            modalCancel.textContent = trans.cancel || 'Cancel';
        }

        // Show/hide cancel button based on whether this is a confirm dialog
        if (onConfirm) {
            modalCancel.classList.remove('hidden');

            const handleOk = () => {
                closeModal();
                resolve(true);
                if (onConfirm) onConfirm();
            };

            const handleCancel = () => {
                closeModal();
                resolve(false);
            };

            modalOk.onclick = handleOk;
            modalCancel.onclick = handleCancel;
        } else {
            modalCancel.classList.add('hidden');
            modalOk.onclick = () => {
                closeModal();
                resolve(true);
            };
        }

        modal.classList.replace('hidden', 'flex');
    });
}

function closeModal() {
    const modal = document.getElementById('modal');
    modal.classList.replace('flex', 'hidden');
}
