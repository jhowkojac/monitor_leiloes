// Theme Customization Manager
class ThemeManager {
    constructor() {
        this.currentTheme = 'default';
        this.systemPreference = 'default';
        this.customThemes = {};
        this.userPreferences = {};
        
        this.init();
    }
    
    async init() {
        // Detectar preferência do sistema
        this.detectSystemPreference();
        
        // Carregar preferências do usuário
        await this.loadUserPreferences();
        
        // Aplicar tema inicial
        this.applyTheme(this.currentTheme);
        
        // Configurar listeners
        this.setupEventListeners();
        
        // Observar mudanças no sistema
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)')
                .addEventListener('change', (e) => {
                    this.systemPreference = e.matches ? 'dark' : 'light';
                    if (this.userPreferences.auto_switch) {
                        this.autoSwitchTheme();
                    }
                });
        }
    }
    
    detectSystemPreference() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.systemPreference = 'dark';
        } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
            this.systemPreference = 'light';
        } else {
            this.systemPreference = 'default';
        }
    }
    
    setupEventListeners() {
        // Theme switcher buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-theme-switch]')) {
                const theme = e.target.dataset.themeSwitch;
                this.switchTheme(theme);
            }
        });
        
        // Theme customizer
        document.addEventListener('change', (e) => {
            if (e.target.matches('[data-theme-customizer]')) {
                this.handleCustomizerChange(e);
            }
        });
        
        // Save custom theme
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-save-theme]')) {
                this.saveCustomTheme();
            }
        });
    }
    
    async loadUserPreferences() {
        try {
            // Aqui você carregaria as preferências do backend
            // Por ora, usar localStorage
            const stored = localStorage.getItem('theme-preferences');
            if (stored) {
                this.userPreferences = JSON.parse(stored);
                this.currentTheme = this.userPreferences.theme || 'default';
            }
        } catch (error) {
            console.error('Erro ao carregar preferências:', error);
        }
    }
    
    async saveUserPreferences() {
        try {
            // Aqui você salvaria as preferências no backend
            // Por ora, usar localStorage
            localStorage.setItem('theme-preferences', JSON.stringify(this.userPreferences));
            
            // Enviar para backend se usuário estiver logado
            if (window.currentUser) {
                await this.syncPreferencesWithBackend();
            }
        } catch (error) {
            console.error('Erro ao salvar preferências:', error);
        }
    }
    
    async syncPreferencesWithBackend() {
        try {
            const response = await fetch(`/api/theme/preferences/${window.currentUser.id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.userPreferences)
            });
            
            if (response.ok) {
                console.log('Preferências sincronizadas com backend');
            }
        } catch (error) {
            console.error('Erro ao sincronizar preferências:', error);
        }
    }
    
    async switchTheme(themeName) {
        if (themeName === this.currentTheme) return;
        
        try {
            // Carregar tema
            const theme = await this.loadTheme(themeName);
            if (!theme) {
                console.error(`Tema ${themeName} não encontrado`);
                return;
            }
            
            // Aplicar tema
            this.applyTheme(theme);
            
            // Atualizar preferências
            this.currentTheme = themeName;
            this.userPreferences.theme = themeName;
            
            // Salvar preferências
            await this.saveUserPreferences();
            
            // Disparar evento
            this.dispatchThemeChange(themeName);
            
        } catch (error) {
            console.error('Erro ao trocar tema:', error);
        }
    }
    
    async loadTheme(themeName) {
        try {
            // Tentar carregar temas disponíveis
            const response = await fetch('/api/theme/themes');
            const data = await response.json();
            
            return data.themes[themeName];
        } catch (error) {
            console.error('Erro ao carregar tema:', error);
            return null;
        }
    }
    
    applyTheme(theme) {
        if (!theme) return;
        
        // Aplicar variáveis CSS
        const root = document.documentElement;
        const colors = theme.colors || {};
        const fonts = theme.fonts || {};
        
        // Aplicar cores
        Object.keys(colors).forEach(key => {
            root.style.setProperty(`--${key}`, colors[key]);
        });
        
        // Aplicar fontes
        Object.keys(fonts).forEach(key => {
            root.style.setProperty(`--font-${key}`, fonts[key]);
        });
        
        // Aplicar border radius
        if (theme.border_radius) {
            root.style.setProperty('--border-radius', theme.border_radius);
        }
        
        // Aplicar shadows
        if (theme.shadows) {
            const shadowValue = theme.shadows === 'enabled' ? '0 4px 6px rgba(0, 0, 0, 0.1)' : 'none';
            root.style.setProperty('--card-shadow', shadowValue);
        }
        
        // Atualizar atributo no body
        document.body.setAttribute('data-theme', theme.name);
        
        // Atualizar tema system
        this.updateSystemTheme(theme.name);
    }
    
    updateSystemTheme(themeName) {
        const systemThemeElement = document.getElementById('system-theme');
        if (systemThemeElement) {
            systemThemeElement.textContent = `Tema: ${theme.name}`;
        }
    }
    
    autoSwitchTheme() {
        let targetTheme;
        
        switch (this.userPreferences.system_preference) {
            case 'auto':
                targetTheme = this.systemPreference === 'dark' ? 'dark' : 'light';
                break;
            case 'dark':
                targetTheme = 'dark';
                break;
            case 'light':
                targetTheme = 'light';
                break;
            default:
                targetTheme = this.userPreferences.theme || 'default';
        }
        
        this.switchTheme(targetTheme);
    }
    
    async createCustomTheme(name, customizations) {
        try {
            const response = await fetch('/api/theme/custom', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    base_theme: this.currentTheme,
                    customizations: customizations
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.customThemes[name] = data.theme;
                console.log('Tema customizado criado:', name);
                return data;
            } else {
                throw new Error('Erro ao criar tema customizado');
            }
        } catch (error) {
            console.error('Erro ao criar tema customizado:', error);
            throw error;
        }
    }
    
    handleCustomizerChange(event) {
        const target = event.target;
        const property = target.dataset.themeCustomizer;
        const value = target.type === 'checkbox' ? target.checked : target.value;
        
        // Aplicar preview em tempo real
        if (property.startsWith('color-')) {
            const cssVar = property.replace('color-', '');
            document.documentElement.style.setProperty(`--${cssVar}`, value);
        } else if (property === 'border-radius') {
            document.documentElement.style.setProperty('--border-radius', `${value}px`);
        } else if (property === 'shadows') {
            const shadowValue = value ? '0 4px 6px rgba(0, 0, 0, 0.1)' : 'none';
            document.documentElement.style.setProperty('--card-shadow', shadowValue);
        }
    }
    
    async saveCustomTheme() {
        const name = prompt('Nome do tema customizado:');
        if (!name) return;
        
        // Coletar customizações atuais
        const customizations = {};
        
        // Cores customizadas
        const colorInputs = document.querySelectorAll('[data-theme-customizer^="color-"]');
        colorInputs.forEach(input => {
            const cssVar = input.dataset.themeCustomizer.replace('color-', '');
            customizations.colors = customizations.colors || {};
            customizations.colors[cssVar] = input.value;
        });
        
        // Outras customizações
        const borderRadius = document.querySelector('[data-theme-customizer="border-radius"]');
        if (borderRadius) {
            customizations.border_radius = `${borderRadius.value}px`;
        }
        
        const shadows = document.querySelector('[data-theme-customizer="shadows"]');
        if (shadows) {
            customizations.shadows = shadows.checked;
        }
        
        try {
            await this.createCustomTheme(name, customizations);
            alert(`Tema "${name}" criado com sucesso!`);
        } catch (error) {
            alert('Erro ao criar tema customizado');
        }
    }
    
    dispatchThemeChange(themeName) {
        const event = new CustomEvent('themechange', {
            detail: { theme: themeName, manager: this }
        });
        document.dispatchEvent(event);
    }
    
    // Métodos públicos
    getCurrentTheme() {
        return this.currentTheme;
    }
    
    getAvailableThemes() {
        return this.themes;
    }
    
    async refreshThemes() {
        try {
            const response = await fetch('/api/theme/themes');
            const data = await response.json();
            return data.themes;
        } catch (error) {
            console.error('Erro ao atualizar temas:', error);
            return {};
        }
    }
    
    // Propriedades
    get themes() {
        return {
            ...this.defaultThemes,
            ...this.customThemes
        };
    }
    
    get defaultThemes() {
        return {
            'default': { name: 'Padrão', icon: '🎨' },
            'dark': { name: 'Escuro', icon: '🌙' },
            'light': { name: 'Claro', icon: '☀️' },
            'high_contrast': { name: 'Alto Contraste', icon: '👁' }
        };
    }
}

// Instância global
window.themeManager = new ThemeManager();

// Funções auxiliares globais
window.switchTheme = async (themeName) => {
    await window.themeManager.switchTheme(themeName);
};

window.createCustomTheme = async (name, customizations) => {
    return await window.themeManager.createCustomTheme(name, customizations);
};

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.themeManager.init();
});
