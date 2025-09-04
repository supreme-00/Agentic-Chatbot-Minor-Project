class AIChatbot {
    constructor() {
        this.messages = [];
        this.isRecording = false;
        this.isLoading = false;
        this.recognition = null;
        this.currentMessageId = 1;
        
        // Initialize the application
        this.init();
    }

    /**
     * Initialize the chatbot application
     */
    init() {
        this.setupEventListeners();
        this.setupSpeechRecognition();
        this.setupEmojiPicker();
        this.addInitialMessage();
        this.autoResizeTextarea();
    }

    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Mobile menu
        document.getElementById('mobile-menu-btn').addEventListener('click', () => {
            this.toggleSidebar();
        });

        document.getElementById('close-sidebar').addEventListener('click', () => {
            this.closeSidebar();
        });

        // New chat buttons
        document.getElementById('new-chat-btn').addEventListener('click', () => {
            this.startNewChat();
        });

        document.getElementById('header-new-chat').addEventListener('click', () => {
            this.startNewChat();
        });

        // Message input
        const messageInput = document.getElementById('message-input');
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
        });

        // Control buttons
        document.getElementById('send-btn').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('voice-btn').addEventListener('click', () => {
            this.toggleVoiceRecording();
        });

        document.getElementById('emoji-btn').addEventListener('click', () => {
            this.toggleEmojiPicker();
        });

        document.getElementById('file-btn').addEventListener('click', () => {
            document.getElementById('file-input').click();
        });

        document.getElementById('image-btn').addEventListener('click', () => {
            document.getElementById('image-input').click();
        });

        // File uploads
        document.getElementById('file-input').addEventListener('change', (e) => {
            this.handleFileUpload(e);
        });

        document.getElementById('image-input').addEventListener('change', (e) => {
            this.handleImageUpload(e);
        });

        // Close emoji picker when clicking outside
        document.addEventListener('click', (e) => {
            const emojiPicker = document.getElementById('emoji-picker');
            const emojiBtn = document.getElementById('emoji-btn');
            
            if (!emojiPicker.contains(e.target) && !emojiBtn.contains(e.target)) {
                emojiPicker.classList.add('hidden');
            }
        });

        // Close sidebar when clicking outside (mobile)
        document.addEventListener('click', (e) => {
            const sidebar = document.getElementById('sidebar');
            const mobileBtn = document.getElementById('mobile-menu-btn');
            
            if (window.innerWidth <= 768 && sidebar.classList.contains('open') && 
                !sidebar.contains(e.target) && !mobileBtn.contains(e.target)) {
                this.closeSidebar();
            }
        });
    }

    /**
     * Setup speech recognition
     */
    setupSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('message-input').value = transcript;
                this.autoResizeTextarea();
                this.stopRecording();
            };

            this.recognition.onerror = () => {
                this.stopRecording();
                this.showToast('Speech recognition error. Please try again.', 'error');
            };

            this.recognition.onend = () => {
                this.stopRecording();
            };
        }
    }

    /**
     * Setup emoji picker
     */
    setupEmojiPicker() {
        const emojiData = {
            smileys: ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏'],
            people: ['👋', '🤚', '🖐️', '✋', '🖖', '👌', '🤏', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉', '👆', '🖕', '👇', '☝️', '👍', '👎', '👊', '✊', '🤛', '🤜', '👏', '🙌', '👐', '🤲', '🤝', '🙏', '✍️', '💅'],
            nature: ['🌟', '⭐', '🌙', '☀️', '⛅', '🌤️', '⛈️', '🌧️', '❄️', '☃️', '⛄', '🌈', '🔥', '💧', '🌊', '🎄', '🌲', '🌳', '🌴', '🌱', '🌿', '🍀', '🎍', '🎋', '🍃', '🍂', '🍁', '🌾', '🌺', '🌻', '🌹', '🥀'],
            objects: ['⚡', '💫', '✨', '💥', '💢', '💨', '💦', '💤', '🎵', '🎶', '🔔', '🔕', '📢', '📣', '📯', '🔈', '🔉', '🔊', '📱', '📞', '☎️', '📟', '📠', '🔋', '🔌', '💻', '🖥️', '🖨️', '⌨️', '🖱️', '🖲️', '💽']
        };

        const emojiGrid = document.getElementById('emoji-grid');
        const categoryButtons = document.querySelectorAll('.emoji-category');

        // Set up category switching
        categoryButtons.forEach(button => {
            button.addEventListener('click', () => {
                categoryButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                this.renderEmojis(button.dataset.category, emojiData);
            });
        });

        // Initial render
        this.renderEmojis('smileys', emojiData);
    }

    /**
     * Render emojis for a specific category
     */
    renderEmojis(category, emojiData) {
        const emojiGrid = document.getElementById('emoji-grid');
        emojiGrid.innerHTML = '';

        emojiData[category].forEach(emoji => {
            const emojiButton = document.createElement('button');
            emojiButton.className = 'emoji-item';
            emojiButton.textContent = emoji;
            emojiButton.addEventListener('click', () => {
                this.insertEmoji(emoji);
            });
            emojiGrid.appendChild(emojiButton);
        });
    }

    /**
     * Insert emoji into message input
     */
    insertEmoji(emoji) {
        const messageInput = document.getElementById('message-input');
        const cursorPos = messageInput.selectionStart;
        const textBefore = messageInput.value.substring(0, cursorPos);
        const textAfter = messageInput.value.substring(cursorPos);
        
        messageInput.value = textBefore + emoji + textAfter;
        messageInput.setSelectionRange(cursorPos + emoji.length, cursorPos + emoji.length);
        messageInput.focus();
        
        document.getElementById('emoji-picker').classList.add('hidden');
        this.autoResizeTextarea();
    }

    /**
     * Add initial welcome message
     */
    addInitialMessage() {
        const welcomeMessage = {
            id: this.currentMessageId++,
            type: 'bot',
            content: "Hello! I'm your AI assistant. How can I help you today?",
            timestamp: new Date()
        };
        
        this.messages.push(welcomeMessage);
        document.getElementById('initial-time').textContent = this.formatTime(welcomeMessage.timestamp);
    }

    /**
     * Send a message
     */
    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        const content = messageInput.value.trim();
        
        if (!content || this.isLoading) return;

        // Create user message
        const userMessage = {
            id: this.currentMessageId++,
            type: 'user',
            content: content,
            timestamp: new Date()
        };

        this.messages.push(userMessage);
        this.renderMessage(userMessage);
        
        // Clear input
        messageInput.value = '';
        this.autoResizeTextarea();
        
        // Show loading
        this.showLoadingMessage();
        this.isLoading = true;
        
        // Simulate AI response
        setTimeout(() => {
            const botMessage = {
                id: this.currentMessageId++,
                type: 'bot',
                content: this.generateAIResponse(content),
                timestamp: new Date()
            };
            
            this.messages.push(botMessage);
            this.hideLoadingMessage();
            this.renderMessage(botMessage);
            this.isLoading = false;
        }, 1500);
    }

    /**
     * Generate simulated AI response
     */
    generateAIResponse(userMessage) {
        const responses = [
            "That's an interesting question! Let me think about that for you.",
            "I understand what you're asking. Here's my perspective on that...",
            "Great question! Based on the information you've provided, I'd suggest...",
            "I'd be happy to help you with that. Here's what I think...",
            "That's a thoughtful inquiry. Let me provide you with a comprehensive answer.",
            "I can definitely assist you with that. Here's my response..."
        ];
        
        // Simple keyword-based responses
        if (userMessage.toLowerCase().includes('hello') || userMessage.toLowerCase().includes('hi')) {
            return "Hello there! It's great to meet you. How can I assist you today?";
        }
        
        if (userMessage.toLowerCase().includes('help')) {
            return "I'm here to help! You can ask me questions, upload images for analysis, or share files for discussion. What would you like assistance with?";
        }

        if (userMessage.toLowerCase().includes('image') || userMessage.toLowerCase().includes('picture')) {
            return "I can analyze images for you! Just use the image upload button to share a picture, and I'll help describe what I see or answer questions about it.";
        }

        if (userMessage.toLowerCase().includes('voice') || userMessage.toLowerCase().includes('speak')) {
            return "You can use the voice recording feature by clicking the microphone button. I'll convert your speech to text automatically!";
        }

        return responses[Math.floor(Math.random() * responses.length)] + " " + 
               "This is a demo response. In a real implementation, this would connect to an AI service like OpenAI, Claude, or Google's Gemini API.";
    }

    /**
     * Render a message in the chat
     */
    renderMessage(message) {
        const messagesContent = document.querySelector('.messages-content');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.type}-message message-appear`;
        
        const avatarHtml = message.type === 'bot' 
            ? '<div class="message-avatar"><i class="fas fa-robot"></i></div>'
            : '<div class="message-avatar"><i class="fas fa-user"></i></div>';
            
        let contentHtml = '';
        if (message.image) {
            contentHtml += `<img src="${message.image}" alt="Uploaded image" class="message-image">`;
        }
        if (message.file) {
            contentHtml += `<div class="message-file"><i class="fas fa-paperclip"></i><span>${message.file}</span></div>`;
        }
        contentHtml += `<p>${message.content}</p>`;
        contentHtml += `<span class="message-time">${this.formatTime(message.timestamp)}</span>`;

        if (message.type === 'user') {
            messageElement.innerHTML = `
                <div class="message-content">${contentHtml}</div>
                ${avatarHtml}
            `;
        } else {
            messageElement.innerHTML = `
                ${avatarHtml}
                <div class="message-content">${contentHtml}</div>
            `;
        }
        
        messagesContent.appendChild(messageElement);
        this.scrollToBottom();
    }

    /**
     * Show loading message
     */
    showLoadingMessage() {
        const messagesContent = document.querySelector('.messages-content');
        const loadingElement = document.createElement('div');
        loadingElement.className = 'loading-message message-appear';
        loadingElement.id = 'loading-message';
        
        loadingElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        messagesContent.appendChild(loadingElement);
        this.scrollToBottom();
    }

    /**
     * Hide loading message
     */
    hideLoadingMessage() {
        const loadingMessage = document.getElementById('loading-message');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }

    /**
     * Handle file upload
     */
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const userMessage = {
            id: this.currentMessageId++,
            type: 'user',
            content: `Uploaded file: ${file.name}`,
            file: file.name,
            timestamp: new Date()
        };

        this.messages.push(userMessage);
        this.renderMessage(userMessage);

        // Simulate AI response for file
        setTimeout(() => {
            const botMessage = {
                id: this.currentMessageId++,
                type: 'bot',
                content: `I've received your file "${file.name}". I can help you analyze, discuss, or extract information from this file. What would you like to know about it?`,
                timestamp: new Date()
            };
            
            this.messages.push(botMessage);
            this.renderMessage(botMessage);
        }, 1000);

        // Reset input
        event.target.value = '';
    }

    /**
     * Handle image upload
     */
    handleImageUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const userMessage = {
                id: this.currentMessageId++,
                type: 'user',
                content: 'Uploaded an image',
                image: e.target.result,
                timestamp: new Date()
            };

            this.messages.push(userMessage);
            this.renderMessage(userMessage);

            // Simulate AI response for image
            setTimeout(() => {
                const botMessage = {
                    id: this.currentMessageId++,
                    type: 'bot',
                    content: "I can see the image you've shared! I can help analyze its contents, describe what I see, or answer any questions you have about it. What would you like to know?",
                    timestamp: new Date()
                };
                
                this.messages.push(botMessage);
                this.renderMessage(botMessage);
            }, 1500);
        };
        
        reader.readAsDataURL(file);
        
        // Reset input
        event.target.value = '';
    }

    /**
     * Toggle voice recording
     */
    toggleVoiceRecording() {
        if (!this.recognition) {
            this.showToast('Speech recognition is not supported in your browser.', 'error');
            return;
        }

        if (this.isRecording) {
            this.recognition.stop();
        } else {
            this.recognition.start();
            this.startRecording();
        }
    }

    /**
     * Start recording
     */
    startRecording() {
        this.isRecording = true;
        const voiceBtn = document.getElementById('voice-btn');
        voiceBtn.classList.add('recording');
        voiceBtn.innerHTML = '<i class="fas fa-microphone-slash"></i>';
        this.showToast('Recording... Speak now!', 'success');
    }

    /**
     * Stop recording
     */
    stopRecording() {
        this.isRecording = false;
        const voiceBtn = document.getElementById('voice-btn');
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    }

    /**
     * Toggle emoji picker
     */
    toggleEmojiPicker() {
        const emojiPicker = document.getElementById('emoji-picker');
        emojiPicker.classList.toggle('hidden');
    }

    /**
     * Toggle sidebar (mobile)
     */
    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('open');
    }

    /**
     * Close sidebar
     */
    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.remove('open');
    }

    /**
     * Start new chat
     */
    startNewChat() {
        // Clear messages
        this.messages = [];
        this.currentMessageId = 1;
        
        // Clear chat display
        const messagesContent = document.querySelector('.messages-content');
        messagesContent.innerHTML = '';
        
        // Add initial message
        this.addInitialMessage();
        const welcomeMessage = this.messages[0];
        this.renderMessage(welcomeMessage);
        
        // Clear input
        document.getElementById('message-input').value = '';
        this.autoResizeTextarea();
        
        this.showToast('New chat started!', 'success');
    }

    /**
     * Auto-resize textarea
     */
    autoResizeTextarea() {
        const textarea = document.getElementById('message-input');
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        
        // Update send button state
        const sendBtn = document.getElementById('send-btn');
        sendBtn.disabled = !textarea.value.trim() || this.isLoading;
    }

    /**
     * Scroll to bottom of messages
     */
    scrollToBottom() {
        const messagesContainer = document.getElementById('messages-container');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    /**
     * Format timestamp
     */
    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        toastContainer.appendChild(toast);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

// Initialize the chatbot when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AIChatbot();
});

// Handle resize events
window.addEventListener('resize', () => {
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth > 768) {
        sidebar.classList.remove('open');
    }
});
// Handle resize events
window.addEventListener('resize', () => {
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth > 768) {
        sidebar.classList.remove('open');
    }
});