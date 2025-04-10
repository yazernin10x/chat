function openModal(id, type = 'room', action = 'create') {
    event.preventDefault();
    event.stopPropagation();
    const modal = document.getElementById(`${action}-${type}-modal-${id}`);
    if (modal) {
        modal.showModal();
    } else {
        console.error(`Modal not found for ${type} ${id}`);
    }
}

function closeModal(id, type = 'room', action = 'create') {
    const modal = document.getElementById(`${action}-${type}-modal-${id}`);
    if (modal) {
        modal.close();
    } else {
        console.error(`Modal not found for ${type} ${id}`);
    }
}

document.addEventListener('htmx:afterSwap', function(event) {
    id_splited = event.target.id.split('-');
    modalId = `${id_splited[0]}-${id_splited[1]}-modal-${id_splited.pop()}`
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.showModal();
    }
});