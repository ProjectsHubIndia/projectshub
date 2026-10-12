/**
 * WordPress ACF (Advanced Custom Fields) Flexible Content Blocks Engine
 * Provides authentic block creation, inline editing, field serialization,
 * reordering, visibility toggles, and modal picker for ProjectsHub Pages.
 */

(function() {
  'use strict';

  // 1. ACF BLOCK DEFINITIONS
  var ACF_BLOCK_DEFINITIONS = {
    'acf/hero-section': {
      name: 'Hero Section',
      icon: '⚡',
      category: 'headers',
      desc: 'Large prominent hero banner with badge, headline, subtitle, and dual CTA buttons.',
      defaultData: {
        badge: '⚡ Next-Gen AI Engineering',
        headline: 'Real-World AI Projects & Production Systems',
        subheadline: 'Production-ready machine learning solutions, automated workflows, and comprehensive student mentorship.',
        primary_cta_text: 'Explore Projects →',
        primary_cta_url: '/projects/',
        secondary_cta_text: '3-Day AI Bootcamp',
        secondary_cta_url: '/workshop/',
        style: 'glow-dark'
      },
      render: function(b, idx) {
        var d = b.data || {};
        return `
          <div class="acf-fields-grid">
            <div class="acf-field-row">
              <label class="acf-field-label">Pill Badge Text</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.badge || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'badge', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Background Style</label>
              <select class="acf-input" onchange="window.AcfBuilder.updateField(${idx}, 'style', this.value)">
                <option value="glow-dark" ${d.style === 'glow-dark' ? 'selected' : ''}>Cyber Glow Dark (Recommended)</option>
                <option value="violet-glow" ${d.style === 'violet-glow' ? 'selected' : ''}>Violet Nebula Glow</option>
                <option value="amber-glow" ${d.style === 'amber-glow' ? 'selected' : ''}>Warm Amber Glow</option>
                <option value="clean-dark" ${d.style === 'clean-dark' ? 'selected' : ''}>Clean Minimal Dark</option>
              </select>
            </div>
            <div class="acf-field-row full-width">
              <label class="acf-field-label">Main Headline</label>
              <input type="text" class="acf-input" style="font-weight:700;" value="${escapeHtml(d.headline || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'headline', this.value)">
            </div>
            <div class="acf-field-row full-width">
              <label class="acf-field-label">Subheadline / Paragraph</label>
              <textarea class="acf-input" rows="2" oninput="window.AcfBuilder.updateField(${idx}, 'subheadline', this.value)">${escapeHtml(d.subheadline || '')}</textarea>
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Primary Button Text</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.primary_cta_text || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'primary_cta_text', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Primary Button Destination URL</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.primary_cta_url || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'primary_cta_url', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Secondary Button Text</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.secondary_cta_text || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'secondary_cta_text', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Secondary Button Destination URL</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.secondary_cta_url || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'secondary_cta_url', this.value)">
            </div>
          </div>
        `;
      }
    },

    'acf/projects-grid': {
      name: 'Featured Projects Grid',
      icon: '🚀',
      category: 'content',
      desc: 'Dynamic grid of real-world AI projects with filter tags, live demo links, and tech badges.',
      defaultData: {
        section_title: 'Featured AI Projects & Case Studies',
        subtitle: 'Production-grade codebases, models, and interactive web demos.',
        category_filter: 'all',
        max_items: 6,
        layout: 'grid-3-col',
        show_badges: true
      },
      render: function(b, idx) {
        var d = b.data || {};
        return `
          <div class="acf-fields-grid">
            <div class="acf-field-row full-width">
              <label class="acf-field-label">Section Title</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.section_title || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'section_title', this.value)">
            </div>
            <div class="acf-field-row full-width">
              <label class="acf-field-label">Subtitle</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.subtitle || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'subtitle', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Category Filter</label>
              <select class="acf-input" onchange="window.AcfBuilder.updateField(${idx}, 'category_filter', this.value)">
                <option value="all" ${d.category_filter === 'all' ? 'selected' : ''}>All Categories</option>
                <option value="agents" ${d.category_filter === 'agents' ? 'selected' : ''}>Autonomous AI Agents</option>
                <option value="vision" ${d.category_filter === 'vision' ? 'selected' : ''}>Computer Vision &amp; Deep Learning</option>
                <option value="nlp" ${d.category_filter === 'nlp' ? 'selected' : ''}>NLP &amp; LLM Orchestration</option>
              </select>
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Max Projects to Display</label>
              <input type="number" class="acf-input" min="1" max="24" value="${escapeHtml(d.max_items || 6)}" oninput="window.AcfBuilder.updateField(${idx}, 'max_items', parseInt(this.value)||6)">
            </div>
          </div>
        `;
      }
    },

    'acf/services-grid': {
      name: 'Services & Solutions',
      icon: '💼',
      category: 'content',
      desc: 'Grid of tailored service offerings, engineering capabilities, and AI workflows.',
      defaultData: {
        section_title: 'Enterprise AI Engineering & Automation',
        subtitle: 'End-to-end intelligence pipelines built for modern software teams.',
        columns: '3',
        style: 'gradient-border'
      },
      render: function(b, idx) {
        var d = b.data || {};
        return `
          <div class="acf-fields-grid">
            <div class="acf-field-row">
              <label class="acf-field-label">Section Title</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.section_title || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'section_title', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Subtitle</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.subtitle || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'subtitle', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Layout Columns</label>
              <select class="acf-input" onchange="window.AcfBuilder.updateField(${idx}, 'columns', this.value)">
                <option value="2" ${d.columns === '2' ? 'selected' : ''}>2 Columns (Wide)</option>
                <option value="3" ${d.columns === '3' ? 'selected' : ''}>3 Columns (Standard)</option>
                <option value="4" ${d.columns === '4' ? 'selected' : ''}>4 Columns (Compact)</option>
              </select>
            </div>
          </div>
        `;
      }
    },

    'acf/tools-directory': {
      name: 'AI Tools Showcase',
      icon: '🛠️',
      category: 'content',
      desc: 'Interactive web tools directory with instant live search and browser utilities.',
      defaultData: {
        section_title: 'Interactive AI Utilities & Developer Tools',
        subtitle: 'Browser-based utilities designed to supercharge your workflow.',
        enable_search: true,
        max_items: 6
      },
      render: function(b, idx) {
        var d = b.data || {};
        return `
          <div class="acf-fields-grid">
            <div class="acf-field-row">
              <label class="acf-field-label">Section Title</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.section_title || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'section_title', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Subtitle</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.subtitle || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'subtitle', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label" style="display:flex;align-items:center;gap:6px;margin-top:14px;cursor:pointer;">
                <input type="checkbox" ${d.enable_search ? 'checked' : ''} onchange="window.AcfBuilder.updateField(${idx}, 'enable_search', this.checked)">
                <span>Enable Real-Time Search Bar</span>
              </label>
            </div>
          </div>
        `;
      }
    },

    'acf/workshop-teaser': {
      name: 'Bootcamp / Workshop Teaser',
      icon: '🎓',
      category: 'content',
      desc: 'Spotlight banner for the intensive 3-Day Autonomous Multi-Agent AI Bootcamp.',
      defaultData: {
        section_title: '3-Day Hands-on Autonomous Agents Bootcamp',
        subtitle: 'Learn to architect, evaluate, and deploy multi-agent LLM systems from scratch.',
        cta_text: 'View Curriculum & Claim Spot',
        cta_url: '/workshop/'
      },
      render: function(b, idx) {
        var d = b.data || {};
        return `
          <div class="acf-fields-grid">
            <div class="acf-field-row full-width">
              <label class="acf-field-label">Heading</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.section_title || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'section_title', this.value)">
            </div>
            <div class="acf-field-row full-width">
              <label class="acf-field-label">Subtitle</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.subtitle || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'subtitle', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">CTA Button Text</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.cta_text || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'cta_text', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">CTA Link URL</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.cta_url || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'cta_url', this.value)">
            </div>
          </div>
        `;
      }
    },

    'acf/stats-counter': {
      name: 'Live Statistics & KPIs',
      icon: '📊',
      category: 'proof',
      desc: '4-card metric counter bar displaying projects deployed, engineers mentored, and system uptime.',
      defaultData: {
        items: [
          { number: '25+', label: 'Production AI Projects', accent: '#38bdf8' },
          { number: '1,200+', label: 'Engineers Mentored', accent: '#818cf8' },
          { number: '99.4%', label: 'System Accuracy', accent: '#34d399' },
          { number: '24/7', label: 'Community Support', accent: '#fbbf24' }
        ]
      },
      render: function(b, idx) {
        var items = (b.data && b.data.items) || [];
        var rowsHtml = '';
        for (var i = 0; i < 4; i++) {
          var it = items[i] || { number: '', label: '', accent: '#38bdf8' };
          rowsHtml += `
            <div style="display:flex;gap:8px;margin-bottom:8px;align-items:center;">
              <span style="font-weight:700;color:#646970;font-size:11px;width:20px;">#${i+1}</span>
              <input type="text" placeholder="Value (e.g. 25+)" class="acf-input" style="width:130px;" value="${escapeHtml(it.number || '')}" oninput="window.AcfBuilder.updateStatItem(${idx}, ${i}, 'number', this.value)">
              <input type="text" placeholder="Label (e.g. AI Projects)" class="acf-input" style="flex:1;" value="${escapeHtml(it.label || '')}" oninput="window.AcfBuilder.updateStatItem(${idx}, ${i}, 'label', this.value)">
              <input type="color" class="acf-input" style="width:38px;padding:2px;" value="${it.accent || '#38bdf8'}" onchange="window.AcfBuilder.updateStatItem(${idx}, ${i}, 'accent', this.value)">
            </div>
          `;
        }
        return `
          <div class="acf-field-row full-width">
            <label class="acf-field-label">Metric Counter Items (4 Cards)</label>
            ${rowsHtml}
          </div>
        `;
      }
    },

    'acf/testimonials': {
      name: 'Client Testimonials Carousel',
      icon: '💬',
      category: 'proof',
      desc: 'Customer proof quotes, reviewer avatars, company roles, and rating stars.',
      defaultData: {
        section_title: 'Trusted by Developers & Industry Innovators',
        subtitle: 'Real feedback from engineers building real-world AI applications.',
        rating: '5.0',
        layout: 'carousel'
      },
      render: function(b, idx) {
        var d = b.data || {};
        return `
          <div class="acf-fields-grid">
            <div class="acf-field-row">
              <label class="acf-field-label">Section Title</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.section_title || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'section_title', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Subtitle</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.subtitle || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'subtitle', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Display Style</label>
              <select class="acf-input" onchange="window.AcfBuilder.updateField(${idx}, 'layout', this.value)">
                <option value="carousel" ${d.layout === 'carousel' ? 'selected' : ''}>Slider Carousel</option>
                <option value="grid" ${d.layout === 'grid' ? 'selected' : ''}>Static 3-Column Grid</option>
              </select>
            </div>
          </div>
        `;
      }
    },

    'acf/faq-accordion': {
      name: 'FAQ Accordion',
      icon: '❓',
      category: 'proof',
      desc: 'Expandable question & answer accordions with category filtering.',
      defaultData: {
        section_title: 'Frequently Asked Questions',
        category: 'general',
        show_search: false
      },
      render: function(b, idx) {
        var d = b.data || {};
        return `
          <div class="acf-fields-grid">
            <div class="acf-field-row">
              <label class="acf-field-label">Section Title</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.section_title || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'section_title', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Target FAQ Category</label>
              <select class="acf-input" onchange="window.AcfBuilder.updateField(${idx}, 'category', this.value)">
                <option value="general" ${d.category === 'general' ? 'selected' : ''}>General / All</option>
                <option value="projects" ${d.category === 'projects' ? 'selected' : ''}>Projects &amp; Code</option>
                <option value="workshops" ${d.category === 'workshops' ? 'selected' : ''}>Bootcamps &amp; Workshops</option>
                <option value="services" ${d.category === 'services' ? 'selected' : ''}>Custom Services &amp; Enterprise</option>
              </select>
            </div>
          </div>
        `;
      }
    },

    'acf/cta-banner': {
      name: 'Call To Action Banner',
      icon: '📢',
      category: 'cta',
      desc: 'High-conversion bottom banner with radiant background glow and action button.',
      defaultData: {
        headline: 'Ready to Engineer Next-Generation AI?',
        description: 'Access production-grade code, interactive tools, and direct guidance from veteran machine learning engineers.',
        button_text: 'Explore All Projects Now →',
        button_url: '/projects/',
        style: 'cyan-glow'
      },
      render: function(b, idx) {
        var d = b.data || {};
        return `
          <div class="acf-fields-grid">
            <div class="acf-field-row full-width">
              <label class="acf-field-label">Banner Headline</label>
              <input type="text" class="acf-input" style="font-weight:700;" value="${escapeHtml(d.headline || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'headline', this.value)">
            </div>
            <div class="acf-field-row full-width">
              <label class="acf-field-label">Supporting Description</label>
              <textarea class="acf-input" rows="2" oninput="window.AcfBuilder.updateField(${idx}, 'description', this.value)">${escapeHtml(d.description || '')}</textarea>
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Action Button Text</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.button_text || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'button_text', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Action Button URL</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.button_url || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'button_url', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Accent Theme</label>
              <select class="acf-input" onchange="window.AcfBuilder.updateField(${idx}, 'style', this.value)">
                <option value="cyan-glow" ${d.style === 'cyan-glow' ? 'selected' : ''}>Cyan &amp; Blue Glow</option>
                <option value="purple-glow" ${d.style === 'purple-glow' ? 'selected' : ''}>Purple &amp; Violet Glow</option>
                <option value="emerald-glow" ${d.style === 'emerald-glow' ? 'selected' : ''}>Emerald Green Glow</option>
              </select>
            </div>
          </div>
        `;
      }
    },

    'acf/rich-text': {
      name: 'Rich Text / Gutenberg Content',
      icon: '📝',
      category: 'content',
      desc: 'Freeform HTML body content, formatted text paragraphs, images, and lists.',
      defaultData: {
        heading: '',
        html_content: '<p>Enter your custom formatted content here...</p>'
      },
      render: function(b, idx) {
        var d = b.data || {};
        return `
          <div class="acf-fields-grid">
            <div class="acf-field-row full-width">
              <label class="acf-field-label">Optional Block Heading</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.heading || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'heading', this.value)">
            </div>
            <div class="acf-field-row full-width">
              <label class="acf-field-label">HTML / Rich Content</label>
              <textarea class="acf-input" rows="5" style="font-family:monospace;font-size:12px;" oninput="window.AcfBuilder.updateField(${idx}, 'html_content', this.value)">${escapeHtml(d.html_content || '')}</textarea>
            </div>
          </div>
        `;
      }
    },

    'acf/contact-form': {
      name: 'Contact & Lead Form',
      icon: '📬',
      category: 'cta',
      desc: 'Direct customer inquiry submission form with custom field routing.',
      defaultData: {
        heading: 'Get in Touch with Our Engineering Team',
        subheading: 'Have a project or questions? Send us a message below.',
        form_type: 'general'
      },
      render: function(b, idx) {
        var d = b.data || {};
        return `
          <div class="acf-fields-grid">
            <div class="acf-field-row">
              <label class="acf-field-label">Form Heading</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.heading || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'heading', this.value)">
            </div>
            <div class="acf-field-row">
              <label class="acf-field-label">Form Subheading</label>
              <input type="text" class="acf-input" value="${escapeHtml(d.subheading || '')}" oninput="window.AcfBuilder.updateField(${idx}, 'subheading', this.value)">
            </div>
          </div>
        `;
      }
    }
  };

  // 2. HELPER UTILS
  function escapeHtml(str) {
    if (typeof str !== 'string') return str || '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // 3. BUILDER CONTROLLER
  var blocks = [];

  function safeParseBlocks(str) {
    if (!str || typeof str !== 'string') return [];
    var s = str.trim();
    if (!s || s === '[]') return [];

    // 1. Direct JSON parse
    try {
      var res = JSON.parse(s);
      if (Array.isArray(res)) return res;
      if (typeof res === 'string') return safeParseBlocks(res);
    } catch (e1) {
      // Continue to fallbacks
    }

    // 2. Decode HTML entities if present (e.g. &quot;)
    try {
      var txt = document.createElement('textarea');
      txt.innerHTML = s;
      var decoded = txt.value;
      if (decoded && decoded !== s) {
        var res2 = JSON.parse(decoded);
        if (Array.isArray(res2)) return res2;
      }
    } catch (e2) {
      // Continue to fallbacks
    }

    // 3. Fallback: Fix single-quoted Python dict representations
    try {
      var sanitized = s
        .replace(/'/g, '"')
        .replace(/\bTrue\b/g, 'true')
        .replace(/\bFalse\b/g, 'false')
        .replace(/\bNone\b/g, 'null');
      var res3 = JSON.parse(sanitized);
      if (Array.isArray(res3)) return res3;
    } catch (e3) {
      console.warn('Could not parse initial ACF blocks data:', s, e3);
    }

    return [];
  }

  function init() {
    var rawTextarea = document.getElementById('id_acf_blocks');
    if (!rawTextarea) return;

    var bootstrapScript = document.getElementById('acf-blocks-initial-data');
    var rawVal = '';
    if (bootstrapScript && bootstrapScript.textContent.trim()) {
      rawVal = bootstrapScript.textContent.trim();
    } else {
      rawVal = rawTextarea.value.trim();
    }

    blocks = safeParseBlocks(rawVal);

    renderAllBlocks();
    renderModalGrid('all');

    // Attach submit listener to ensure syncJson is always called prior to form submission
    var form = rawTextarea.closest('form');
    if (form) {
      form.addEventListener('submit', function() {
        syncJson();
      });
    }
  }

  function syncJson() {
    var rawTextarea = document.getElementById('id_acf_blocks');
    if (rawTextarea) {
      rawTextarea.value = JSON.stringify(blocks, null, 2);
    }
    var badge = document.getElementById('acf-blocks-badge-count');
    if (badge) {
      badge.textContent = blocks.length + (blocks.length === 1 ? ' block' : ' blocks');
    }
  }

  function renderAllBlocks() {
    var container = document.getElementById('acf-blocks-container');
    if (!container) return;

    syncJson();

    if (blocks.length === 0) {
      container.innerHTML = `
        <div style="text-align:center;padding:36px 16px;background:#fff;border:1px dashed #c3c4c7;border-radius:4px;">
          <div style="font-size:32px;margin-bottom:8px;">🧩</div>
          <h3 style="margin:0 0 6px 0;font-size:15px;color:#1d2327;">No ACF Blocks Added Yet</h3>
          <p style="margin:0 0 16px 0;font-size:12.5px;color:#646970;">Start constructing this page by adding flexible ACF blocks from the library.</p>
          <button type="button" class="button button-primary" onclick="window.AcfBuilder.openModal()" style="font-weight:600;">+ Add First ACF Block</button>
        </div>
      `;
      return;
    }

    var html = '';
    blocks.forEach(function(b, idx) {
      var def = ACF_BLOCK_DEFINITIONS[b.type] || {
        name: b.name || b.type,
        icon: '🧩',
        render: function() { return '<p>Custom block type</p>'; }
      };

      var isCollapsed = b._isCollapsed ? 'is-collapsed' : '';
      var isHidden = b.visible === false ? 'is-hidden' : '';
      var visText = b.visible === false ? 'Hidden' : 'Visible';
      var visClass = b.visible === false ? 'hidden' : 'visible';
      var labelDisplay = b.label ? b.label : def.name;

      html += `
        <div class="acf-block-card ${isCollapsed} ${isHidden}" data-block-index="${idx}">
          <div class="acf-block-header">
            <div class="acf-block-header-left" onclick="window.AcfBuilder.toggleCollapse(${idx})">
              <span class="acf-block-handle" title="Drag to reorder">⋮⋮</span>
              <span class="acf-block-icon">${def.icon}</span>
              <span class="acf-block-title">${def.name}</span>
              <span class="acf-block-type-badge">${b.type}</span>
              <span class="acf-block-label-display">— ${escapeHtml(labelDisplay)}</span>
              <span class="acf-block-visibility-badge ${visClass}">${visText}</span>
            </div>
            <div class="acf-block-actions">
              <button type="button" class="acf-action-btn" title="Move Up" onclick="window.AcfBuilder.moveBlock(${idx}, -1)" ${idx === 0 ? 'disabled style="opacity:0.3;"' : ''}>▲</button>
              <button type="button" class="acf-action-btn" title="Move Down" onclick="window.AcfBuilder.moveBlock(${idx}, 1)" ${idx === blocks.length - 1 ? 'disabled style="opacity:0.3;"' : ''}>▼</button>
              <button type="button" class="acf-action-btn" title="Toggle Visibility" onclick="window.AcfBuilder.toggleVisibility(${idx})">👁️</button>
              <button type="button" class="acf-action-btn" title="Duplicate Block" onclick="window.AcfBuilder.duplicateBlock(${idx})">⧉</button>
              <button type="button" class="acf-action-btn delete" title="Remove Block" onclick="window.AcfBuilder.removeBlock(${idx})">🗑️</button>
              <button type="button" class="acf-action-btn" title="Expand/Collapse" onclick="window.AcfBuilder.toggleCollapse(${idx})">
                ${b._isCollapsed ? '▸' : '▾'}
              </button>
            </div>
          </div>
          <div class="acf-block-body">
            <div class="acf-field-row" style="margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #f0f0f1;">
              <label class="acf-field-label">Admin Label (Custom Identifier)</label>
              <input type="text" class="acf-input" style="width:300px;" value="${escapeHtml(b.label || '')}" placeholder="e.g. Hero Section - Top" oninput="window.AcfBuilder.updateLabel(${idx}, this.value)">
            </div>
            ${def.render(b, idx)}
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
  }

  // 4. BLOCK ACTIONS
  function addBlock(type) {
    var def = ACF_BLOCK_DEFINITIONS[type];
    if (!def) return;

    var newBlock = {
      id: 'block_' + Date.now() + '_' + Math.floor(Math.random() * 1000),
      type: type,
      name: def.name,
      label: def.name,
      visible: true,
      _isCollapsed: false,
      data: JSON.parse(JSON.stringify(def.defaultData))
    };

    blocks.push(newBlock);
    renderAllBlocks();
    closeModal();

    // Scroll to the newly added block
    setTimeout(function() {
      var lastCard = document.querySelector('.acf-block-card:last-child');
      if (lastCard) {
        lastCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  }

  function removeBlock(idx) {
    if (confirm('Are you sure you want to remove this ACF block?')) {
      blocks.splice(idx, 1);
      renderAllBlocks();
    }
  }

  function moveBlock(idx, delta) {
    var newIdx = idx + delta;
    if (newIdx < 0 || newIdx >= blocks.length) return;
    var temp = blocks[idx];
    blocks[idx] = blocks[newIdx];
    blocks[newIdx] = temp;
    renderAllBlocks();
  }

  function duplicateBlock(idx) {
    var orig = blocks[idx];
    var clone = JSON.parse(JSON.stringify(orig));
    clone.id = 'block_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
    clone.label = (clone.label || orig.name) + ' (Copy)';
    clone._isCollapsed = false;
    blocks.splice(idx + 1, 0, clone);
    renderAllBlocks();
  }

  function toggleVisibility(idx) {
    if (blocks[idx].visible === false) {
      blocks[idx].visible = true;
    } else {
      blocks[idx].visible = false;
    }
    renderAllBlocks();
  }

  function toggleCollapse(idx) {
    blocks[idx]._isCollapsed = !blocks[idx]._isCollapsed;
    renderAllBlocks();
  }

  function expandAll() {
    blocks.forEach(function(b) { b._isCollapsed = false; });
    renderAllBlocks();
  }

  function collapseAll() {
    blocks.forEach(function(b) { b._isCollapsed = true; });
    renderAllBlocks();
  }

  function updateLabel(idx, val) {
    blocks[idx].label = val;
    syncJson();
    var card = document.querySelector(`.acf-block-card[data-block-index="${idx}"]`);
    if (card) {
      var disp = card.querySelector('.acf-block-label-display');
      if (disp) disp.textContent = '— ' + (val || blocks[idx].name);
    }
  }

  function updateField(idx, field, val) {
    if (!blocks[idx].data) blocks[idx].data = {};
    blocks[idx].data[field] = val;
    syncJson();
  }

  function updateStatItem(blockIdx, itemIdx, field, val) {
    if (!blocks[blockIdx].data) blocks[blockIdx].data = {};
    if (!Array.isArray(blocks[blockIdx].data.items)) blocks[blockIdx].data.items = [];
    if (!blocks[blockIdx].data.items[itemIdx]) blocks[blockIdx].data.items[itemIdx] = {};
    blocks[blockIdx].data.items[itemIdx][field] = val;
    syncJson();
  }

  // 5. MODAL PICKER
  function openModal() {
    var modal = document.getElementById('acf-block-picker-modal');
    if (modal) {
      modal.style.display = 'flex';
      var search = document.getElementById('acf-block-search-input');
      if (search) {
        search.value = '';
        search.focus();
      }
      renderModalGrid('all');
    }
  }

  function closeModal() {
    var modal = document.getElementById('acf-block-picker-modal');
    if (modal) modal.style.display = 'none';
  }

  function renderModalGrid(category, query) {
    var grid = document.getElementById('acf-blocks-modal-grid');
    if (!grid) return;

    var q = (query || '').toLowerCase().trim();
    var html = '';

    Object.keys(ACF_BLOCK_DEFINITIONS).forEach(function(key) {
      var def = ACF_BLOCK_DEFINITIONS[key];
      if (category && category !== 'all' && def.category !== category) return;
      if (q && def.name.toLowerCase().indexOf(q) === -1 && def.desc.toLowerCase().indexOf(q) === -1) return;

      html += `
        <div class="acf-block-picker-item" onclick="window.AcfBuilder.addBlock('${key}')">
          <div class="acf-picker-top">
            <span class="acf-picker-icon">${def.icon}</span>
            <span class="acf-picker-title">${def.name}</span>
          </div>
          <p class="acf-picker-desc">${def.desc}</p>
        </div>
      `;
    });

    if (!html) {
      html = '<div style="grid-column:1/-1;text-align:center;padding:24px;color:#646970;">No matching blocks found.</div>';
    }

    grid.innerHTML = html;
  }

  // 6. EXPOSE GLOBAL INTERFACE
  window.AcfBuilder = {
    init: init,
    openModal: openModal,
    closeModal: closeModal,
    addBlock: addBlock,
    removeBlock: removeBlock,
    moveBlock: moveBlock,
    duplicateBlock: duplicateBlock,
    toggleVisibility: toggleVisibility,
    toggleCollapse: toggleCollapse,
    expandAll: expandAll,
    collapseAll: collapseAll,
    updateLabel: updateLabel,
    updateField: updateField,
    updateStatItem: updateStatItem,
    renderModalGrid: renderModalGrid
  };

  document.addEventListener('DOMContentLoaded', init);
})();
