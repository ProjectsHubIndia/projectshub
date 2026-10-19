/**
 * Menu Management Admin JavaScript
 * Handles drag-and-drop sorting, depth indicators, and style switching
 */

(function() {
    'use strict';

    /**
     * Initialize drag-and-drop sorting for menu items
     */
    function initMenuItemSorting() {
        const inlineRows = document.querySelectorAll('.menu-item-inline, .inline-related');
        
        inlineRows.forEach(row => {
            // Add drag handle if not already present
            if (!row.querySelector('.drag-handle')) {
                const dragHandle = document.createElement('span');
                dragHandle.className = 'drag-handle';
                dragHandle.textContent = '☰';
                dragHandle.draggable = true;
                dragHandle.title = 'Drag to reorder';
                
                const firstChild = row.querySelector('h3, .inline-group');
                if (firstChild) {
                    firstChild.insertBefore(dragHandle, firstChild.firstChild);
                }
                
                // Attach event listeners
                dragHandle.addEventListener('dragstart', handleDragStart);
                row.addEventListener('dragover', handleDragOver);
                row.addEventListener('drop', handleDrop);
                row.addEventListener('dragend', handleDragEnd);
            }
        });
    }

    let draggedElement = null;

    function handleDragStart(e) {
        draggedElement = this.closest('.menu-item-inline, .inline-related');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', draggedElement.innerHTML);
        draggedElement.classList.add('dragging');
    }

    function handleDragOver(e) {
        if (e.preventDefault) {
            e.preventDefault();
        }
        e.dataTransfer.dropEffect = 'move';
        
        const targetRow = this.closest('.menu-item-inline, .inline-related');
        if (targetRow && targetRow !== draggedElement) {
            targetRow.classList.add('drag-over');
        }
        return false;
    }

    function handleDrop(e) {
        if (e.stopPropagation) {
            e.stopPropagation();
        }
        
        const targetRow = this.closest('.menu-item-inline, .inline-related');
        
        // Remove drag-over class from all rows
        document.querySelectorAll('.drag-over').forEach(el => {
            el.classList.remove('drag-over');
        });
        
        if (targetRow && draggedElement && targetRow !== draggedElement) {
            // Insert dragged element before target
            targetRow.parentNode.insertBefore(draggedElement, targetRow);
            
            // Update order fields
            updateOrderFields();
        }
        
        return false;
    }

    function handleDragEnd(e) {
        document.querySelectorAll('.dragging').forEach(el => {
            el.classList.remove('dragging');
        });
        document.querySelectorAll('.drag-over').forEach(el => {
            el.classList.remove('drag-over');
        });
    }

    /**
     * Update order fields after drag-and-drop
     */
    function updateOrderFields() {
        const rows = document.querySelectorAll('.menu-item-inline, .inline-related');
        rows.forEach((row, index) => {
            const orderField = row.querySelector('input[name*="-order"]');
            if (orderField) {
                orderField.value = index;
            }
        });
    }

    /**
     * Toggle nested item visibility
     */
    function toggleNestedItems(parentId) {
        const children = document.querySelectorAll(`[data-parent="${parentId}"]`);
        children.forEach(child => {
            child.style.display = child.style.display === 'none' ? 'block' : 'none';
        });
    }

    /**
     * Update depth indicators based on parent selection
     */
    function updateDepthIndicators() {
        const parentSelects = document.querySelectorAll('select[name*="-parent"]');
        
        parentSelects.forEach(select => {
            select.addEventListener('change', function() {
                const row = this.closest('.menu-item-inline, .inline-related');
                if (!row) return;
                
                const parentId = this.value;
                let depth = 0;
                
                if (parentId) {
                    // Find parent row and calculate depth
                    const allRows = Array.from(document.querySelectorAll('.menu-item-inline, .inline-related'));
                    const parentRow = allRows.find(r => {
                        const pkField = r.querySelector('input[name*="-id"]');
                        return pkField && pkField.value === parentId;
                    });
                    
                    if (parentRow) {
                        const parentDepth = parseInt(parentRow.dataset.depth || 0);
                        depth = parentDepth + 1;
                    }
                }
                
                row.dataset.depth = depth;
                row.style.paddingLeft = `${depth * 24}px`;
                
                // Update depth label
                const depthLabel = '→ '.repeat(depth);
                row.dataset.depthLabel = depthLabel;
            });
        });
    }

    /**
     * Preview style switcher
     */
    function previewStyleSwitch(style) {
        const container = document.querySelector('.menu-preview-container');
        if (container) {
            container.dataset.style = style;
            
            // Update active button state
            document.querySelectorAll('.toolbar-actions .button').forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.toLowerCase().includes(style.replace('_', ' '))) {
                    btn.classList.add('active');
                }
            });
        }
    }

    /**
     * Auto-populate slug from menu name
     */
    function autoPopulateSlug() {
        const nameField = document.querySelector('input[name="name"]');
        const slugField = document.querySelector('input[name="slug"]');
        
        if (nameField && slugField && !slugField.value) {
            nameField.addEventListener('input', function() {
                const slug = this.value
                    .toLowerCase()
                    .replace(/[^a-z0-9]+/g, '-')
                    .replace(/^-|-$/g, '');
                slugField.value = slug;
            });
        }
    }

    /**
     * Add style switcher buttons to preview page
     */
    function initStyleSwitcher() {
        const toolbar = document.querySelector('.toolbar-actions');
        if (toolbar && document.querySelector('.menu-preview-container')) {
            // Check if buttons already exist
            if (!toolbar.querySelector('.style-switch-btn')) {
                const standardBtn = document.createElement('button');
                standardBtn.type = 'button';
                standardBtn.className = 'button style-switch-btn';
                standardBtn.textContent = 'Preview: Standard';
                standardBtn.onclick = () => previewStyleSwitch('standard');
                
                const pillBtn = document.createElement('button');
                pillBtn.type = 'button';
                pillBtn.className = 'button style-switch-btn';
                pillBtn.textContent = 'Preview: Floating Pill';
                pillBtn.onclick = () => previewStyleSwitch('floating_pill');
                
                // Insert before other buttons
                const firstBtn = toolbar.firstElementChild;
                toolbar.insertBefore(pillBtn, firstBtn);
                toolbar.insertBefore(standardBtn, pillBtn);
            }
        }
    }

    /**
     * Initialize collapsible inline groups
     */
    function initCollapsibleInlines() {
        const inlineGroups = document.querySelectorAll('.inline-group');
        
        inlineGroups.forEach(group => {
            const header = group.querySelector('h3');
            if (header && !header.querySelector('.collapse-toggle')) {
                const toggle = document.createElement('button');
                toggle.type = 'button';
                toggle.className = 'collapse-toggle';
                toggle.textContent = '▼';
                toggle.style.cssText = 'margin-left: 8px; background: none; border: none; cursor: pointer; font-size: 12px;';
                
                toggle.addEventListener('click', function() {
                    const inlines = group.querySelector('.inline-related');
                    if (inlines) {
                        const isHidden = inlines.style.display === 'none';
                        inlines.style.display = isHidden ? 'block' : 'none';
                        this.textContent = isHidden ? '▼' : '▶';
                    }
                });
                
                header.appendChild(toggle);
            }
        });
    }

    /**
     * Calculate and display depth for existing items
     */
    function calculateInitialDepth() {
        const parentSelects = document.querySelectorAll('select[name*="-parent"]');
        
        parentSelects.forEach(select => {
            const row = select.closest('.menu-item-inline, .inline-related');
            if (!row) return;
            
            const parentId = select.value;
            let depth = 0;
            
            if (parentId) {
                // Calculate depth by counting ancestors
                let currentParentId = parentId;
                while (currentParentId && depth < 10) { // Max depth safety
                    depth++;
                    const parentSelect = document.querySelector(`select[name*="-parent"][id*="${currentParentId}"]`);
                    currentParentId = parentSelect ? parentSelect.value : null;
                }
            }
            
            row.dataset.depth = depth;
            row.style.paddingLeft = `${depth * 24}px`;
        });
    }

    /**
     * Initialize all menu admin functionality
     */
    function init() {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // Initialize features
        autoPopulateSlug();
        initMenuItemSorting();
        updateDepthIndicators();
        initStyleSwitcher();
        initCollapsibleInlines();
        calculateInitialDepth();

        // Re-initialize when new inline forms are added
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length) {
                    initMenuItemSorting();
                    updateDepthIndicators();
                    calculateInitialDepth();
                }
            });
        });

        const inlineContainer = document.querySelector('.inline-group');
        if (inlineContainer) {
            observer.observe(inlineContainer, {
                childList: true,
                subtree: true
            });
        }
    }

    // Expose functions globally for inline onclick handlers
    window.previewStyleSwitch = previewStyleSwitch;
    window.toggleNestedItems = toggleNestedItems;

    // Auto-initialize
    init();

})();
