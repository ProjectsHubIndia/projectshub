/**
 * Menu Management Admin JavaScript
 *
 * Drag-and-drop reordering, nesting depth indicators, and the preview style
 * switcher for the Menu / MenuConfig admin screens.
 *
 * DOM contract (Django stacked inline):
 *   .menu-item-inline            the <fieldset> wrapping every row
 *   .inline-related              one row; the last is .empty-form, the blank
 *                                "add another" template
 *   input[name$="-id"]           a saved row's primary key
 *   select[name$="-parent"]      the chosen parent's primary key
 */

(function () {
    'use strict';

    // Rows live inside the fieldset. Treating '.menu-item-inline' as a row
    // makes the whole group a drop target, which moves rows out of the
    // formset, so scope queries to real rows and skip the blank template.
    var ROW_SELECTOR = '.menu-item-inline .inline-related:not(.empty-form)';

    var draggedElement = null;
    var observer = null;

    function rows() {
        return Array.prototype.slice.call(document.querySelectorAll(ROW_SELECTOR));
    }

    function fieldValue(row, suffix) {
        var el = row.querySelector('[name$="' + suffix + '"]');
        return el ? el.value : '';
    }

    /* --- Drag and drop ---------------------------------------------------- */

    function initMenuItemSorting() {
        rows().forEach(function (row) {
            if (row.querySelector('.drag-handle')) {
                return;
            }
            var header = row.querySelector('h3');
            if (!header) {
                return;
            }

            var handle = document.createElement('span');
            handle.className = 'drag-handle';
            handle.textContent = '☰';
            handle.draggable = true;
            handle.title = 'Drag to reorder';
            header.insertBefore(handle, header.firstChild);

            handle.addEventListener('dragstart', handleDragStart);
            row.addEventListener('dragover', handleDragOver);
            row.addEventListener('dragleave', handleDragLeave);
            row.addEventListener('drop', handleDrop);
            row.addEventListener('dragend', handleDragEnd);
        });
    }

    function handleDragStart(e) {
        draggedElement = this.closest('.inline-related');
        e.dataTransfer.effectAllowed = 'move';
        // Some browsers abort the drag unless data is set; the payload is unused.
        e.dataTransfer.setData('text/plain', draggedElement.id || 'menu-item');
        draggedElement.classList.add('dragging');
    }

    function handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        var target = this.closest('.inline-related');
        if (target && target !== draggedElement) {
            target.classList.add('drag-over');
        }
    }

    function handleDragLeave() {
        // Without this the highlight stays on every row the cursor crossed.
        var target = this.closest('.inline-related');
        if (target) {
            target.classList.remove('drag-over');
        }
    }

    function handleDrop(e) {
        // The default drop action navigates away, discarding unsaved edits.
        e.preventDefault();
        e.stopPropagation();
        clearDragClasses();

        var target = this.closest('.inline-related');
        if (target && draggedElement && target !== draggedElement) {
            target.parentNode.insertBefore(draggedElement, target);
            updateOrderFields();
        }
        return false;
    }

    function handleDragEnd() {
        clearDragClasses();
        draggedElement = null;
    }

    function clearDragClasses() {
        document.querySelectorAll('.dragging, .drag-over').forEach(function (el) {
            el.classList.remove('dragging', 'drag-over');
        });
    }

    /**
     * Renumber order fields to match DOM order.
     *
     * Only real rows are numbered; writing into the .empty-form template makes
     * Django treat the blank row as filled in and try to validate it.
     */
    function updateOrderFields() {
        rows().forEach(function (row, index) {
            var orderField = row.querySelector('[name$="-order"]');
            if (orderField) {
                orderField.value = index;
            }
        });
    }

    /* --- Nesting depth ---------------------------------------------------- */

    /**
     * Map each saved row's pk to its selected parent's pk.
     *
     * The old code looked for select[name*="-parent"][id*="<pk>"], but inline
     * ids carry the form index (id_items-0-parent), never the pk, so that
     * lookup matched the wrong row or nothing at all.
     */
    function buildParentMap() {
        var parentOf = {};
        rows().forEach(function (row) {
            var pk = fieldValue(row, '-id');
            if (pk) {
                parentOf[pk] = fieldValue(row, '-parent');
            }
        });
        return parentOf;
    }

    function depthOf(pk, parentOf) {
        var depth = 0;
        var seen = {};
        var current = parentOf[pk];
        // Guard against a parent cycle in existing data.
        while (current && !seen[current] && depth < 10) {
            seen[current] = true;
            depth += 1;
            current = parentOf[current];
        }
        return depth;
    }

    function applyDepths() {
        var parentOf = buildParentMap();
        rows().forEach(function (row) {
            var pk = fieldValue(row, '-id');
            var depth;
            if (pk) {
                depth = depthOf(pk, parentOf);
            } else {
                // Unsaved row: depth follows the parent it points at, if any.
                var parentPk = fieldValue(row, '-parent');
                depth = parentPk ? depthOf(parentPk, parentOf) + 1 : 0;
            }
            row.dataset.depth = depth;
            row.dataset.depthLabel = depth ? '└' : '';
        });
    }

    function watchParentSelects() {
        var selects = document.querySelectorAll(
            '.menu-item-inline select[name$="-parent"]'
        );
        selects.forEach(function (select) {
            if (select.dataset.depthWatched) {
                return;
            }
            select.dataset.depthWatched = '1';
            select.addEventListener('change', applyDepths);
        });
    }

    /* --- Preview style switcher ------------------------------------------- */

    function previewStyleSwitch(style) {
        var container = document.querySelector('.menu-preview-container');
        if (!container) {
            return;
        }
        container.dataset.style = style;
        document.querySelectorAll('.style-switch-btn').forEach(function (btn) {
            btn.classList.toggle('active', btn.dataset.style === style);
        });
    }

    /**
     * Tag the preview buttons with the style each one selects.
     *
     * Matching on button text broke as soon as a label changed, so read the
     * style from the onclick target and mark the current one active on load.
     */
    function initStyleSwitcher() {
        var container = document.querySelector('.menu-preview-container');
        if (!container) {
            return;
        }
        document.querySelectorAll('.style-switch-btn').forEach(function (btn) {
            if (!btn.dataset.style) {
                var match = /previewStyleSwitch\(.([^'"]+)./.exec(
                    btn.getAttribute('onclick') || ''
                );
                if (match) {
                    btn.dataset.style = match[1];
                }
            }
            btn.classList.toggle(
                'active',
                btn.dataset.style === container.dataset.style
            );
        });
    }

    /* --- Collapsible inline group ----------------------------------------- */

    function initCollapsibleInlines() {
        document.querySelectorAll('.inline-group').forEach(function (group) {
            var header = group.querySelector('h2, h3');
            if (!header || header.querySelector('.collapse-toggle')) {
                return;
            }

            var toggle = document.createElement('button');
            toggle.type = 'button';
            toggle.className = 'collapse-toggle';
            toggle.textContent = '▼';
            toggle.title = 'Show or hide these items';

            toggle.addEventListener('click', function () {
                // querySelector returns only the first row, so the original
                // toggle hid one item and left the rest visible.
                var items = group.querySelectorAll('.inline-related');
                var collapsed = group.dataset.collapsed === '1';
                items.forEach(function (item) {
                    item.style.display = collapsed ? '' : 'none';
                });
                group.dataset.collapsed = collapsed ? '0' : '1';
                this.textContent = collapsed ? '▼' : '▶';
            });

            header.appendChild(toggle);
        });
    }

    /* --- Init ------------------------------------------------------------- */

    function refresh() {
        initMenuItemSorting();
        watchParentSelects();
        applyDepths();
    }

    function init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        // Slug prepopulation is Django's job (MenuAdmin.prepopulated_fields).
        // A second handler here fought it and overwrote manual slug edits.
        refresh();
        initStyleSwitcher();
        initCollapsibleInlines();

        var container = document.querySelector('.menu-item-inline');
        if (!container) {
            return;
        }

        // refresh() inserts handles into the observed subtree, which would
        // re-trigger the observer; disconnect while mutating.
        observer = new MutationObserver(function (mutations) {
            var added = mutations.some(function (m) {
                return m.addedNodes.length > 0;
            });
            if (!added) {
                return;
            }
            observer.disconnect();
            refresh();
            observer.observe(container, { childList: true, subtree: true });
        });
        observer.observe(container, { childList: true, subtree: true });
    }

    window.previewStyleSwitch = previewStyleSwitch;

    init();
})();
