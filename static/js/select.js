// Ordinal Frame - Select Page JavaScript
// Clean, lint-free JavaScript for ordinal selection

class SelectionManager {
    constructor() {
        this.selectedIds = new Set();
        this.ordinals = [];
        this.totalCount = 0;
        
        // DOM elements
        this.saveButton = document.getElementById('saveButton');
        this.saveButtonText = document.getElementById('saveButtonText');
        this.resultMessage = document.getElementById('resultMessage');
        this.totalCountEl = document.getElementById('totalCount');
        this.selectedCountEl = document.getElementById('selectedCount');
        this.imageCountEl = document.getElementById('imageCount');
        
        // Buttons
        this.selectAllBtn = document.getElementById('selectAllBtn');
        this.selectNoneBtn = document.getElementById('selectNoneBtn');
        this.selectRareBtn = document.getElementById('selectRareBtn');
        
        this.init();
    }
    
    init() {
        this.loadData();
        this.setupEventListeners();
        this.loadExistingSelection();
        this.updateUI();
    }
    
    loadData() {
        try {
            // Get ordinals data from data attributes
            const ordinalsData = document.body.dataset.ordinals;
            this.ordinals = JSON.parse(ordinalsData);
            this.totalCount = this.ordinals.length;
            
            // Get selected IDs from data attributes
            const selectedIdsData = document.body.dataset.selectedIds;
            const selectedIds = JSON.parse(selectedIdsData);
            if (Array.isArray(selectedIds)) {
                selectedIds.forEach(id => this.selectedIds.add(id));
            }
        } catch (error) {
            console.error('Error loading data:', error);
            this.ordinals = [];
            this.totalCount = 0;
        }
    }
    
    setupEventListeners() {
        // Button event listeners
        this.selectAllBtn.addEventListener('click', () => this.selectAll());
        this.selectNoneBtn.addEventListener('click', () => this.selectNone());
        this.selectRareBtn.addEventListener('click', () => this.selectRare());
        this.saveButton.addEventListener('click', () => this.saveSelection());
        
        // Card click listeners
        document.querySelectorAll('.ordinal-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // Don't trigger if clicking on checkbox directly
                if (!e.target.classList.contains('selection-checkbox')) {
                    const ordinalId = card.dataset.id;
                    this.toggleSelection(ordinalId);
                }
            });
        });
        
        // Checkbox click listeners
        document.querySelectorAll('.selection-checkbox').forEach(checkbox => {
            checkbox.addEventListener('click', (e) => {
                e.stopPropagation(); // Prevent card click
                const card = checkbox.closest('.ordinal-card');
                const ordinalId = card.dataset.id;
                this.toggleSelection(ordinalId);
            });
        });
    }
    
    async loadExistingSelection() {
        try {
            const response = await fetch('/api/ordinals');
            const data = await response.json();
            
            if (data.success && data.selection && data.selection.selected_ids) {
                // Clear current selection
                this.selectedIds.clear();
                
                // Load saved selection
                data.selection.selected_ids.forEach(id => {
                    this.selectedIds.add(id);
                    this.updateCheckbox(id, true);
                });
                
                this.updateCounts();
            }
        } catch (error) {
            console.error('Error loading existing selection:', error);
        }
    }
    
    toggleSelection(ordinalId) {
        if (this.selectedIds.has(ordinalId)) {
            this.selectedIds.delete(ordinalId);
            this.updateCheckbox(ordinalId, false);
        } else {
            this.selectedIds.add(ordinalId);
            this.updateCheckbox(ordinalId, true);
        }
        
        this.updateCounts();
        this.updateSaveButton();
    }
    
    updateCheckbox(ordinalId, selected) {
        const card = document.querySelector(`[data-id="${ordinalId}"]`);
        if (card) {
            const checkbox = card.querySelector('.selection-checkbox');
            
            if (selected) {
                checkbox.classList.add('checked');
                card.classList.add('selected');
            } else {
                checkbox.classList.remove('checked');
                card.classList.remove('selected');
            }
        }
    }
    
    updateCounts() {
        this.selectedCountEl.textContent = this.selectedIds.size;
    }
    
    updateSaveButton() {
        this.saveButton.disabled = this.selectedIds.size === 0;
    }
    
    updateUI() {
        this.updateCounts();
        this.updateSaveButton();
        
        // Update existing selections
        this.selectedIds.forEach(id => {
            this.updateCheckbox(id, true);
        });
    }
    
    selectAll() {
        this.ordinals.forEach(ordinal => {
            this.selectedIds.add(ordinal.id);
            this.updateCheckbox(ordinal.id, true);
        });
        this.updateUI();
    }
    
    selectNone() {
        this.selectedIds.clear();
        this.ordinals.forEach(ordinal => {
            this.updateCheckbox(ordinal.id, false);
        });
        this.updateUI();
    }
    
    selectRare() {
        this.selectNone();
        this.ordinals.forEach(ordinal => {
            if (ordinal.sat_rarity && ordinal.sat_rarity !== 'common') {
                this.selectedIds.add(ordinal.id);
                this.updateCheckbox(ordinal.id, true);
            }
        });
        this.updateUI();
    }
    
    async saveSelection() {
        const selectedArray = Array.from(this.selectedIds);
        
        if (selectedArray.length === 0) {
            this.showResult('Please select at least one Ordinal to display.', 'error');
            return;
        }
        
        this.setSaving(true);
        this.hideResult();
        
        try {
            const response = await fetch('/api/update-selection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    selected_ids: selectedArray
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showResult(`✅ Selection saved! ${selectedArray.length} Ordinals selected for display.`, 'success');
                
                // Redirect to frame after short delay
                setTimeout(() => {
                    window.location.href = '/frame';
                }, 2000);
                
            } else {
                this.showResult(`❌ Error: ${data.message}`, 'error');
            }
            
        } catch (error) {
            console.error('Save error:', error);
            this.showResult('❌ Network error. Please try again.', 'error');
        } finally {
            this.setSaving(false);
        }
    }
    
    setSaving(saving) {
        if (saving) {
            this.saveButtonText.textContent = 'Saving...';
            this.saveButton.disabled = true;
        } else {
            this.saveButtonText.textContent = 'Save Selection';
            this.saveButton.disabled = this.selectedIds.size === 0;
        }
    }
    
    showResult(message, type) {
        this.resultMessage.textContent = message;
        this.resultMessage.className = `result-message result-${type}`;
        this.resultMessage.style.display = 'block';
    }
    
    hideResult() {
        this.resultMessage.style.display = 'none';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.selectionManager = new SelectionManager();
});