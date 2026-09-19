/**
 * ProjectsHub — Modern Platform Interactive Engine
 * Handles Global Search (⌘K / Ctrl+K), Real-time Filter, Hero Terminal tabs, and UI Polish
 */

(function () {
  'use strict';

  // 1. GLOBAL COMMAND SEARCH (⌘K / Ctrl+K)
  var cmdBackdrop = null;
  var cmdInput = null;
  var cmdResults = null;

  var searchableIndex = [
    { title: 'Explore AI Projects Catalog', category: 'Projects', url: '/projects/', icon: '🚀' },
    { title: 'Autonomous Multi-Agent AI Bootcamp', category: 'Workshops', url: '/workshop/', icon: '🎓' },
    { title: 'Interactive AI Tools Directory', category: 'Free Tools', url: '/tools/', icon: '🛠️' },
    { title: 'Custom AI Development for Businesses', category: 'Services', url: '/services/ai-development/', icon: '💼' },
    { title: 'Enterprise AI Workflow Automation', category: 'Services', url: '/services/ai-automation/', icon: '⚡' },
    { title: 'AI System Integration & APIs', category: 'Services', url: '/services/ai-integration/', icon: '🔗' },
    { title: 'Real-World Client Case Studies', category: 'Case Studies', url: '/case-studies/', icon: '📊' },
    { title: 'Computer Vision Deep Learning Projects', category: 'Projects', url: '/projects/?category=vision', icon: '👁️' },
    { title: 'Natural Language Processing & RAG Pipelines', category: 'Projects', url: '/projects/?category=nlp', icon: '📝' },
    { title: 'Final-Year Student Mentorship', category: 'Students', url: '/workshop/', icon: '💡' },
    { title: 'Start a Project / Free Consultation', category: 'Contact', url: '/contact/', icon: '📬' },
    { title: 'Frequently Asked Questions', category: 'Resources', url: '/#faq', icon: '❓' }
  ];

  function initCommandSearch() {
    cmdBackdrop = document.getElementById('globalCmdBackdrop');
    cmdInput = document.getElementById('globalCmdInput');
    cmdResults = document.getElementById('globalCmdResults');

    if (!cmdBackdrop || !cmdInput || !cmdResults) return;

    // Keyboard shortcut: Cmd+K / Ctrl+K
    document.addEventListener('keydown', function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        toggleCommandSearch();
      } else if (e.key === 'Escape' && cmdBackdrop.classList.contains('is-open')) {
        closeCommandSearch();
      }
    });

    // Close on backdrop click
    cmdBackdrop.addEventListener('click', function (e) {
      if (e.target === cmdBackdrop) {
        closeCommandSearch();
      }
    });

    // Search input typing
    cmdInput.addEventListener('input', function () {
      renderCommandResults(this.value.trim());
    });
  }

  function toggleCommandSearch() {
    if (!cmdBackdrop) return;
    if (cmdBackdrop.classList.contains('is-open')) {
      closeCommandSearch();
    } else {
      openCommandSearch();
    }
  }

  function openCommandSearch() {
    if (!cmdBackdrop) return;
    cmdBackdrop.classList.add('is-open');
    if (cmdInput) {
      cmdInput.value = '';
      cmdInput.focus();
    }
    renderCommandResults('');
  }

  function closeCommandSearch() {
    if (!cmdBackdrop) return;
    cmdBackdrop.classList.remove('is-open');
  }

  function renderCommandResults(query) {
    if (!cmdResults) return;
    var q = query.toLowerCase();
    var filtered = searchableIndex.filter(function (item) {
      if (!q) return true;
      return item.title.toLowerCase().indexOf(q) !== -1 || item.category.toLowerCase().indexOf(q) !== -1;
    });

    if (filtered.length === 0) {
      cmdResults.innerHTML = '<div style="padding: 24px; text-align: center; color: #64748b; font-size: 14px;">No matching results found for "' + escapeHtml(query) + '"</div>';
      return;
    }

    var html = '';
    filtered.forEach(function (item) {
      html += `
        <a href="${item.url}" class="p-cmd-item">
          <span style="font-size: 16px;">${item.icon}</span>
          <div style="flex: 1;">
            <div style="font-weight: 600; color: #f8fafc;">${escapeHtml(item.title)}</div>
            <div style="font-size: 11.5px; color: #94a3b8; text-transform: uppercase;">${item.category}</div>
          </div>
          <span style="color: #64748b; font-size: 12px;">↗</span>
        </a>
      `;
    });
    cmdResults.innerHTML = html;
  }

  function escapeHtml(str) {
    return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // 2. HERO TERMINAL TAB SWITCHER (Creem.io CLI & Agent Workflow)
  var terminalTabsData = {
    cli: `
<span style="color:#64748b;"># ── ProjectsHub CLI & MCP Agent Setup ──</span>
<span style="color:#38bdf8;">➜</span> <span style="color:#f8fafc;">Read https://projectshub.co.in/SKILL.md and set up the ProjectsHub CLI</span>
<span style="color:#10b981;">✔ Installed &amp; authenticated</span> <span style="color:#64748b;">[projectshub-agent-runtime v2.4]</span>

<span style="color:#38bdf8;">➜</span> <span style="color:#f8fafc;">Deploy autonomous multi-agent RAG pipeline with PyTorch &amp; FastAPI gateway</span>
<span style="color:#38bdf8;">✔ Architecture initialized.</span> Live inference gateway:
<span style="color:#a855f7;">https://api.projectshub.co.in/v1/predict</span> <span style="color:#10b981;">(14ms latency)</span>
    `,
    workflow: `
<span style="color:#64748b;"># ── ProjectsHub Multi-Agent Pipeline ──</span>
<span style="color:#38bdf8;">from</span> projectshub.agents <span style="color:#38bdf8;">import</span> SupervisorAgent, CodeEvaluator

agent = SupervisorAgent(
    model=<span style="color:#a855f7;">"claude-3-7-sonnet"</span>,
    tools=[<span style="color:#10b981;">"rag_retriever"</span>, <span style="color:#10b981;">"docker_sandbox"</span>, <span style="color:#10b981;">"api_validator"</span>],
    memory=<span style="color:#f59e0b;">"stateful_vector_store"</span>
)

<span style="color:#10b981;">[OK]</span> Agent Pipeline Initialized. Uptime: 99.98%
<span style="color:#38bdf8;">[200 OK]</span> Live Stream connected at wss://api.projectshub.co.in/v1/stream
    `,
    code: `
<span style="color:#64748b;"># ── Production PyTorch Model Inference ──</span>
<span style="color:#38bdf8;">import</span> torch
<span style="color:#38bdf8;">import</span> torchvision.transforms <span style="color:#38bdf8;">as</span> T
<span style="color:#38bdf8;">from</span> fastapi <span style="color:#38bdf8;">import</span> FastAPI

app = FastAPI(title=<span style="color:#a855f7;">"ProjectsHub Inference Gateway"</span>)
device = torch.device(<span style="color:#a855f7;">"cuda"</span> <span style="color:#38bdf8;">if</span> torch.cuda.is_available() <span style="color:#38bdf8;">else</span> <span style="color:#a855f7;">"cpu"</span>)

@app.post(<span style="color:#a855f7;">"/predict"</span>)
<span style="color:#38bdf8;">async def</span> predict(payload: dict):
    tensor = preprocess(payload).to(device)
    output = model(tensor)
    <span style="color:#38bdf8;">return</span> {<span style="color:#a855f7;">"prediction"</span>: output.argmax().item(), <span style="color:#a855f7;">"latency_ms"</span>: 4.8}
    `,
    metrics: `
<span style="color:#64748b;"># ── Production Performance Telemetry ──</span>
{
  <span style="color:#38bdf8;">"production_projects"</span>: <span style="color:#10b981;">50</span>,
  <span style="color:#38bdf8;">"free_developer_tools"</span>: <span style="color:#10b981;">12</span>,
  <span style="color:#38bdf8;">"mentored_engineers"</span>: <span style="color:#10b981;">1250</span>,
  <span style="color:#38bdf8;">"avg_response_latency"</span>: <span style="color:#a855f7;">"14.2ms"</span>,
  <span style="color:#38bdf8;">"verified_accuracy"</span>: <span style="color:#10b981;">"99.4%"</span>,
  <span style="color:#38bdf8;">"lighthouse_score"</span>: <span style="color:#10b981;">98</span>
}
    `
  };

  function initTerminalTabs() {
    var tabs = document.querySelectorAll('.p-terminal-tab');
    var body = document.getElementById('heroTerminalBody');
    if (!tabs.length || !body) return;

    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        tabs.forEach(function (t) { t.classList.remove('active'); });
        tab.classList.add('active');
        var key = tab.dataset.tab;
        if (terminalTabsData[key]) {
          body.innerHTML = terminalTabsData[key].trim();
        }
      });
    });
  }

  // 3. CLIENT-SIDE PROJECT CATEGORY FILTERING
  function initProjectFiltering() {
    var filterBtns = document.querySelectorAll('.p-filter-pill');
    var cards = document.querySelectorAll('.p-project-card-wrap');
    if (!filterBtns.length || !cards.length) return;

    filterBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        filterBtns.forEach(function (b) { b.classList.remove('active'); });
        btn.classList.add('active');

        var cat = (btn.dataset.category || 'all').toLowerCase();

        cards.forEach(function (card) {
          var cardCats = (card.dataset.category || '').toLowerCase();
          if (cat === 'all' || cardCats.indexOf(cat) !== -1) {
            card.style.display = '';
            card.style.animation = 'fadeIn 0.25s ease-in-out';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }

  // 4. STICKY NAVBAR SCROLL SENSING
  function initNavbarScroll() {
    var navbar = document.getElementById('navbar') || document.querySelector('.p-navbar');
    if (!navbar) return;

    var handleScroll = function () {
      if (window.scrollY > 20) {
        navbar.classList.add('is-scrolled');
      } else {
        navbar.classList.remove('is-scrolled');
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
  }

  // 5. ACCESSIBLE ACCORDIONS
  function initAccordions() {
    document.querySelectorAll('.p-accordion-trigger').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var item = btn.closest('.p-accordion-item');
        if (!item) return;
        var isOpen = item.classList.toggle('active');
        btn.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
      });
    });
  }

  // INITIALIZE ON DOM READY
  document.addEventListener('DOMContentLoaded', function () {
    initCommandSearch();
    initTerminalTabs();
    initProjectFiltering();
    initNavbarScroll();
    initAccordions();
  });

  // Expose global controller
  window.ProjectsHubPlatform = {
    openSearch: openCommandSearch,
    closeSearch: closeCommandSearch,
    toggleSearch: toggleCommandSearch
  };
})();
