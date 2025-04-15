const messagesDiv = document.getElementById('messages');
const questionInput = document.getElementById('questionInput');
const sendButton = document.getElementById('sendButton');

// Determine WebSocket protocol based on location protocol
const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
let websocket;

function connectWebSocket() {
    websocket = new WebSocket(wsUrl);

    websocket.onopen = (event) => {
        console.log("WebSocket connection established");
        addMessage("System", "Connected to the server.");
    };

    websocket.onmessage = (event) => {
        // Assuming the server sends plain text messages prefixed with type
        const message = event.data;
        console.log("Message from server: ", message);

        if (message.startsWith("Generated Query:")) {
            addMessage("Server", message);
        } else if (message.startsWith("Query Results:")) {
            addMessage("Server", message);
        } else if (message.startsWith("Final Answer:")) {
            addMessage("Server", `${message}`); // Bold the final answer
        } else {
            addMessage("Server", message);
        }
    };

    websocket.onclose = (event) => {
        console.log("WebSocket connection closed", event.reason);
        addMessage("System", "Connection closed. Attempting to reconnect...");
        // Simple reconnect logic
        setTimeout(connectWebSocket, 5000); // Try to reconnect every 5 seconds
    };

    websocket.onerror = (error) => {
        console.error("WebSocket Error: ", error);
        addMessage("System", "WebSocket error occurred.");
    };
}

function sendMessage() {
    const question = questionInput.value.trim();
    if (question && websocket && websocket.readyState === WebSocket.OPEN) {
        addMessage("You", question);
        websocket.send(question);
        questionInput.value = ''; // Clear input field
    } else if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        addMessage("System", "Not connected to the server. Please wait or refresh.");
    } else {
        addMessage("System", "Please enter a question.");
    }
}

// Function to escape HTML special characters
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Function to format message with line breaks and preserve URLs
function formatMessage(message) {
    // First escape HTML to prevent XSS and preserve special characters
    let escapedMessage = escapeHtml(message);
    
    // Replace newlines with <br> tags
    escapedMessage = escapedMessage.replace(/\n/g, '<br>');
    
    // Highlight URLs (optional)
    escapedMessage = escapedMessage.replace(
        /(https?:\/\/[^\s<]+)/g, 
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
    );
    
    return escapedMessage;
}

function addMessage(sender, message) {
    const messageElement = document.createElement('p');
    // Basic styling based on sender
    if (sender === "You") {
        messageElement.innerHTML = `<strong>${sender}:</strong> ${formatMessage(message)}`;
        messageElement.classList.add('text-primary');
    } else if (sender === "Server") {
        messageElement.innerHTML = `<i>${sender}:</i> <pre>${formatMessage(message)}</pre>`;
        messageElement.classList.add('text-success');
    } else { // System messages
        messageElement.innerHTML = `<i>${sender}:</i> ${formatMessage(message)}`;
        messageElement.classList.add('text-muted');
    }

    // Remove initial placeholder if it exists
    const placeholder = messagesDiv.querySelector('.text-muted');
    if (placeholder && placeholder.textContent === 'Ask a question below.') {
        messagesDiv.removeChild(placeholder);
    }

    messagesDiv.appendChild(messageElement);
    // Scroll to the bottom
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Event listeners
sendButton.addEventListener('click', sendMessage);
questionInput.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// Initial connection
connectWebSocket();
