/**
 * WordPress Admin Interactive Engine for ProjectsHub
 * Manages Screen Options, Contextual Help, Sidebar Folding,
 * and WP_List_Table row interactions.
 */

(function() {
  // 1. Sidebar Fold / Collapse Persistence
  var collapseBtn = document.getElementById('collapse-menu');
  var wpwrap = document.getElementById('wpwrap');
  var isFolded = localStorage.getItem('wp-admin-folded') === 'true';

  if (isFolded && wpwrap) {
    wpwrap.classList.add('folded');
    if (collapseBtn) collapseBtn.querySelector('.collapse-icon').textContent = '▶';
  }

  if (collapseBtn && wpwrap) {
    collapseBtn.addEventListener('click', function() {
      var folded = wpwrap.classList.toggle('folded');
      collapseBtn.querySelector('.collapse-icon').textContent = folded ? '▶' : '◀';
      localStorage.setItem('wp-admin-folded', folded ? 'true' : 'false');
    });
  }

  // 2. Screen Options Slide-Down Drawer
  window.toggleScreenOptions = function() {
    var meta = document.getElementById('screen-meta');
    var wrap = document.getElementById('screen-options-wrap');
    var helpWrap = document.getElementById('contextual-help-wrap');
    var link = document.getElementById('screen-options-link');

    if (!meta || !wrap) return;

    if (wrap.style.display === 'block') {
      wrap.style.display = 'none';
      meta.style.display = 'none';
      if (link) link.classList.remove('active');
    } else {
      if (helpWrap) helpWrap.style.display = 'none';
      meta.style.display = 'block';
      wrap.style.display = 'block';
      if (link) link.classList.add('active');
      var helpLink = document.getElementById('contextual-help-link');
      if (helpLink) helpLink.classList.remove('active');
    }
  };

  // 3. Help Tab Slide-Down Drawer
  window.toggleHelpTab = function() {
    var meta = document.getElementById('screen-meta');
    var wrap = document.getElementById('screen-options-wrap');
    var helpWrap = document.getElementById('contextual-help-wrap');
    var link = document.getElementById('contextual-help-link');

    if (!meta || !helpWrap) return;

    if (helpWrap.style.display === 'block') {
      helpWrap.style.display = 'none';
      meta.style.display = 'none';
      if (link) link.classList.remove('active');
    } else {
      if (wrap) wrap.style.display = 'none';
      meta.style.display = 'block';
      helpWrap.style.display = 'block';
      if (link) link.classList.add('active');
      var optLink = document.getElementById('screen-options-link');
      if (optLink) optLink.classList.remove('active');
    }
  };

  // 4. Help Tab Switcher
  window.switchHelpTab = function(tabId, linkEl) {
    var panes = ['overview', 'screen-content', 'quick-actions'];
    panes.forEach(function(id) {
      var pane = document.getElementById('help-pane-' + id);
      if (pane) pane.style.display = (id === tabId) ? 'block' : 'none';
    });

    var ul = linkEl.closest('ul');
    if (ul) {
      ul.querySelectorAll('a').forEach(function(a) {
        a.style.fontWeight = 'normal';
        a.style.color = '#646970';
      });
      linkEl.style.fontWeight = '700';
      linkEl.style.color = '#2271b1';
    }
  };

  // 5. Dismissible Notices
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.notice.is-dismissible').forEach(function(notice) {
      if (!notice.querySelector('.notice-dismiss')) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'notice-dismiss';
        btn.innerHTML = '✕';
        btn.style.cssText = 'background:none;border:none;color:#787c82;cursor:pointer;margin-left:auto;font-size:12px;padding:4px 8px;';
        btn.onclick = function() { notice.remove(); };
        notice.appendChild(btn);
      }
    });
  });
})();
