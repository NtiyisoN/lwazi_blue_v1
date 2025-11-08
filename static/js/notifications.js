// Notification handling JavaScript

$(document).ready(function() {
    // Mark notification as read via AJAX
    $('.mark-notification-read').on('click', function(e) {
        e.preventDefault();
        const notificationId = $(this).data('notification-id');
        const url = `/notifications/${notificationId}/mark-read/`;
        
        $.post(url, {
            csrfmiddlewaretoken: lwazi.getCookie('csrftoken')
        }, function(response) {
            if (response.success) {
                // Fade out the notification
                $(`#notification-${notificationId}`).fadeOut(300, function() {
                    $(this).remove();
                    // Update unread count
                    updateNotificationCount();
                });
            }
        });
    });
    
    // Mark all as read
    $('#markAllRead').on('click', function(e) {
        if (!confirm('Mark all notifications as read?')) {
            e.preventDefault();
        }
    });
    
    // Auto-refresh notification count every 30 seconds
    setInterval(updateNotificationCount, 30000);
});

function updateNotificationCount() {
    // Update notification badge in navbar
    $.get('/notifications/api/unread-count/', function(data) {
        const count = data.count;
        const badge = $('.notification-count-badge');
        
        if (count > 0) {
            badge.text(count).show();
        } else {
            badge.hide();
        }
    }).fail(function() {
        // Silent fail - don't interrupt user
    });
}

// Toast notification for new notifications (can be called from other scripts)
function showNotificationToast(title, message, link) {
    const toast = `
        <div class="toast align-items-center text-white bg-primary border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong><br>
                    ${message}
                    ${link ? `<br><a href="${link}" class="text-white">View</a>` : ''}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    $('#toastContainer').append(toast);
    const toastEl = $('#toastContainer .toast').last()[0];
    const bsToast = new bootstrap.Toast(toastEl);
    bsToast.show();
}

