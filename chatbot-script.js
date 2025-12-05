/* document.addEventListener('DOMContentLoaded', () => {
    const chatBody = document.getElementById('chat-body');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const newChatBtn = document.querySelector('.new-chat-btn');
    const logoutBtn = document.querySelector('.logout-btn');
    const imageBtn = document.getElementById('image-btn');
    const documentBtn = document.getElementById('document-btn');
    const imageUpload = document.getElementById('image-upload');
    const documentUpload = document.getElementById('document-upload');

    // Function to add a message to the chat body
    function addMessage(text, sender) {
        // Hides the initial welcome message when a user starts chatting
        const initialMessage = document.querySelector('.initial-message');
        if (initialMessage) {
            initialMessage.style.display = 'none';
        }

        const messageContainer = document.createElement('div');
        messageContainer.classList.add('message-container', `${sender}-message-container`);
        
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(`${sender}-message`);
        messageDiv.textContent = text;
        messageContainer.appendChild(messageDiv);
        
        // This is the CRITICAL FIX: it appends the new message to the chat body
        // instead of overwriting its entire content.
        chatBody.appendChild(messageContainer);

        // Scrolls to the latest message
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // A simple function for a demo chatbot response (rule-based)
    function getBotResponse(userMessage) {
        const lowerCaseMessage = userMessage.toLowerCase();
        if (lowerCaseMessage.includes('hello') || lowerCaseMessage.includes('hi')) {
            return 'Hello there! How can I help you today?';
        } else if (lowerCaseMessage.includes('how are you')) {
            return "I'm just a bot, but I'm doing great! Thanks for asking.";
        } else if (lowerCaseMessage.includes('your name')) {
            return "I don't have a name. You can just call me a chatbot.";
        } else if (lowerCaseMessage.includes('enrollment')) {
            return "You can log in using your enrollment number and password on the main page.";
        } else if (lowerCaseMessage.includes('password')) {
            return "If you've lost your password, you can use the 'Lost Password?' link on the login page to recover it.";
        } else if (lowerCaseMessage.includes('ce-it information management system')) {
            return "The CE-IT Information Management System is designed to manage information for students and faculty.";
        } else {
            return "I am sorry, I can only respond to a few pre-programmed questions. Please try asking about the system or login process.";
        }
    }

    // Handles sending a message
    sendBtn.addEventListener('click', () => {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, 'user');
            userInput.value = '';
            userInput.style.height = 'auto';

            const botResponse = getBotResponse(message);

            // Using setTimeout to simulate a "thinking" delay
            setTimeout(() => {
                addMessage(botResponse, 'bot');
            }, 500); 
        }
    });

    // Adjusts textarea height dynamically
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = `${userInput.scrollHeight}px`;
    });

    // Handles Enter key for sending
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendBtn.click();
        }
    });

    // Voice recognition functionality
    if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        voiceBtn.addEventListener('click', () => {
            recognition.start();
            voiceBtn.style.color = 'red'; // Listening indicator
        });

        recognition.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            userInput.value = transcript;
            voiceBtn.style.color = '#5f6368'; // Reset color
            sendBtn.click();
        };

        recognition.onend = () => {
            voiceBtn.style.color = '#5f6368';
        };

        recognition.onerror = (e) => {
            console.error('Speech recognition error:', e.error);
            voiceBtn.style.color = '#5f6368';
        };
    } else {
        voiceBtn.style.display = 'none';
        console.warn('Speech recognition not supported.');
    }

    // Handles file upload button clicks
    imageBtn.addEventListener('click', () => imageUpload.click());
    documentBtn.addEventListener('click', () => documentUpload.click());

    // Handles the file upload change event (when a file is selected)
    imageUpload.addEventListener('change', () => {
        const file = imageUpload.files[0];
        if (file) {
            addMessage(`Image uploaded: ${file.name}`, 'user');
            setTimeout(() => {
                addMessage("I've received your image, but as a frontend-only bot, I can't process it.", 'bot');
            }, 500);
        }
    });

    documentUpload.addEventListener('change', () => {
        const file = documentUpload.files[0];
        if (file) {
            addMessage(`Document uploaded: ${file.name}`, 'user');
            setTimeout(() => {
                addMessage("I've received your document, but as a frontend-only bot, I can't process it.", 'bot');
            }, 500);
        }
    });

    // New Chat functionality
    newChatBtn.addEventListener('click', () => {
        chatBody.innerHTML = `
            <div class="initial-message">
                <h1>How can I help you today?</h1>
                <p>You can ask me questions about the CE-IT Information Management System.</p>
            </div>
        `;
    });

    // Log Out functionality
    logoutBtn.addEventListener('click', () => {
        window.location.href = 'index.html';
    });
});
*/
document.addEventListener('DOMContentLoaded', () => {
    const chatBody = document.getElementById('chat-body');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const newChatBtn = document.querySelector('.new-chat-btn');
    const logoutBtn = document.querySelector('.logout-btn');
    const imageBtn = document.getElementById('image-btn');
    const documentBtn = document.getElementById('document-btn');
    const imageUpload = document.getElementById('image-upload');
    const documentUpload = document.getElementById('document-upload');

    function addMessage(text, sender) {
        const initialMessage = document.querySelector('.initial-message');
        if (initialMessage) {
            initialMessage.style.display = 'none';
        }
        const messageContainer = document.createElement('div');
        messageContainer.classList.add('message-container', `${sender}-message-container`);
        const messageDiv = document.createElement('div');
        messageDiv.classList.add(`${sender}-message`);
        messageDiv.textContent = text;
        messageContainer.appendChild(messageDiv);
        chatBody.appendChild(messageContainer);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    sendBtn.addEventListener('click', async () => {
    const message = userInput.value.trim();
    if (message) {
        addMessage(message, 'user');
        userInput.value = '';
        userInput.style.height = 'auto';

        addMessage('Thinking...', 'bot');
        const thinkingMessage = chatBody.lastElementChild;

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            thinkingMessage.remove();
            addMessage(data.reply, 'bot');   // << FIXED

        } catch (error) {
            console.error('Error:', error);
            thinkingMessage.remove();
            addMessage('Sorry, something went wrong. Please check if the backend server is running.', 'bot');
        }
    }
});


    // Other event listeners (for new chat, logout, etc.) remain the same
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = `${userInput.scrollHeight}px`;
    });

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendBtn.click();
        }
    });

    newChatBtn.addEventListener('click', () => {
        chatBody.innerHTML = `
            <div class="initial-message">
                <h1>How can I help you today?</h1>
                <p>You can ask me questions about the CE-IT Information Management System.</p>
            </div>
        `;
    });

    logoutBtn.addEventListener('click', () => {
        window.location.href = 'index.html';
    });
});