// Messaging system JavaScript

$(document).ready(function() {
    // Auto-scroll to bottom of chat on page load
    scrollToBottom();
    
    // Auto-scroll on new message
    $('#messageForm').on('submit', function() {
        setTimeout(scrollToBottom, 100);
    });
    
    // Character counter for message input
    const messageInput = $('textarea[name="message"]');
    if (messageInput.length) {
        const counter = $('<small class="text-muted"></small>');
        messageInput.after(counter);
        
        messageInput.on('input', function() {
            const length = $(this).val().length;
            const minLength = 5;
            counter.text(`${length} characters (min: ${minLength})`);
            
            if (length >= minLength) {
                counter.removeClass('text-danger').addClass('text-success');
            } else {
                counter.removeClass('text-success').addClass('text-danger');
            }
        });
        
        messageInput.trigger('input');
    }
    
    // Prevent empty message submission
    $('#messageForm').on('submit', function(e) {
        const message = $('textarea[name="message"]').val().trim();
        if (message.length < 5) {
            e.preventDefault();
            alert('Message must be at least 5 characters long.');
            return false;
        }
    });
    
    // Auto-focus message input
    messageInput.focus();
});

function scrollToBottom() {
    const container = document.getElementById('messagesContainer');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

// Real-time message checking (optional - can be enabled)
function checkNewMessages() {
    const conversationId = $('#conversationId').val();
    if (!conversationId) return;
    
    $.get(`/messages/${conversationId}/new-messages/`, function(data) {
        if (data.new_messages && data.new_messages.length > 0) {
            // Append new messages to chat
            data.new_messages.forEach(function(msg) {
                appendMessage(msg);
            });
            scrollToBottom();
        }
    }).fail(function() {
        // Silent fail
    });
}

function appendMessage(messageData) {
    const isSent = messageData.is_sent;
    const bubble = $(`
        <div class="mb-3 ${isSent ? 'text-end' : ''}">
            <div class="d-inline-block message-bubble ${isSent ? 'message-sent' : 'message-received'}">
                <div class="message-text">${escapeHtml(messageData.message)}</div>
                <div class="message-time small text-muted mt-1">
                    ${messageData.sent_at}
                </div>
            </div>
        </div>
    `);
    
    $('#messagesContainer').append(bubble);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

