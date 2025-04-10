function closeMessage(element) {
    element.classList.add('fade-out');
    setTimeout(() => {
        element.remove();
        if (document.querySelectorAll('#messages-container .alert').length === 0) {
            const container = document.getElementById('messages-container');
            if (container) {
                container.remove();
            }
        }
    }, 300);
}

document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('#messages-container .alert');
    messages.forEach(message => {
        setTimeout(() => {
            if (message) {
                closeMessage(message);
            }
        }, 3000);
    });
});