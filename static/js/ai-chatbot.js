/* ═══════════════════════════════════════════════════════════════════════════════
   PROJECTSHUB AI CHATBOT — HIGH-CONVERSION LEAD GENERATION ENGINE (2026)
   Features: Proactive Teaser, Quick Intent Action Chips, In-Chat Lead Capture,
             Direct WhatsApp Handoff, Smart Knowledge Base, Dual CRM Sync
   ═══════════════════════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    var WHATSAPP_PHONE = '919213472954';

    class AIChatbot {
        constructor() {
            this.isOpen = false;
            this.messages = [];
            this.isTyping = false;
            this.unreadCount = 0;
            this.sessionId = this.getOrCreateSessionId();
            this.teaserTimer = null;
            this.init();
        }

        getOrCreateSessionId() {
            try {
                var sid = localStorage.getItem('projectshub_chat_session');
                if (!sid) {
                    sid = 'chat_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now().toString(36);
                    localStorage.setItem('projectshub_chat_session', sid);
                }
                return sid;
            } catch (e) {
                return 'chat_' + Math.random().toString(36).substring(2, 10);
            }
        }

        sendToBackend(text, sender, meta) {
            try {
                var payload = {
                    session_id: this.sessionId,
                    sender: sender,
                    message: text,
                    page_url: window.location.pathname + window.location.search
                };
                if (meta) {
                    if (meta.name) payload.user_name = meta.name;
                    if (meta.email) payload.user_email = meta.email;
                    if (meta.phone) payload.user_phone = meta.phone;
                    if (meta.interest) payload.service_interest = meta.interest;
                }

                fetch('/api/chatbot/message/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }).catch(function(err) {
                    console.debug('Chatbot backend telemetry offline:', err);
                });
            } catch (e) {}
        }

        init() {
            this.createChatbotHTML();
            this.cacheElements();
            this.bindEvents();
            this.loadMessages();

            if (this.messages.length === 0) {
                this.addWelcomeFlow();
            } else {
                this.renderMessages();
            }

            this.initProactiveTeaser();
        }

        createChatbotHTML() {
            if (document.querySelector('.ai-chatbot-widget')) return;

            var html = `
                <div class="ai-chatbot-widget">
                    <!-- Proactive Engagement Teaser Bubble -->
                    <div class="ai-chatbot-teaser-bubble" id="aiChatbotTeaser" role="alert">
                        <div class="ai-chatbot-teaser-header">
                            <div class="ai-chatbot-teaser-avatar-group">
                                <div class="ai-chatbot-teaser-avatar">🤖</div>
                                <span class="ai-chatbot-teaser-title">ProjectsHub AI Architect</span>
                            </div>
                            <button type="button" class="ai-chatbot-teaser-close" aria-label="Dismiss">&times;</button>
                        </div>
                        <p class="ai-chatbot-teaser-text">
                            Looking for production AI project code, custom ML systems, or 3-Day Bootcamp enrollment?
                        </p>
                        <div class="ai-chatbot-teaser-cta">
                            <span>💬 Let's Chat Now &rarr;</span>
                        </div>
                    </div>

                    <!-- Floating Toggle Button -->
                    <button class="ai-chatbot-toggle" aria-label="Open AI Assistant" aria-expanded="false" title="Chat with ProjectsHub AI">
                        <svg class="chatbot-icon chatbot-icon--chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                        </svg>
                        <svg class="chatbot-icon chatbot-icon--close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>

                    <!-- Main Chat Window -->
                    <div class="ai-chatbot-window" role="dialog" aria-modal="false" aria-label="ProjectsHub AI Chat">
                        <div class="ai-chatbot-header">
                            <div class="ai-chatbot-header-title">
                                <div class="ai-chatbot-avatar-circle" style="width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#0284c7,#6366f1);display:flex;align-items:center;justify-content:center;color:#ffffff;box-shadow:0 0 12px rgba(56,189,248,0.4);">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M12 2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2 2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/>
                                        <rect x="4" y="8" width="16" height="12" rx="2"/>
                                        <line x1="9" y1="13" x2="9.01" y2="13"/>
                                        <line x1="15" y1="13" x2="15.01" y2="13"/>
                                    </svg>
                                </div>
                                <div class="ai-chatbot-header-info">
                                    <span class="ai-chatbot-name" style="font-weight:700;letter-spacing:-0.01em;">ProjectsHub AI</span>
                                    <span class="ai-chatbot-status"><span class="ai-chatbot-status-dot"></span> Senior Engineer Online</span>
                                </div>
                            </div>
                            <div style="display:flex;align-items:center;gap:8px;">
                                <a href="https://wa.me/${WHATSAPP_PHONE}?text=Hi%20ProjectsHub%20Team%2C%20I%20am%20chatting%20from%20the%20website%20and%20want%20to%20connect%20with%20an%20engineer." target="_blank" rel="noopener noreferrer" class="ai-chatbot-wa-btn" title="Chat with Engineer on WhatsApp" aria-label="WhatsApp" style="display:flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:8px;background:rgba(37,211,102,0.12);color:#25d366;border:1px solid rgba(37,211,102,0.25);text-decoration:none;transition:all 0.2s ease;">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                                        <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.771-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.312.045-.694.062-2.18-.553-1.616-.669-2.658-2.298-2.738-2.404-.08-.107-.648-.864-.648-1.648 0-.785.412-1.171.558-1.332.146-.16.32-.201.427-.201.107 0 .213.001.306.006.1.005.234-.038.365.277.135.325.462 1.127.502 1.208.04.082.067.178.013.285-.053.107-.08.173-.16.267-.08.093-.167.208-.24.279-.08.08-.163.167-.07.327.093.16.413.682.887 1.103.61.542 1.123.71 1.283.79.16.08.254.067.348-.041.094-.108.4-.467.507-.628.107-.16.213-.134.36-.08.146.053.933.44 1.093.52.16.08.267.12.307.187.04.067.04.387-.104.792z"/>
                                    </svg>
                                </a>
                                <button class="ai-chatbot-close" aria-label="Close chat">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                        <line x1="18" y1="6" x2="6" y2="18"></line>
                                        <line x1="6" y1="6" x2="18" y2="18"></line>
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <div class="ai-chatbot-messages" id="aiChatbotMessages">
                            <div class="ai-chatbot-empty">
                                <p>Starting conversation with ProjectsHub AI...</p>
                            </div>
                        </div>

                        <form class="ai-chatbot-input-form">
                            <input 
                                type="text" 
                                class="ai-chatbot-input" 
                                placeholder="Ask about projects, bootcamp, pricing..."
                                autocomplete="off"
                                aria-label="Your message to ProjectsHub AI"
                            />
                            <button type="submit" class="ai-chatbot-send-btn" aria-label="Send message">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
                                    <line x1="22" y1="2" x2="11" y2="13"></line>
                                    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                                </svg>
                            </button>
                        </form>
                    </div>
                </div>
            `;

            document.body.insertAdjacentHTML('beforeend', html);
        }

        cacheElements() {
            this.widget = document.querySelector('.ai-chatbot-widget');
            this.toggle = document.querySelector('.ai-chatbot-toggle');
            this.window = document.querySelector('.ai-chatbot-window');
            this.closeBtn = document.querySelector('.ai-chatbot-close');
            this.messagesContainer = document.querySelector('.ai-chatbot-messages');
            this.form = document.querySelector('.ai-chatbot-input-form');
            this.input = document.querySelector('.ai-chatbot-input');
            this.sendBtn = document.querySelector('.ai-chatbot-send-btn');
            this.teaser = document.getElementById('aiChatbotTeaser');
        }

        bindEvents() {
            var self = this;

            if (this.toggle) {
                this.toggle.addEventListener('click', function (e) {
                    e.stopPropagation();
                    self.toggleChat();
                });
            }

            if (this.closeBtn) {
                this.closeBtn.addEventListener('click', function (e) {
                    e.stopPropagation();
                    self.toggleChat(false);
                });
            }

            if (this.teaser) {
                this.teaser.addEventListener('click', function(e) {
                    if (e.target.closest('.ai-chatbot-teaser-close')) {
                        e.stopPropagation();
                        self.dismissTeaser();
                        return;
                    }
                    self.dismissTeaser();
                    self.toggleChat(true);
                });
            }

            if (this.form) {
                this.form.addEventListener('submit', function (e) {
                    self.handleSubmit(e);
                });
            }

            if (this.input) {
                this.input.addEventListener('keydown', function (e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        self.handleSubmit(e);
                    }
                });
            }

            document.addEventListener('keydown', function (e) {
                if (e.key === 'Escape' && self.isOpen) {
                    self.toggleChat(false);
                }
            });

            document.addEventListener('click', function (e) {
                if (self.isOpen && self.widget && !self.widget.contains(e.target)) {
                    self.toggleChat(false);
                }
            });
        }

        initProactiveTeaser() {
            var self = this;
            try {
                if (sessionStorage.getItem('ph_teaser_dismissed') === '1') return;
            } catch (e) {}

            this.teaserTimer = setTimeout(function () {
                if (!self.isOpen && self.teaser) {
                    self.teaser.classList.add('is-visible');
                    document.body.classList.add('has-teaser');
                }
            }, 6000);
        }

        dismissTeaser() {
            if (this.teaser) {
                this.teaser.classList.remove('is-visible');
            }
            document.body.classList.remove('has-teaser');
            try {
                sessionStorage.setItem('ph_teaser_dismissed', '1');
            } catch (e) {}
        }

        toggleChat(force) {
            this.isOpen = (typeof force === 'boolean') ? force : !this.isOpen;
            if (this.window) {
                this.window.classList.toggle('is-open', this.isOpen);
            }
            if (this.toggle) {
                this.toggle.classList.toggle('is-active', this.isOpen);
                this.toggle.setAttribute('aria-expanded', this.isOpen ? 'true' : 'false');
            }
            document.body.classList.toggle('chatbot-open', this.isOpen);
            if (this.isOpen) {
                this.dismissTeaser();
                if (this.input) {
                    setTimeout(() => this.input.focus(), 150);
                }
            }
        }

        addWelcomeFlow() {
            var welcomeText = "Hi there! 👋 I'm ProjectsHub AI. I can guide you through production AI project code, help you enroll in our intensive 3-Day Autonomous Multi-Agent AI Bootcamp, or connect you with our engineering team for custom enterprise AI development.";
            
            this.messages.push({
                text: welcomeText,
                isUser: false,
                hasChips: true,
                timestamp: Date.now()
            });

            this.renderMessages();
            this.saveMessages();
            this.sendToBackend(welcomeText, 'bot');
        }

        handleSubmit(e) {
            e.preventDefault();
            var text = this.input.value.trim();
            if (!text || this.isTyping) return;

            this.addUserMessage(text);
            this.input.value = '';
            this.sendBtn.disabled = true;

            this.isTyping = true;
            this.showTypingIndicator();

            var self = this;
            setTimeout(function () {
                self.removeTypingIndicator();
                var result = self.processUserQuery(text);
                self.addBotMessage(result.text, result.hasChips, result.showLeadCard, result.leadInterest);
                self.isTyping = false;
                self.sendBtn.disabled = false;
            }, 800 + Math.random() * 600);
        }

        addUserMessage(text) {
            var message = { text: text, isUser: true, timestamp: Date.now() };
            this.messages.push(message);
            this.renderMessages();
            this.saveMessages();
            this.sendToBackend(text, 'user');
        }

        addBotMessage(text, hasChips, showLeadCard, leadInterest) {
            var message = {
                text: text,
                isUser: false,
                hasChips: !!hasChips,
                showLeadCard: !!showLeadCard,
                leadInterest: leadInterest || '',
                timestamp: Date.now()
            };
            this.messages.push(message);
            this.renderMessages();
            this.saveMessages();
            this.sendToBackend(text, 'bot');
        }

        handleChipClick(topic) {
            var query = '';
            if (topic === 'projects') query = 'I want to explore AI Projects and source code.';
            else if (topic === 'bootcamp') query = 'Tell me about the 3-Day Autonomous Agents Bootcamp curriculum.';
            else if (topic === 'services') query = 'I need custom enterprise AI development.';
            else if (topic === 'tools') query = 'What free developer AI tools do you offer?';
            else if (topic === 'lead_form') query = 'I would like to request a callback / custom quote.';
            else if (topic === 'whatsapp') {
                window.open(`https://wa.me/${WHATSAPP_PHONE}?text=Hi%20ProjectsHub%2C%20I%20am%20interested%20in%20your%20AI%20Projects%20and%20Services.`, '_blank');
                return;
            }

            if (query) {
                this.addUserMessage(query);
                this.isTyping = true;
                this.showTypingIndicator();
                var self = this;
                setTimeout(function () {
                    self.removeTypingIndicator();
                    var result = self.processUserQuery(query);
                    self.addBotMessage(result.text, result.hasChips, result.showLeadCard, result.leadInterest);
                    self.isTyping = false;
                }, 700);
            }
        }

        processUserQuery(userMessage) {
            var msg = userMessage.toLowerCase();

            // 1. Bootcamp & Workshop
            if (msg.includes('bootcamp') || msg.includes('workshop') || msg.includes('agent') || msg.includes('curriculum')) {
                return {
                    text: "Our flagship 3-Day Autonomous Multi-Agent AI Bootcamp covers LangGraph, CrewAI, memory systems, tool routing, and production deployment from scratch. Includes 100% hands-on code and verified certificate. Would you like our senior architect to send you the curriculum and claim your spot?",
                    hasChips: false,
                    showLeadCard: true,
                    leadInterest: '3-Day Autonomous Agents Bootcamp'
                };
            }

            // 2. Custom Development & Business
            if (msg.includes('custom') || msg.includes('hire') || msg.includes('business') || msg.includes('service') || msg.includes('mvp') || msg.includes('company')) {
                return {
                    text: "We build and deploy end-to-end production AI applications: LLM agents, computer vision, automated workflow pipelines, and scalable microservices. Enter your details below to schedule an architectural scoping call with our lead AI engineer:",
                    hasChips: false,
                    showLeadCard: true,
                    leadInterest: 'Custom AI Development for Business'
                };
            }

            // 3. AI Projects & Source Code
            if (msg.includes('project') || msg.includes('code') || msg.includes('github') || msg.includes('source') || msg.includes('dataset') || msg.includes('repo')) {
                return {
                    text: "We have 50+ production-grade AI projects with full codebases, architecture diagrams, datasets, and video explanations across Computer Vision, NLP, and Autonomous Agents. You can browse our catalog at /projects/ or submit your details to get instant repository recommendations:",
                    hasChips: false,
                    showLeadCard: true,
                    leadInterest: 'AI Projects & Source Code'
                };
            }

            // 4. Pricing / Cost / Quote
            if (msg.includes('price') || msg.includes('cost') || msg.includes('fee') || msg.includes('quote') || msg.includes('callback') || msg.includes('consult')) {
                return {
                    text: "Our pricing is transparent with modular packages for students, developers, and enterprise teams. Submit your contact details below, and we will send you tailored pricing breakdown and project scope within 30 minutes:",
                    hasChips: false,
                    showLeadCard: true,
                    leadInterest: 'Pricing & Project Estimation'
                };
            }

            // 5. Free Tools
            if (msg.includes('tool') || msg.includes('free')) {
                return {
                    text: "You can explore our free suite of developer utilities including prompt optimizers, model benchmark calculators, and token estimators in our Tools Directory at /tools/.",
                    hasChips: true,
                    showLeadCard: false
                };
            }

            // 6. Greetings
            if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey')) {
                return {
                    text: "Hello! Great to connect with you. How can I assist you with our AI projects, bootcamps, or custom engineering solutions today?",
                    hasChips: true,
                    showLeadCard: false
                };
            }

            // 7. Fallback with direct Lead Card offer
            return {
                text: "Thanks for asking! Our engineering team specializes in production-ready AI solutions, research codebases, and custom LLM deployments. Would you like to connect directly with a senior AI engineer?",
                hasChips: true,
                showLeadCard: true,
                leadInterest: 'General AI Consultation'
            };
        }

        submitLeadCard(e, formEl) {
            e.preventDefault();
            var name = formEl.querySelector('input[name="name"]').value.trim();
            var email = formEl.querySelector('input[name="email"]').value.trim();
            var phone = formEl.querySelector('input[name="phone"]').value.trim();
            var interest = formEl.querySelector('select[name="interest"]').value;
            var submitBtn = formEl.querySelector('button[type="submit"]');

            if (!email && !phone) {
                alert('Please enter your email or phone number.');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>Submitting... ⏳</span>';

            var self = this;
            fetch('/api/chatbot/lead/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: self.sessionId,
                    name: name,
                    email: email,
                    phone: phone,
                    interest: interest,
                    page_url: window.location.pathname + window.location.search
                })
            })
            .then(function (res) { return res.json(); })
            .then(function (data) {
                if (data.success) {
                    var cardContainer = formEl.closest('.ai-chatbot-lead-card');
                    if (cardContainer) {
                        cardContainer.innerHTML = `
                            <div class="ai-chatbot-lead-success">
                                <div class="ai-chatbot-lead-success-title">🎯 Consultation Request Confirmed!</div>
                                <div class="ai-chatbot-lead-success-msg">
                                    Thank you, <strong>${self.escapeHtml(name || 'there')}</strong>! A senior AI engineer has received your inquiry for <em>${self.escapeHtml(interest)}</em> and will contact you via WhatsApp/Email shortly.
                                </div>
                                <a href="https://wa.me/${WHATSAPP_PHONE}?text=Hi%20ProjectsHub%20Team%2C%20my%20name%20is%20${encodeURIComponent(name)}.%20I%20just%20submitted%20a%20consultation%20request%20for%20${encodeURIComponent(interest)}." target="_blank" rel="noopener noreferrer" class="ai-chatbot-whatsapp-btn">
                                    <span>💬 Chat on WhatsApp Directly &rarr;</span>
                                </a>
                            </div>
                        `;
                    }
                    self.saveMessages();
                } else {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<span>Request Consultation &rarr;</span>';
                    alert(data.error || 'Submission failed. Please try again.');
                }
            })
            .catch(function (err) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span>Request Consultation &rarr;</span>';
                console.error('Lead submission error:', err);
                alert('Network error. Please chat with us on WhatsApp or submit through our contact page.');
            });
        }

        renderMessages() {
            var self = this;
            if (this.messagesContainer.querySelector('.ai-chatbot-empty')) {
                this.messagesContainer.innerHTML = '';
            }

            this.messagesContainer.innerHTML = '';

            this.messages.forEach(function (msg, idx) {
                var bubble = document.createElement('div');
                bubble.className = `ai-chatbot-message ${msg.isUser ? 'user' : 'bot'}`;

                var contentHtml = `<div class="ai-chatbot-message-bubble">${self.escapeHtml(msg.text)}</div>`;

                // Render Quick Action Chips if present
                if (msg.hasChips) {
                    contentHtml += `
                        <div class="ai-chatbot-chips-wrap">
                            <button type="button" class="ai-chatbot-chip" onclick="window.chatbot.handleChipClick('projects')">🚀 AI Projects</button>
                            <button type="button" class="ai-chatbot-chip" onclick="window.chatbot.handleChipClick('bootcamp')">🎓 3-Day Bootcamp</button>
                            <button type="button" class="ai-chatbot-chip" onclick="window.chatbot.handleChipClick('services')">💼 Custom AI</button>
                            <button type="button" class="ai-chatbot-chip" onclick="window.chatbot.handleChipClick('tools')">🛠️ Free Tools</button>
                            <button type="button" class="ai-chatbot-chip" onclick="window.chatbot.handleChipClick('lead_form')">📞 Request Callback</button>
                            <button type="button" class="ai-chatbot-chip" onclick="window.chatbot.handleChipClick('whatsapp')">💬 WhatsApp</button>
                        </div>
                    `;
                }

                // Render Lead Capture Card if present
                if (msg.showLeadCard) {
                    contentHtml += `
                        <div class="ai-chatbot-lead-card" data-card-idx="${idx}">
                            <div class="ai-chatbot-lead-card-header">
                                <span class="ai-chatbot-lead-card-icon">🎯</span>
                                <div>
                                    <h4 class="ai-chatbot-lead-card-title">Direct AI Engineer Consultation</h4>
                                    <p class="ai-chatbot-lead-card-desc">Receive tailored repository recommendations, syllabus, and custom pricing.</p>
                                </div>
                            </div>
                            <form class="ai-chatbot-lead-form" onsubmit="window.chatbot.submitLeadCard(event, this)">
                                <input type="text" name="name" placeholder="Your Name" required class="ai-chatbot-lead-input" />
                                <input type="email" name="email" placeholder="Email Address" required class="ai-chatbot-lead-input" />
                                <input type="tel" name="phone" placeholder="WhatsApp / Phone Number" required class="ai-chatbot-lead-input" />
                                <select name="interest" class="ai-chatbot-lead-input ai-chatbot-lead-select">
                                    <option value="AI Projects & Source Code" ${msg.leadInterest === 'AI Projects & Source Code' ? 'selected' : ''}>AI Projects & Source Code</option>
                                    <option value="3-Day Autonomous Agents Bootcamp" ${msg.leadInterest === '3-Day Autonomous Agents Bootcamp' ? 'selected' : ''}>3-Day AI Bootcamp</option>
                                    <option value="Custom AI Development for Business" ${msg.leadInterest === 'Custom AI Development for Business' ? 'selected' : ''}>Custom AI Development</option>
                                    <option value="Pricing & Project Estimation" ${msg.leadInterest === 'Pricing & Project Estimation' ? 'selected' : ''}>Pricing & Estimation</option>
                                    <option value="General AI Consultation" ${msg.leadInterest === 'General AI Consultation' ? 'selected' : ''}>General Consultation</option>
                                </select>
                                <button type="submit" class="ai-chatbot-lead-submit">
                                    <span>Request Consultation &rarr;</span>
                                </button>
                            </form>
                        </div>
                    `;
                }

                bubble.innerHTML = contentHtml;
                self.messagesContainer.appendChild(bubble);
            });

            this.scrollToBottom();
        }

        showTypingIndicator() {
            var typing = document.createElement('div');
            typing.className = 'ai-chatbot-message bot ai-typing-wrap';
            typing.innerHTML = `
                <div class="ai-chatbot-typing">
                    <div class="ai-chatbot-typing-dot"></div>
                    <div class="ai-chatbot-typing-dot"></div>
                    <div class="ai-chatbot-typing-dot"></div>
                </div>
            `;
            this.messagesContainer.appendChild(typing);
            this.scrollToBottom();
        }

        removeTypingIndicator() {
            var typing = this.messagesContainer.querySelector('.ai-typing-wrap');
            if (typing) {
                typing.remove();
            }
        }

        scrollToBottom() {
            var self = this;
            setTimeout(function () {
                if (self.messagesContainer) {
                    self.messagesContainer.scrollTop = self.messagesContainer.scrollHeight;
                }
            }, 50);
        }

        saveMessages() {
            try {
                localStorage.setItem('ai-chatbot-messages', JSON.stringify(this.messages));
            } catch (e) {}
        }

        loadMessages() {
            try {
                var saved = localStorage.getItem('ai-chatbot-messages');
                if (saved) {
                    var parsed = JSON.parse(saved);
                    if (Array.isArray(parsed) && parsed.length > 0) {
                        this.messages = parsed;
                    }
                }
            } catch (e) {}
        }

        escapeHtml(text) {
            if (typeof text !== 'string') return text || '';
            var div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            window.chatbot = new AIChatbot();
        });
    } else {
        window.chatbot = new AIChatbot();
    }
})();
