document.addEventListener("DOMContentLoaded", function () {
    
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = {
        hour: '2-digit',
        minute: '2-digit',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        timeZone: 'Europe/Paris'
    };
    return new Intl.DateTimeFormat('fr-FR', options).format(date);
}

// Fonction pour effacer le message "Aucun message"
function removeEmptyMessage() {
    const messagesContainer = document.getElementById('chat-messages-container');
    const emptyMessage = document.getElementById('emptyMessageContainer');

    // On vérifie si le conteneur existe et contient UNIQUEMENT le message "empty"
    if (messagesContainer && messagesContainer.children.length !== 1 && emptyMessage) {
        emptyMessage.remove();
    }
}


function scrollToBottom() {
    const messageContainer = document.querySelector("#chat-messages-container");
    messageContainer.parentElement.scrollTop = messageContainer.parentElement.scrollHeight;
}

// Appeler scrollToBottom au chargement de la page
scrollToBottom();

let chatSocket = null;

// Constantes réutilisables
const DOM_SELECTORS = {
    messageContainer: "#chat-messages-container",
    onlineUsers: "#onlineUsers",
    offlineUsers: "#offlineUsers",
    username: "#username",
    roomPk: "#room-pk",
    roomName: "#room-name"
};

// Fonction utilitaire pour créer un élément utilisateur
function createUserElement(username, isOnline) {
    return `
        <div class="flex items-center gap-2 p-2 bg-base-200 rounded-lg">
            <i class="fas fa-circle text-${isOnline ? 'success' : 'error'} text-xs"></i>
            <span>${username}</span>
        </div>
    `;
}

// Fonction utilitaire pour créer un message système
function createSystemMessage(username, action, timestamp, roomName) {
    return `
        <div class="text-center text-sm opacity-50 my-2">
            ${username} a ${action} la salle ${roomName} à ${formatDate(timestamp)}
        </div>
    `;
}

// Fonction pour créer le message empty avec un ID
function createEmptyUserMessage(type) {
    const isOnline = type === 'online';
    return `
        <div id="empty-${type}-message" class="flex items-center justify-center p-3 bg-base-200/50 rounded-lg">
            <div class="flex items-center gap-2">
                <i class="fas fa-circle text-${isOnline ? 'success' : 'error'}/30 text-sm"></i>
                <p class="text-sm text-base-content/50">Aucun utilisateur ${isOnline ? 'en ligne' : 'hors ligne'}</p>
            </div>
        </div>
    `;
}

// Fonction pour vérifier et mettre à jour les messages empty
function updateEmptyMessages(container, type) {
    const userElements = container.querySelectorAll('.flex.items-center.gap-2.p-2');
    const emptyMessage = document.getElementById(`empty-${type}-message`);

    if (userElements.length === 0 && !emptyMessage) {
        container.innerHTML = createEmptyUserMessage(type);
    } else if (userElements.length > 0 && emptyMessage) {
        emptyMessage.remove();
    }
}

// Gestionnaire de messages
const messageHandlers = {
    room_message: (data) => {
        const messageContainer = document.querySelector(DOM_SELECTORS.messageContainer);
        const currentUser = document.querySelector(DOM_SELECTORS.username)?.value;
        const isCurrentUser = data.sender === currentUser;
        
        const messageHTML = `
            <div class="chat ${isCurrentUser ? 'chat-end' : 'chat-start'}">
                <div class="chat-header">
                    ${data.sender}
                    <time class="text-xs opacity-50 ml-1">${formatDate(data.timestamp)}</time>
                </div>
                <div class="chat-bubble ${isCurrentUser ? 'chat-bubble-primary' : ''}">
                    ${data.content}
                </div>
            </div>
        `;
        messageContainer.insertAdjacentHTML('beforeend', messageHTML);
        scrollToBottom();
    },

    room_join: (data) => {
        const onlineUsers = document.querySelector(DOM_SELECTORS.onlineUsers);
        const offlineUsers = document.querySelector(DOM_SELECTORS.offlineUsers);
        const roomName = document.querySelector(DOM_SELECTORS.roomName).value;
        
        const existingOnlineUser = Array.from(onlineUsers.children)
            .some(div => div.textContent.includes(data.sender));
        
        if (!existingOnlineUser) {
            const emptyOnlineMessage = document.getElementById('empty-online-message');
            if (emptyOnlineMessage) {
                emptyOnlineMessage.remove();
            }
            
            onlineUsers.insertAdjacentHTML('beforeend', createUserElement(data.sender, true));
            
            Array.from(offlineUsers.children)
                .filter(div => div.textContent.includes(data.sender))
                .forEach(div => div.remove());

            if (data.action === "join") {
                document.querySelector(DOM_SELECTORS.messageContainer)
                    .insertAdjacentHTML('beforeend', 
                        createSystemMessage(data.sender, 'rejoint', data.timestamp, roomName));
            }
            
            updateEmptyMessages(offlineUsers, 'offline');
            scrollToBottom();
        }
    },

    room_leave: (data) => {
        const onlineUsers = document.querySelector(DOM_SELECTORS.onlineUsers);
        const offlineUsers = document.querySelector(DOM_SELECTORS.offlineUsers);
        const roomName = document.querySelector(DOM_SELECTORS.roomName).value;
        
        const emptyOfflineMessage = document.getElementById('empty-offline-message');
        if (emptyOfflineMessage) {
            emptyOfflineMessage.remove();
        }
        
        Array.from(onlineUsers.children)
            .filter(div => div.textContent.includes(data.sender))
            .forEach(div => div.remove());

        offlineUsers.insertAdjacentHTML('beforeend', createUserElement(data.sender, false));
        
        if (data.action === "leave") {
            document.querySelector(DOM_SELECTORS.messageContainer)
                .insertAdjacentHTML('beforeend', 
                    createSystemMessage(data.sender, 'quitté', data.timestamp, roomName));
        }

        updateEmptyMessages(onlineUsers, 'online');
        scrollToBottom();
    },

    private_message: (data) => {
        const messageContainer = document.querySelector(DOM_SELECTORS.messageContainer);
        const currentUser = document.querySelector(DOM_SELECTORS.username)?.value;
        const isCurrentUser = data.sender === currentUser;
        
        const messageHTML = ` 
            <div class="chat ${isCurrentUser ? 'chat-end' : 'chat-start'}">
                <div class="chat-header">
                    ${data.sender}
                    <time class="text-xs opacity-50 ml-1">${formatDate(data.timestamp)}</time>
                </div>
                <div class="chat-bubble ${isCurrentUser ? 'chat-bubble-primary' : ''}">
                    ${data.content}
                </div>
            </div>
        `;
        messageContainer.insertAdjacentHTML('beforeend', messageHTML);
        scrollToBottom();       
    },

    private_message_sent: (data) => {        
        const messageConfirmation =  `
                <div class="text-center text-sm opacity-50 my-2">
                    Message privé envoyé à ${data.recipient}
                </div>
            `
        document.querySelector(DOM_SELECTORS.messageContainer)
                .insertAdjacentHTML('beforeend', 
                    messageConfirmation);
                    
        scrollToBottom();
    }
};

function updateConnectionStatus(status, message) {
    const statusElement = document.getElementById('connection-status');
    if (!statusElement) return;

    // Vérifier d'abord si l'utilisateur est connecté à Internet
    if (!navigator.onLine) {
        statusElement.innerHTML = `
            <i class="fas fa-wifi-slash text-error text-xs"></i>
            <span class="text-sm">Vous n'êtes pas connecté à Internet</span>
        `;
        return;
    }

    let html = '';
    switch(status) {
        case 'connecting':
            html = `
                <span class="loading loading-spinner loading-xs text-primary"></span>
                <span class="text-sm">Connexion en cours...</span>
            `;
            break;
        case 'connected':
            html = `
                <i class="fas fa-circle text-success text-xs"></i>
                <span class="text-sm">Connecté</span>
            `;
            break;
        case 'disconnected':
            html = `
                <i class="fas fa-circle text-error text-xs"></i>
                <span class="text-sm">Reconnexion...</span>
            `;
            break;
        case 'error':
            html = `
                <i class="fas fa-exclamation-triangle text-warning text-xs"></i>
                <span class="text-sm">${message || 'Erreur de connexion'}</span>
            `;
            break;
    }
    statusElement.innerHTML = html;
}

// Renommage de la fonction connect en initializeWebSocket
function initializeWebSocket() {
    updateConnectionStatus('connecting');
    let roomPk = document.querySelector(DOM_SELECTORS.roomPk).value;

    chatSocket = new WebSocket(
        `ws://${window.location.host}/ws/rooms/${roomPk}/`
    );

    chatSocket.onopen = function(e) {
        console.log("Successfully connected to the WebSocket server.");
        updateConnectionStatus('connected');
    }

    chatSocket.onclose = function(e) {
        console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 5s...");
        updateConnectionStatus('disconnected');
        setTimeout(function() {
            console.log("Reconnecting...");
            initializeWebSocket();
        }, 5000);
    };

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const handler = messageHandlers[data.type];
        
        if (handler) {
            handler(data);
            removeEmptyMessage();
        } else {
            console.error("Unknown message type!");
        }
    };

    chatSocket.onerror = function(err) {
        console.log("WebSocket encountered an error: " + err.message);
        console.log("Closing the socket.");
        updateConnectionStatus('error', "Erreur de connexion au serveur");
        chatSocket.close();
    }
}
initializeWebSocket();

MessageSend.onclick = function() {
    if (MessageInput.value.length === 0 || !chatSocket) {
        return;
    }
    chatSocket.send(JSON.stringify({
        "content": MessageInput.value,
    }));
    MessageInput.value = "";
};

// Ajouter les écouteurs d'événements pour la connexion Internet
window.addEventListener('online', function() {
    if (chatSocket?.readyState !== WebSocket.OPEN) {
        initializeWebSocket();
    } else {
        updateConnectionStatus('connected');
    }
});

window.addEventListener('offline', function() {
    updateConnectionStatus('error', "Vous n'êtes pas connecté à Internet");
});

});