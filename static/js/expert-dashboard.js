document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.querySelector('.toggle-availability');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            fetch('/userauths/expert/toggle-availability/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update the status pill
                    const statusPill = document.querySelector('.status-pill');
                    statusPill.className = `status-pill status-${data.new_status}`;
                    const statusText = statusPill.querySelector('.status-text');
                    statusText.textContent = data.new_status.charAt(0).toUpperCase() + data.new_status.slice(1);
                    
                    // Show notification
                    showNotification(`Status updated to ${data.new_status}`);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Failed to update status', 'error');
            });
        });
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Helper function to show notifications
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}); 