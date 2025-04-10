const messageHandlers = {
    // ... handlers existants ...

    clear_chat: (data) => {
        if (data.username === document.querySelector(DOM_SELECTORS.username).value) {
            document.querySelector(DOM_SELECTORS.messageContainer).innerHTML = '';
        }
    },

    system_message: (data) => {
        const messageContainer = document.querySelector(DOM_SELECTORS.messageContainer);
        messageContainer.insertAdjacentHTML('beforeend', `
            <div class="text-center text-sm text-base-content/70 my-2 whitespace-pre-line">
                ${data.message}
            </div>
        `);
        scrollToBottom();
    },

    action_message: (data) => {
        const messageContainer = document.querySelector(DOM_SELECTORS.messageContainer);
        messageContainer.insertAdjacentHTML('beforeend', `
            <div class="text-center text-sm italic text-primary my-2">
                * ${data.username} ${data.action}
            </div>
        `);
        scrollToBottom();
    },

    dice_roll: (data) => {
        const messageContainer = document.querySelector(DOM_SELECTORS.messageContainer);
        messageContainer.insertAdjacentHTML('beforeend', `
            <div class="text-center text-sm my-2">
                🎲 ${data.username} lance un dé ${data.max} et obtient: ${data.result}
            </div>
        `);
        scrollToBottom();
    },

    error_message: (data) => {
        const messageContainer = document.querySelector(DOM_SELECTORS.messageContainer);
        messageContainer.insertAdjacentHTML('beforeend', `
            <div class="text-center text-sm text-error my-2">
                ⚠️ ${data.message}
            </div>
        `);
        scrollToBottom();
    }
};