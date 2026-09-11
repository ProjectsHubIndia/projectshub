/* ════════════════════════════════════════════════════════════
   AI Chatbot — Vanilla JS implementation
   Features: Toggle, messaging, typing indicator, theme support
   ════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    class AIChatbot {
        constructor() {
            this.isOpen = false;
            this.messages = [];
            this.isTyping = false;
            this.unreadCount = 0;
            this.sessionId = this.getOrCreateSessionId();
            this.init();
        }

        getOrCreateSessionId() {
            try {
                let sid = localStorage.getItem('projectshub_chat_session');
                if (!sid) {
                    sid = 'chat_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now().toString(36);
                    localStorage.setItem('projectshub_chat_session', sid);
                }
                return sid;
            } catch (e) {
                return 'chat_' + Math.random().toString(36).substring(2, 10);
            }
        }

        sendToBackend(text, sender) {
            try {
                fetch('/api/chatbot/message/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        session_id: this.sessionId,
                        sender: sender,
                        message: text,
                        page_url: window.location.pathname + window.location.search
                    })
                }).catch(function(err) {
                    console.debug('Chatbot backend telemetry offline:', err);
                });
            } catch (e) {}
        }

        init() {
            // Inject HTML
            this.createChatbotHTML();
            this.cacheElements();
            this.bindEvents();
            
            // Load saved messages from localStorage
            this.loadMessages();
            
            // Send welcome message
            if (this.messages.length === 0) {
                this.addBotMessage("Hi there! 👋 I'm ProjectsHub AI. How can I help you today?");
            } else {
                this.renderMessages();
            }
        }

        createChatbotHTML() {
            if (document.querySelector('.ai-chatbot-widget')) return;

            const html = `
                <div class="ai-chatbot-widget">
                    <button class="ai-chatbot-toggle" aria-label="Open AI Assistant" aria-expanded="false" title="Chat with ProjectsHub AI">
                        <svg class="chatbot-icon chatbot-icon--chat" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                        </svg>
                        <svg class="chatbot-icon chatbot-icon--close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                    <div class="ai-chatbot-window" role="dialog" aria-modal="false" aria-label="ProjectsHub AI Chat">
                        <div class="ai-chatbot-header">
                            <div class="ai-chatbot-header-title">
                                <img src="/static/image/logo/projectshub-logo-dark.svg" alt="ProjectsHub" class="ai-chatbot-logo ai-chatbot-logo--dark" width="120" height="38" />
                                <img src="/static/image/logo/projectshub-logo-light.svg" alt="ProjectsHub" class="ai-chatbot-logo ai-chatbot-logo--light" width="120" height="38" />
                                <div class="ai-chatbot-header-info">
                                    <span class="ai-chatbot-name">ProjectsHub AI</span>
                                    <span class="ai-chatbot-status"><span class="ai-chatbot-status-dot"></span> Online</span>
                                </div>
                            </div>
                            <button class="ai-chatbot-close" aria-label="Close chat">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                                    <line x1="18" y1="6" x2="6" y2="18"></line>
                                    <line x1="6" y1="6" x2="18" y2="18"></line>
                                </svg>
                            </button>
                        </div>

                        <div class="ai-chatbot-messages">
                            <div class="ai-chatbot-empty">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                                </svg>
                                <p>Start a conversation with ProjectsHub AI</p>
                            </div>
                        </div>

                        <form class="ai-chatbot-input-form">
                            <input 
                                type="text" 
                                class="ai-chatbot-input" 
                                placeholder="Type a message..."
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
            this.emptyState = document.querySelector('.ai-chatbot-empty');
            this.form = document.querySelector('.ai-chatbot-input-form');
            this.input = document.querySelector('.ai-chatbot-input');
            this.sendBtn = document.querySelector('.ai-chatbot-send-btn');
            this.badge = null;
        }

        bindEvents() {
            if (this.toggle) {
                this.toggle.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleChat();
                });
            }
            if (this.closeBtn) {
                this.closeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleChat(false);
                });
            }
            if (this.form) {
                this.form.addEventListener('submit', (e) => this.handleSubmit(e));
            }
            if (this.input) {
                this.input.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        this.handleSubmit(e);
                    }
                });
            }

            // Close on Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.toggleChat(false);
                }
            });

            // Close on click outside
            document.addEventListener('click', (e) => {
                if (this.isOpen && this.widget && !this.widget.contains(e.target)) {
                    this.toggleChat(false);
                }
            });
        }

        toggleChat(force) {
            this.isOpen = (typeof force === 'boolean') ? force : !this.isOpen;
            if (this.window) {
                this.window.classList.toggle('is-open', this.isOpen);
            }
            if (this.toggle) {
                this.toggle.classList.toggle('is-active', this.isOpen);
                this.toggle.setAttribute('aria-expanded', this.isOpen ? 'true' : 'false');
                this.toggle.setAttribute('aria-label', this.isOpen ? 'Close AI Assistant' : 'Open AI Assistant');
            }
            
            if (this.isOpen && this.input) {
                setTimeout(() => this.input.focus(), 150);
                this.clearUnreadBadge();
            }
        }

        handleSubmit(e) {
            e.preventDefault();
            const text = this.input.value.trim();
            
            if (!text || this.isTyping) return;
            
            this.addUserMessage(text);
            this.input.value = '';
            this.sendBtn.disabled = true;
            
            // Simulate typing delay
            this.isTyping = true;
            this.showTypingIndicator();
            
            setTimeout(() => {
                this.removeTypingIndicator();
                const response = this.generateResponse(text);
                this.addBotMessage(response);
                this.isTyping = false;
                this.sendBtn.disabled = false;
            }, 1000 + Math.random() * 1000);
        }

        addUserMessage(text) {
            const message = { text, isUser: true, timestamp: Date.now() };
            this.messages.push(message);
            this.renderMessages();
            this.saveMessages();
            this.sendToBackend(text, 'user');
        }

        addBotMessage(text) {
            const message = { text, isUser: false, timestamp: Date.now() };
            this.messages.push(message);
            this.renderMessages();
            this.saveMessages();
            this.sendToBackend(text, 'bot');
            
            // Show unread badge if closed
            if (!this.isOpen) {
                this.unreadCount++;
                this.updateBadge();
            }
        }

        renderMessages() {
            // Remove empty state
            if (this.messagesContainer.querySelector('.ai-chatbot-empty')) {
                this.messagesContainer.innerHTML = '';
            }

            // Clear and rebuild
            this.messagesContainer.innerHTML = '';

            this.messages.forEach(msg => {
                const bubble = document.createElement('div');
                bubble.className = `ai-chatbot-message ${msg.isUser ? 'user' : 'bot'}`;
                bubble.innerHTML = `
                    <div class="ai-chatbot-message-bubble">${this.escapeHtml(msg.text)}</div>
                `;
                this.messagesContainer.appendChild(bubble);
            });

            // Scroll to bottom
            this.scrollToBottom();
        }

        showTypingIndicator() {
            const typing = document.createElement('div');
            typing.className = 'ai-chatbot-message bot';
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
            const typing = this.messagesContainer.querySelector('.ai-chatbot-typing');
            if (typing) {
                typing.parentElement.remove();
            }
        }

        generateResponse(userMessage) {
            const msg = userMessage.toLowerCase();
            
            const responses = {
                greeting: [
                    "Hello! How can I assist you today?",
                    "Hi there! What can I help you with?",
                    "Hey! Nice to meet you. What's on your mind?"
                ],
                help: [
                    "I'm here to help! Feel free to ask me anything about our services, projects, or the workshop.",
                    "Sure! You can ask me about our AI solutions, workshops, or anything else you'd like to know."
                ],
                project: [
                    "We offer various AI-powered solutions including machine learning APIs, data science services, and custom AI implementations. Would you like to know more about any specific service?",
                    "Our projects range from ML models to data analytics. What interests you most?"
                ],
                workshop: [
                    "Our 4-day AI & ML workshop covers Python, TensorFlow, real-world AI systems, and hands-on projects. Check the workshop page for full details!",
                    "The workshop teaches practical AI skills over 4 intensive days. Interested in joining?"
                ],
                pricing: [
                    "For pricing information, please check our pricing page or contact us directly for a custom quote.",
                    "Pricing varies based on project scope. Would you like to discuss a specific project?"
                ],
                contact: [
                    "You can reach us through the contact form on our website, or feel free to ask me any questions!",
                    "Feel free to submit the contact form, and our team will get back to you shortly."
                ],
                thanks: [
                    "You're welcome! Is there anything else I can help you with?",
                    "Happy to help! Let me know if you have more questions."
                ]
            };

            // Match keywords
            if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey')) {
                return responses.greeting[Math.floor(Math.random() * responses.greeting.length)];
            }
            if (msg.includes('help')) {
                return responses.help[Math.floor(Math.random() * responses.help.length)];
            }
            if (msg.includes('project')) {
                return responses.project[Math.floor(Math.random() * responses.project.length)];
            }
            if (msg.includes('workshop')) {
                return responses.workshop[Math.floor(Math.random() * responses.workshop.length)];
            }
            if (msg.includes('price') || msg.includes('cost')) {
                return responses.pricing[Math.floor(Math.random() * responses.pricing.length)];
            }
            if (msg.includes('contact')) {
                return responses.contact[Math.floor(Math.random() * responses.contact.length)];
            }
            if (msg.includes('thank')) {
                return responses.thanks[Math.floor(Math.random() * responses.thanks.length)];
            }

            // Default responses
            const defaults = [
                "That's a great question! Could you tell me more about what you're looking for?",
                "Interesting! Our team specializes in AI solutions. Would you like to know more?",
                "I appreciate your interest! Feel free to explore our services or contact us for more details.",
                "I'm here to help! Is there anything specific about our AI services you'd like to know?",
                "That's helpful to know! Let me know if I can provide more information about ProjectsHub."
            ];

            return defaults[Math.floor(Math.random() * defaults.length)];
        }

        scrollToBottom() {
            setTimeout(() => {
                this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            }, 0);
        }

        updateBadge() {
            if (this.badge) {
                this.badge.style.display = 'none';
            }
        }

        clearUnreadBadge() {
            this.unreadCount = 0;
            this.updateBadge();
        }

        saveMessages() {
            try {
                localStorage.setItem('ai-chatbot-messages', JSON.stringify(this.messages));
            } catch (e) {
                // localStorage might be disabled
            }
        }

        loadMessages() {
            try {
                const saved = localStorage.getItem('ai-chatbot-messages');
                if (saved) {
                    this.messages = JSON.parse(saved);
                }
            } catch (e) {
                // Failed to load, start fresh
            }
        }

        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Public API to add messages programmatically
        static addMessage(text, isUser = false) {
            const event = new CustomEvent('ai-chatbot-add-message', {
                detail: { text, isUser }
            });
            document.dispatchEvent(event);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.chatbot = new AIChatbot();
        });
    } else {
        window.chatbot = new AIChatbot();
    }

    // Custom event listener for adding messages
    document.addEventListener('ai-chatbot-add-message', (e) => {
        if (window.chatbot) {
            if (e.detail.isUser) {
                window.chatbot.addUserMessage(e.detail.text);
            } else {
                window.chatbot.addBotMessage(e.detail.text);
            }
        }
    });
})();
