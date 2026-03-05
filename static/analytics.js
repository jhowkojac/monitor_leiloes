// Advanced Analytics Tracker
class AnalyticsTracker {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.userId = null;
        this.isTracking = false;
        
        // Configuração
        this.config = {
            trackPageViews: true,
            trackClicks: true,
            trackSearches: true,
            trackFilters: true,
            trackPerformance: true,
            trackScrollDepth: true,
            apiEndpoint: '/api/analytics/track'
        };
        
        this.init();
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    init() {
        // Aguardar carregamento completo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.startTracking());
        } else {
            this.startTracking();
        }
    }
    
    startTracking() {
        if (this.isTracking) return;
        
        this.isTracking = true;
        console.log('Analytics tracking iniciado');
        
        // Track page view inicial
        this.trackPageView();
        
        // Configurar listeners
        this.setupEventListeners();
        
        // Track performance
        if (this.config.trackPerformance) {
            this.trackInitialPerformance();
        }
    }
    
    setupEventListeners() {
        // Page views (SPA)
        let lastPage = location.pathname;
        new MutationObserver(() => {
            if (location.pathname !== lastPage) {
                lastPage = location.pathname;
                this.trackPageView();
            }
        }).observe(document, { subtree: true, childList: true });
        
        // Clicks em elementos importantes
        if (this.config.trackClicks) {
            document.addEventListener('click', (e) => this.trackClick(e));
        }
        
        // Formulários de busca
        if (this.config.trackSearches) {
            document.addEventListener('submit', (e) => this.trackSearch(e));
        }
        
        // Filtros
        if (this.config.trackFilters) {
            document.addEventListener('change', (e) => this.trackFilter(e));
        }
        
        // Scroll depth
        if (this.config.trackScrollDepth) {
            let maxScroll = 0;
            window.addEventListener('scroll', () => {
                const scrollPercent = Math.round(
                    (window.scrollY + window.innerHeight) / document.body.scrollHeight * 100
                );
                if (scrollPercent > maxScroll) {
                    maxScroll = scrollPercent;
                    this.trackScrollDepth(maxScroll);
                }
            });
        }
        
        // Performance de carregamento
        window.addEventListener('load', () => {
            if (this.config.trackPerformance) {
                this.trackPageLoadTime();
            }
        });
        
        // Unload
        window.addEventListener('beforeunload', () => {
            this.trackSessionEnd();
        });
    }
    
    async trackEvent(eventType, data = {}) {
        const eventData = {
            event_type: eventType,
            user_id: this.userId,
            session_id: this.sessionId,
            data: data,
            page: location.pathname,
            referrer: document.referrer,
            user_agent: navigator.userAgent,
            timestamp: Date.now()
        };
        
        try {
            await fetch(this.config.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(eventData)
            });
        } catch (error) {
            console.error('Erro ao track evento:', error);
        }
    }
    
    trackPageView() {
        if (!this.config.trackPageViews) return;
        
        this.trackEvent('page_view', {
            page: location.pathname,
            title: document.title,
            url: window.location.href,
            referrer: document.referrer
        });
    }
    
    trackClick(event) {
        const target = event.target;
        const element = target.closest('[data-analytics]');
        
        if (!element) return;
        
        const analyticsData = element.dataset.analytics ? 
            JSON.parse(element.dataset.analytics) : {};
        
        this.trackEvent('click', {
            element: element.tagName.toLowerCase(),
            text: element.textContent?.trim(),
            id: element.id,
            class: element.className,
            data: analyticsData
        });
    }
    
    trackSearch(event) {
        const form = event.target;
        const searchInput = form.querySelector('input[type="search"], input[name*="search"], input[name*="busca"]');
        
        if (!searchInput) return;
        
        const searchTerm = searchInput.value?.trim();
        if (!searchTerm) return;
        
        this.trackEvent('search', {
            search_term: searchTerm,
            form_id: form.id,
            form_action: form.action
        });
    }
    
    trackFilter(event) {
        const target = event.target;
        
        // Verificar se é um elemento de filtro
        if (target.matches('select') || 
            target.matches('input[type="checkbox"]') ||
            target.matches('input[type="radio"]') ||
            (target.matches('input') && target.name?.includes('filtro'))) {
            
            this.trackEvent('filter', {
                filter_name: target.name || target.id,
                filter_value: target.value || target.checked,
                filter_type: target.type
            });
        }
    }
    
    trackInitialPerformance() {
        // Navigation timing
        if (performance.timing) {
            const timing = performance.timing;
            
            this.trackEvent('performance', {
                metric_name: 'dom_interactive',
                value: timing.domInteractive - timing.navigationStart,
                unit: 'ms'
            });
            
            this.trackEvent('performance', {
                metric_name: 'dom_complete',
                value: timing.domComplete - timing.navigationStart,
                unit: 'ms'
            });
            
            this.trackEvent('performance', {
                metric_name: 'load_complete',
                value: timing.loadEventEnd - timing.navigationStart,
                unit: 'ms'
            });
        }
    }
    
    trackPageLoadTime() {
        if (performance.timing) {
            const timing = performance.timing;
            
            this.trackEvent('performance', {
                metric_name: 'page_load_time',
                value: timing.loadEventEnd - timing.navigationStart,
                unit: 'ms'
            });
        }
    }
    
    trackScrollDepth(depth) {
        this.trackEvent('scroll_depth', {
            max_scroll_percent: depth,
            page_height: document.body.scrollHeight,
            viewport_height: window.innerHeight
        });
    }
    
    trackSessionEnd() {
        this.trackEvent('session_end', {
            session_duration: Date.now() - this.sessionStartTime,
            page_views: this.pageViewCount,
            final_page: location.pathname
        });
    }
    
    setUserId(userId) {
        this.userId = userId;
        this.trackEvent('user_identified', {
            user_id: userId
        });
    }
    
    configure(newConfig) {
        this.config = { ...this.config, ...newConfig };
    }
    
    // Métodos para uso manual
    async trackCustomEvent(eventType, data) {
        await this.trackEvent(eventType, data);
    }
    
    async trackPerformanceMetric(name, value, unit = 'ms') {
        await this.trackEvent('performance', {
            metric_name: name,
            value: value,
            unit: unit
        });
    }
    
    // Propriedades
    get pageViewCount() {
        return this._pageViewCount || 0;
    }
    
    set pageViewCount(count) {
        this._pageViewCount = count;
    }
    
    get sessionStartTime() {
        return this._sessionStartTime || Date.now();
    }
    
    set sessionStartTime(time) {
        this._sessionStartTime = time;
    }
}

// Instância global
window.analyticsTracker = new AnalyticsTracker();

// Funções auxiliares globais
window.trackAnalyticsEvent = async (eventType, data) => {
    await window.analyticsTracker.trackCustomEvent(eventType, data);
};

window.trackPerformanceMetric = async (name, value, unit) => {
    await window.analyticsTracker.trackPerformanceMetric(name, value, unit);
};

window.setAnalyticsUserId = (userId) => {
    window.analyticsTracker.setUserId(userId);
};

// Inicializar automaticamente
document.addEventListener('DOMContentLoaded', () => {
    // Tentar obter user_id do dashboard se disponível
    if (window.currentUser) {
        window.analyticsTracker.setUserId(window.currentUser.id);
    }
});
