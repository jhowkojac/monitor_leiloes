// Service Worker para PWA - Monitor de Leilões
const CACHE_NAME = 'monitor-leiloes-v1';
const STATIC_CACHE = 'static-v1';
const API_CACHE = 'api-v1';

// URLs para cache
const STATIC_URLS = [
  '/',
  '/dashboard',
  '/login',
  '/setup-2fa',
  '/static/css/style.css',
  '/static/js/app.js',
  '/static/manifest.json'
];

const API_URLS = [
  '/api/leiloes',
  '/api/dashboard/stats'
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  console.log('Service Worker instalado');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => cache.addAll(STATIC_URLS))
  );
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
  console.log('Service Worker ativado');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => 
            cacheName !== STATIC_CACHE && 
            cacheName !== API_CACHE
          )
          .map((cacheName) => caches.delete(cacheName))
      );
    })
  );
});

// Interceptação de requests
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Apenas requests do mesmo domínio
  if (url.origin !== location.origin) {
    return;
  }
  
  // Estratégia de cache para diferentes tipos de conteúdo
  if (STATIC_URLS.some((staticUrl) => request.url.includes(staticUrl))) {
    // Cache first para static
    event.respondWith(cacheFirst(request));
  } else if (API_URLS.some((apiUrl) => request.url.includes(apiUrl))) {
    // Network first para API
    event.respondWith(networkFirst(request));
  } else {
    // Try network then cache para outros
    event.respondWith(networkFirst(request));
  }
});

// Estratégia Cache First
function cacheFirst(request) {
  return caches.match(request)
    .then((response) => {
      if (response) {
        return response;
      }
      
      return fetch(request)
        .then((response) => {
          // Cache de resposta bem-sucedida
          if (response.ok) {
            caches.open(STATIC_CACHE)
              .then((cache) => cache.put(request, response.clone()));
          }
          return response;
        });
    });
}

// Estratégia Network First
function networkFirst(request) {
  return fetch(request)
    .then((response) => {
      // Cache de resposta bem-sucedida
      if (response.ok) {
        const cacheName = request.url.includes('/api/') ? API_CACHE : STATIC_CACHE;
        caches.open(cacheName)
          .then((cache) => cache.put(request, response.clone()));
      }
      return response;
    })
    .catch(() => {
      // Fallback para cache se network falhar
      return caches.match(request);
    });
}

// Background Sync para dados offline
self.addEventListener('sync', (event) => {
  console.log('Background sync:', event.tag);
  
  if (event.tag === 'sync-leiloes') {
    event.waitUntil(syncLeiloes());
  }
});

// Sync de leilões quando voltar online
function syncLeiloes() {
  return fetch('/api/leiloes')
    .then((response) => response.json())
    .then((data) => {
      // Armazenar dados localmente
      localStorage.setItem('leiloes-cache', JSON.stringify(data));
      console.log('Leilões sincronizados:', data.length);
    })
    .catch((error) => {
      console.error('Erro ao sincronizar leilões:', error);
    });
}

// Push notifications
self.addEventListener('push', (event) => {
  console.log('Push notification recebida:', event);
  
  const options = {
    body: event.data ? event.data.text() : 'Novos leilões disponíveis!',
    icon: '/static/icons/icon-192x192.png',
    badge: '/static/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/',
      timestamp: Date.now()
    },
    actions: [
      {
        action: 'view',
        title: 'Ver Leilões',
        icon: '/static/icons/icon-96x96.png'
      },
      {
        action: 'dismiss',
        title: 'Ignorar'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Monitor de Leilões', options)
  );
});

// Click em notificação
self.addEventListener('notificationclick', (event) => {
  console.log('Notificação clicada:', event);
  
  event.notification.close();
  
  if (event.action === 'view') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/')
    );
  } else if (event.action === 'dismiss') {
    // Apenas fechar a notificação
  } else {
    // Click na notificação (sem ação específica)
    event.waitUntil(
      clients.openWindow(event.notification.data.url || '/')
    );
  }
});
