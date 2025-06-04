// Ordinal Frame - Main JavaScript
// Clean, lint-free JavaScript with proper separation from templates

class OrdinalFrame {
    constructor() {
        this.ordinals = [];
        this.currentIndex = 0;
        this.showingMetadata = false;
        this.metadataTimeout = null;
        this.slideshowInterval = null;
        this.isPlaying = true;
        
        // Get configuration from data attributes
        this.slideshowDuration = this.getSlideshowInterval() * 1000;
        
        // DOM elements
        this.loadingEl = document.getElementById('loadingState');
        this.errorEl = document.getElementById('errorState');
        this.containerEl = document.getElementById('ordinalContainer');
        this.metadataEl = document.getElementById('metadataOverlay');
        this.navEl = document.getElementById('navIndicators');
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.slideshowIndicator = document.getElementById('slideshowIndicator');
        
        this.init();
    }
    
    getSlideshowInterval() {
        const intervalData = document.body.dataset.slideshowInterval;
        return parseInt(intervalData) || 30;
    }
    
    async init() {
        await this.loadOrdinals();
        this.setupEventListeners();
        
        if (this.ordinals.length > 0) {
            this.showOrdinal(0);
            this.createNavIndicators();
            this.startSlideshow();
            this.hideLoading();
        } else {
            this.showError();
        }
    }
    
    async loadOrdinals() {
        try {
            // Try window.frameData first, then data attributes
            if (window.frameData && window.frameData.ordinals) {
                this.ordinals = window.frameData.ordinals;
            } else {
                const ordinalsData = document.body.dataset.ordinals;
                this.ordinals = JSON.parse(ordinalsData);
            }
        } catch (error) {
            console.error('Error loading ordinals data:', error);
            this.ordinals = [];
        }
        
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    setupEventListeners() {
        // Touch/click to cycle
        this.containerEl.addEventListener('click', (e) => {
            e.preventDefault();
            this.nextOrdinal();
        });
        
        this.containerEl.addEventListener('touchend', (e) => {
            e.preventDefault();
            this.nextOrdinal();
        });
        
        // Long press for metadata
        let pressTimer = null;
        let touchStartTime = 0;
        
        const startPress = () => {
            touchStartTime = Date.now();
            pressTimer = setTimeout(() => this.toggleMetadata(), 500);
        };
        
        const endPress = () => {
            const pressDuration = Date.now() - touchStartTime;
            clearTimeout(pressTimer);
            if (pressDuration < 300) {
                this.nextOrdinal();
            }
        };
        
        this.containerEl.addEventListener('mousedown', startPress);
        this.containerEl.addEventListener('mouseup', endPress);
        this.containerEl.addEventListener('mouseleave', () => clearTimeout(pressTimer));
        this.containerEl.addEventListener('touchstart', startPress);
        this.containerEl.addEventListener('touchend', endPress);
        
        // Play/pause button
        this.playPauseBtn.addEventListener('click', () => this.toggleSlideshow());
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowRight':
                case ' ':
                    e.preventDefault();
                    this.nextOrdinal();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.previousOrdinal();
                    break;
                case 'i':
                case 'I':
                    this.toggleMetadata();
                    break;
                case 'p':
                case 'P':
                    this.toggleSlideshow();
                    break;
            }
        });
    }
    
    showOrdinal(index) {
        if (index < 0 || index >= this.ordinals.length) return;
        
        this.currentIndex = index;
        const ordinal = this.ordinals[index];
        
        // Clear container
        this.containerEl.style.display = 'none';
        this.containerEl.innerHTML = '';
        
        const contentUrl = `/content/${ordinal.id}`;
        
        if (ordinal.content_type && ordinal.content_type.includes('text/html')) {
            // Handle HTML content (like Quantum Cats)
            this.loadHTMLContent(ordinal, contentUrl);
        } else {
            // Handle image content
            this.loadImageContent(ordinal, contentUrl);
        }
        
        this.updateMetadata(ordinal);
    }
    
    loadHTMLContent(ordinal, contentUrl) {
        this.containerEl.innerHTML = `
            <iframe src="${contentUrl}" 
                    style="width: 800px; height: 600px; max-width: 90vw; max-height: 70vh; border: none; background: #000; border-radius: 8px;"
                    title="Inscription #${ordinal.number}">
            </iframe>
        `;
        
        // Show the container
        this.containerEl.style.display = 'flex';
        this.updateNavIndicators();
    }
    
    loadImageContent(ordinal, contentUrl) {
        this.containerEl.innerHTML = `
            <img src="${contentUrl}" 
                 alt="Inscription #${ordinal.number}"
                 style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 8px;"
                 onload="this.parentElement.style.display='flex'"
                 onerror="this.parentElement.innerHTML='<div class=&quot;ordinal-fallback&quot;><div class=&quot;icon&quot;>🖼️</div><div class=&quot;title&quot;>Image Loading Error</div></div>'; this.parentElement.style.display='flex'">
        `;
        
        // Show the container immediately for images
        this.containerEl.style.display = 'flex';
        this.updateNavIndicators();
    }
    
    updateMetadata(ordinal) {
        document.getElementById('inscriptionNumber').textContent = `Inscription #${ordinal.number}`;
        document.getElementById('inscriptionId').textContent = ordinal.id;
        
        const collectionInfo = document.getElementById('collectionInfo');
        let infoHTML = `<strong>Type:</strong> ${ordinal.content_type || 'Unknown'}<br>`;
        infoHTML += `<strong>Size:</strong> ${this.formatFileSize(ordinal.content_length)}<br>`;
        if (ordinal.collection_slug) {
            infoHTML += `<strong>Collection:</strong> ${ordinal.collection_slug}<br>`;
        }
        infoHTML += `<strong>Block:</strong> ${ordinal.block_height || 'Unknown'}`;
        collectionInfo.innerHTML = infoHTML;
        
        const rarityBadge = document.getElementById('rarityBadge');
        const rarity = ordinal.sat_rarity || 'common';
        rarityBadge.textContent = rarity;
        rarityBadge.className = `rarity-badge rarity-${rarity.toLowerCase()}`;
    }
    
    formatFileSize(bytes) {
        if (!bytes) return 'Unknown';
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }
    
    nextOrdinal() {
        this.hideMetadata();
        const nextIndex = (this.currentIndex + 1) % this.ordinals.length;
        this.showOrdinal(nextIndex);
        this.resetSlideshow();
    }
    
    previousOrdinal() {
        this.hideMetadata();
        const prevIndex = (this.currentIndex - 1 + this.ordinals.length) % this.ordinals.length;
        this.showOrdinal(prevIndex);
        this.resetSlideshow();
    }
    
    toggleMetadata() {
        if (this.showingMetadata) {
            this.hideMetadata();
        } else {
            this.showMetadata();
        }
    }
    
    showMetadata() {
        this.metadataEl.classList.add('show');
        this.showingMetadata = true;
        clearTimeout(this.metadataTimeout);
        this.metadataTimeout = setTimeout(() => this.hideMetadata(), 5000);
    }
    
    hideMetadata() {
        this.metadataEl.classList.remove('show');
        this.showingMetadata = false;
        clearTimeout(this.metadataTimeout);
    }
    
    createNavIndicators() {
        this.navEl.innerHTML = '';
        this.ordinals.forEach((_, index) => {
            const dot = document.createElement('div');
            dot.className = 'nav-dot';
            dot.addEventListener('click', () => {
                this.showOrdinal(index);
                this.resetSlideshow();
            });
            this.navEl.appendChild(dot);
        });
        this.updateNavIndicators();
    }
    
    updateNavIndicators() {
        const dots = this.navEl.querySelectorAll('.nav-dot');
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === this.currentIndex);
        });
    }
    
    startSlideshow() {
        if (this.ordinals.length <= 1) return;
        
        this.slideshowInterval = setInterval(() => {
            if (!this.showingMetadata && this.isPlaying) {
                this.nextOrdinal();
            }
        }, this.slideshowDuration);
        
        this.updateSlideshowIndicator();
    }
    
    resetSlideshow() {
        if (this.slideshowInterval) {
            clearInterval(this.slideshowInterval);
            this.startSlideshow();
        }
    }
    
    toggleSlideshow() {
        this.isPlaying = !this.isPlaying;
        this.playPauseBtn.textContent = this.isPlaying ? '⏸️' : '▶️';
        this.updateSlideshowIndicator();
    }
    
    updateSlideshowIndicator() {
        const seconds = this.slideshowDuration / 1000;
        this.slideshowIndicator.textContent = this.isPlaying ? 
            `Auto: ${seconds}s` : 'Paused';
        this.slideshowIndicator.classList.toggle('paused', !this.isPlaying);
    }
    
    hideLoading() {
        this.loadingEl.style.display = 'none';
    }
    
    showError() {
        this.loadingEl.style.display = 'none';
        this.errorEl.style.display = 'flex';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.ordinalFrame = new OrdinalFrame();
});