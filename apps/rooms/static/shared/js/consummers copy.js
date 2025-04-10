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
    
    // Gestionnaire de messages
    const messageHandlers = {
        room_message: (data) => {
            const messageContainer = document.querySelector(DOM_SELECTORS.messageContainer);
            const currentUser = document.querySelector(DOM_SELECTORS.username)?.value;
            const isCurrentUser = data.username === currentUser;
            
            const messageHTML = `
                <div class="chat ${isCurrentUser ? 'chat-end' : 'chat-start'}">
                    <div class="chat-header">
                        ${data.username}
                        <time class="text-xs opacity-50 ml-1">${formatDate(data.created_at)}</time>
                    </div>
                    <div class="chat-bubble ${isCurrentUser ? 'chat-bubble-primary' : ''}">
                        ${data.message}
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
                .some(div => div.textContent.includes(data.username));
            
            if (!existingOnlineUser) {
                onlineUsers.insertAdjacentHTML('beforeend', createUserElement(data.username, true));
                
                Array.from(offlineUsers.children)
                    .filter(div => div.textContent.includes(data.username))
                    .forEach(div => div.remove());
    
                if (data.type_message === "user_join") {
                    document.querySelector(DOM_SELECTORS.messageContainer)
                        .insertAdjacentHTML('beforeend', 
                            createSystemMessage(data.username, 'rejoint', data.joined_at, roomName));
                }
                scrollToBottom();
            }
        },
    
        room_leave: (data) => {
            const onlineUsers = document.querySelector(DOM_SELECTORS.onlineUsers);
            const offlineUsers = document.querySelector(DOM_SELECTORS.offlineUsers);
            const roomName = document.querySelector(DOM_SELECTORS.roomName).value;
            
            Array.from(onlineUsers.children)
                .filter(div => div.textContent.includes(data.username))
                .forEach(div => div.remove());
    
            offlineUsers.insertAdjacentHTML('beforeend', createUserElement(data.username, false));
            
            if (data.type_message === "user_leave") {
                document.querySelector(DOM_SELECTORS.messageContainer)
                    .insertAdjacentHTML('beforeend', 
                        createSystemMessage(data.username, 'quitté', data.left_at, roomName));
            }
            scrollToBottom();
        }
    };
    
    // Renommage de la fonction connect en initializeWebSocket
    function initializeWebSocket() {
        let roomPk = document.querySelector(DOM_SELECTORS.roomPk).value;
    
        chatSocket = new WebSocket(
            `ws://${window.location.host}/ws/rooms/${roomPk}/`
        );
    
        chatSocket.onopen = function(e) {
            console.log("Successfully connected to the WebSocket server.");
        }
    
        chatSocket.onclose = function(e) {
            console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 1s...");
            setTimeout(function() {
                console.log("Reconnecting...");
                initializeWebSocket();
            }, 1000);
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
            chatSocket.close();
        }
    }
    initializeWebSocket();
    
    MessageSend.onclick = function() {
        if (MessageInput.value.length === 0 || !chatSocket) {
            return;
        }
        chatSocket.send(JSON.stringify({
            "message": MessageInput.value,
        }));
        MessageInput.value = "";
        };
    });
    
    