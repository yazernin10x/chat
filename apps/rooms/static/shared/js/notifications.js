document.addEventListener("DOMContentLoaded", function () {
    if (checkNotificationPermission()) {
      registerServiceWorker()
        .then((registration) => {
          initializeWebSocket(registration)
        })
        .catch((error) => {
          console.error(
            "Erreur lors de l'enregistrement du Service Worker:",
            error
          );
        });
    } else {
      console.log("Notification refusée");
    }

    function checkNotificationPermission() {
      if ("Notification" in window) {
        return Notification.requestPermission().then((permission) => {
          if (permission === "granted") {
            return true;
          } else {
            return false;
          }
        });
      } else {
        return Promise.resolve(false);
      }
    }

    function registerServiceWorker() {
      if ("serviceWorker" in navigator) {
        return navigator.serviceWorker
          .register("{% static 'js/sw.js' %}")
          .then((registration) => {
            return registration;
          })
          .catch((error) => {
            return Promise.reject(error);
          });
      } else {
        return Promise.reject(new Error("Service Worker non supporté"));
      }
    }

    function showNotification(registration, data) {
        // Envoyer un message au Service Worker pour afficher une notification
        registration.active.postMessage({
          action: "showNotification",
          data: {
            title: data.title,
            content: data.content,
          }
        });
    }

    function initializeWebSocket(registration) {
      const socket = new WebSocket(
        "ws://" + window.location.host + "/ws/notifications"
      );

      socket.onopen = function(e) {
          showNotification(registration, {
            title: "Connexion reussie",
            content: "Successfully connected to the WebSocket server."
          });
      }

      socket.onclose = function(e) {
        console.log("WebSocket connection closed unexpectedly. Trying to reconnect in 1s...");
          setTimeout(function() {
              console.log("Reconnecting...");
              initializeWebSocket();
          }, 1000);
      };


      socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.type === "notification") {
          showNotification(registration, data);
          socket.send(JSON.stringify({type: "acknowledgment"}));
        }
      };

      socket.onerror = function (err) {
        console.log("WebSocket encountered an error: " + err.message);
        console.log("Closing the socket.");
        socket.close();
      };
      return socket;
    }
});