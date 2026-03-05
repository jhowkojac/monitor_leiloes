// PWA Manager - Progressive Web App Features
class PWAManager {
    constructor() {
        this.isInstalled = false;
        this.isOnline = navigator.onLine;
        this.deferredPrompt = null;
        
        // Verificar se está instalado
        this.checkInstalled();
        
        // Event listeners
        this.setupEventListeners();
    }
    
    checkInstalled() {
        // Verificar se está rodando como PWA instalada
        if (window.matchMedia('(display-mode: standalone)').matches) {
            this.isInstalled = true;
            console.log('PWA instalada (standalone mode)');
        } else if (window.navigator.standalone) {
            this.isInstalled = true;
            console.log('PWA instalada (iOS standalone)');
        }
    }
    
    setupEventListeners() {
        // Before install prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            console.log('Install prompt disponível');
            this.showInstallButton();
        });
        
        // App installed
        window.addEventListener('appinstalled', () => {
            this.isInstalled = true;
            this.deferredPrompt = null;
            console.log('PWA instalada com sucesso');
            this.hideInstallButton();
            this.showInstallSuccess();
        });
        
        // Online/Offline status
        window.addEventListener('online', () => {
            this.isOnline = true;
            console.log('Conectado à internet');
            this.updateOnlineStatus(true);
            this.syncData();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            console.log('Desconectado da internet');
            this.updateOnlineStatus(false);
        });
        
        // Service Worker messages
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.addEventListener('message', (event) => {
                this.handleSWMessage(event);
            });
        }
    }
    
    async registerServiceWorker() {
        if (!('serviceWorker' in navigator)) {
            console.log('Service Worker não suportado');
            return false;
        }
        
        try {
            const registration = await navigator.serviceWorker.register('/sw.js');
            console.log('Service Worker registrado:', registration);
            
            // Verificar updates
            registration.addEventListener('updatefound', () => {
                console.log('Novo Service Worker encontrado');
                this.showUpdateButton();
            });
            
            // Push subscription
            await this.subscribeToPush(registration);
            
            return true;
        } catch (error) {
            console.error('Erro ao registrar Service Worker:', error);
            return false;
        }
    }
    
    async subscribeToPush(registration) {
        if (!('PushManager' in window)) {
            console.log('Push notifications não suportadas');
            return;
        }
        
        try {
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array('YOUR_VAPID_PUBLIC_KEY')
            });
            
            console.log('Push subscription:', subscription);
            
            // Enviar subscription para backend
            await this.sendPushSubscription(subscription);
            
        } catch (error) {
            console.error('Erro ao subscriver push:', error);
        }
    }
    
    async sendPushSubscription(subscription) {
        try {
            const response = await fetch('/api/pwa/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(subscription)
            });
            
            if (response.ok) {
                console.log('Push subscription salva no backend');
            }
        } catch (error) {
            console.error('Erro ao salvar push subscription:', error);
        }
    }
    
    async installApp() {
        if (!this.deferredPrompt) {
            console.log('Install prompt não disponível');
            return;
        }
        
        try {
            this.deferredPrompt.prompt();
            const { outcome } = await this.deferredPrompt.userChoice;
            
            if (outcome === 'accepted') {
                console.log('Usuário aceitou instalação');
            } else {
                console.log('Usuário recusou instalação');
            }
            
            this.deferredPrompt = null;
            this.hideInstallButton();
            
        } catch (error) {
            console.error('Erro na instalação:', error);
        }
    }
    
    showInstallButton() {
        const button = document.getElementById('pwa-install-btn');
        if (button) {
            button.style.display = 'block';
            button.addEventListener('click', () => this.installApp());
        }
    }
    
    hideInstallButton() {
        const button = document.getElementById('pwa-install-btn');
        if (button) {
            button.style.display = 'none';
        }
    }
    
    showUpdateButton() {
        const button = document.getElementById('pwa-update-btn');
        if (button) {
            button.style.display = 'block';
            button.addEventListener('click', () => this.updateApp());
        }
    }
    
    async updateApp() {
        if ('serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.ready;
            registration.waiting.postMessage({ type: 'SKIP_WAITING' });
            
            // Recarregar página
            window.location.reload();
        }
    }
    
    showInstallSuccess() {
        this.showNotification('PWA Instalada!', 'Aplicativo instalado com sucesso. Acesse pela tela inicial.');
    }
    
    updateOnlineStatus(isOnline) {
        const status = document.getElementById('online-status');
        if (status) {
            status.textContent = isOnline ? '🟢 Online' : '🔴 Offline';
            status.className = isOnline ? 'online' : 'offline';
        }
        
        // Atualizar UI baseada no status
        this.updateUIForConnection(isOnline);
    }
    
    updateUIForConnection(isOnline) {
        const forms = document.querySelectorAll('form');
        const buttons = document.querySelectorAll('button');
        
        if (isOnline) {
            // Habilitar elementos interativos
            forms.forEach(form => form.style.opacity = '1');
            buttons.forEach(button => {
                button.disabled = false;
                button.style.opacity = '1';
            });
        } else {
            // Desabilitar elementos interativos
            forms.forEach(form => form.style.opacity = '0.7');
            buttons.forEach(button => {
                button.disabled = true;
                button.style.opacity = '0.5';
            });
        }
    }
    
    async syncData() {
        // Sincronizar dados quando voltar online
        if ('serviceWorker' in navigator) {
            const registration = await navigator.serviceWorker.ready;
            registration.sync.register('sync-leiloes');
        }
    }
    
    handleSWMessage(event) {
        const { type, data } = event.data;
        
        switch (type) {
            case 'CACHE_UPDATED':
                console.log('Cache atualizado:', data);
                this.showNotification('Dados Atualizados', 'O conteúdo foi atualizado com sucesso.');
                break;
                
            case 'SYNC_COMPLETE':
                console.log('Sync completo:', data);
                this.showNotification('Sincronizado', 'Dados sincronizados com sucesso.');
                break;
                
            default:
                console.log('Mensagem do SW:', type, data);
        }
    }
    
    showNotification(title, body, options = {}) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body,
                icon: '/static/icons/icon-192x192.png',
                badge: '/static/icons/icon-72x72.png',
                ...options
            });
        }
    }
    
    async requestNotificationPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            console.log('Permissão de notificação:', permission);
            return permission === 'granted';
        }
        return false;
    }
    
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);
        
        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        
        return outputArray;
    }
    
    // Métodos públicos
    async init() {
        await this.registerServiceWorker();
        await this.requestNotificationPermission();
        
        // Mostrar status inicial
        this.updateOnlineStatus(this.isOnline);
        
        // Se não estiver instalado, mostrar botão de instalação
        if (!this.isInstalled) {
            setTimeout(() => {
                if (this.deferredPrompt) {
                    this.showInstallButton();
                }
            }, 3000);
        }
    }
}

// Instância global
window.pwaManager = new PWAManager();

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.pwaManager.init();
});
