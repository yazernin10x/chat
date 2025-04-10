self.addEventListener('install', event => {
    self.skipWaiting(); 
  });
  
  self.addEventListener('activate', event => {
    event.waitUntil(clients.claim());
  });

self.addEventListener('message', function(event) {
    if (event.data.action === 'showNotification') {
        const { title, content } = event.data.data;
        self.registration.showNotification(title, {
            body: content,
        });
    }
});
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
});