document.addEventListener('DOMContentLoaded', function() {
    // Initialize any necessary variables
    let currentComplaint = null;
    
    // Set up event listeners
    setupEventListeners();
});

function setupEventListeners() {
    // Comment form submission
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addComment();
        });
    }
    
    // Close modal when clicking outside
    const modal = document.getElementById('comment-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeCommentModal();
            }
        });
    }
    
    // Like form submissions
    document.querySelectorAll('.like-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const form = this;
            const url = form.action;
            const formData = new FormData(form);
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const likeBtn = form.querySelector('.action-btn');
                    const likeCount = form.querySelector('.like-count');
                    
                    likeBtn.classList.toggle('active', data.liked);
                    likeCount.textContent = data.likes_count;
                    
                    showToast(
                        data.liked ? 'Post liked!' : 'Like removed',
                        data.liked ? 'Thanks for your engagement' : '',
                        'success'
                    );
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error', 'Failed to update like', 'error');
            });
        });
    });
}
// Open comment modal with HTMX
function openCommentModal(postId) {
    // Set up modal content
    const modal = document.getElementById('comment-modal');
    const commentsList = document.getElementById('comments-list');
    const formContainer = document.getElementById('comment-form-container');
    
    // Update HTMX attributes for dynamic loading
    commentsList.setAttribute('hx-get', `/post/${postId}/comments/`);
    formContainer.innerHTML = `
        <div hx-get="/post/${postId}/comments/form/" 
             hx-trigger="load" 
             hx-target="this" 
             hx-swap="innerHTML">
        </div>
    `;
    
    // Show modal
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';

    
    commentsList.setAttribute('hx-get', `/post/${postId}/comments/`);
    formContainer.setAttribute('hx-get', `/post/${postId}/comments/form/`);
    
    // Trigger HTMX load
    htmx.trigger(document.body, 'loadComments');
    
    // Store current post ID in modal for reference
    modal.dataset.postId = postId;
    
    // Trigger HTMX load
    htmx.process(commentsList);
    htmx.process(formContainer);
}

// Close modal
function closeCommentModal() {
    const modal = document.getElementById('comment-modal');
    modal.classList.remove('show');
    document.body.style.overflow = '';
}

// Handle successful comment submission
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'comments-list') {
        // Clear the textarea after successful comment
        const textarea = document.querySelector('#comment-form textarea');
        if (textarea) textarea.value = '';
        
        // Scroll to the new comment
        const commentsList = event.detail.target;
        commentsList.scrollTop = 0;
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Close modal when clicking outside
    document.getElementById('comment-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeCommentModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeCommentModal();
        }
    });
});
// 
// function closeCommentModal() {
//     document.getElementById('comment-modal').classList.remove('show');
//     document.getElementById('comment-input').value = '';
//     currentComplaint = null;
// }

function addComment() {
    const input = document.getElementById('comment-input');
    const text = input.value.trim();
    
    if (!text) {
        showToast('Error', 'Please enter a comment', 'error');
        return;
    }

    if (!currentComplaint) return;

    // In a real implementation, you would submit this to the server
    const form = document.getElementById('comment-form');
    const formData = new FormData(form);
    formData.append('post_id', currentComplaint);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Clear the input
            input.value = '';
            
            // Update the comment count on the post card
            const commentCount = document.querySelector(`.complaint-card[data-post-id="${currentComplaint}"] .comment-count`);
            if (commentCount) {
                commentCount.textContent = data.comments_count;
            }
            
            // Show success message
            showToast('Comment posted!', 'Your comment has been added successfully', 'success');
            
            // Refresh the comments list
            // In a real app, you would append the new comment to the list
            const commentsList = document.getElementById('comments-list');
            if (commentsList.querySelector('div > p')) {
                commentsList.innerHTML = '';
            }
            
            // Create a new comment element
            const newComment = document.createElement('div');
            newComment.className = 'comment';
            newComment.innerHTML = `
                <div class="comment-avatar">
                    ${data.avatar_html || `<div class="avatar-initial">${data.username_initial}</div>`}
                </div>
                <div class="comment-content">
                    <div class="comment-header">
                        <span class="comment-user">${data.username}</span>
                        <span class="comment-time">Just now</span>
                    </div>
                    <div class="comment-text">${text}</div>
                </div>
            `;
            
            // Add the new comment at the top
            commentsList.prepend(newComment);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error', 'Failed to post comment', 'error');
    });
}


function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert("📋 Link copied to clipboard!");
    }).catch(function(err) {
        console.error("Failed to copy: ", err);
    });
}



function showToast(title, message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastTitle = toast.querySelector('.toast-title');
    const toastMessage = toast.querySelector('.toast-message');
    const toastIcon = toast.querySelector('.toast-icon');
    
    // Set content
    toastTitle.textContent = title;
    toastMessage.textContent = message;
    
    // Set icon based on type
    let icon = '';
    if (type === 'success') {
        icon = '✓';
        toast.className = 'toast success';
    } else {
        icon = '⚠';
        toast.className = 'toast error';
    }
    toastIcon.textContent = icon;
    
    // Show toast
    toast.classList.add('show');
    
    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && document.getElementById('comment-modal').classList.contains('show')) {
        closeCommentModal();    
    }
    
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const modal = document.getElementById('comment-modal');
        if (modal.classList.contains('show')) {
            addComment();
        }
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Add click animation to like buttons
    document.body.addEventListener('click', function(e) {
        if (e.target.closest('.like-btn')) {
            const btn = e.target.closest('.like-btn');
            
            // Add temporary class for visual feedback
            btn.classList.add('clicked');
            setTimeout(() => {
                btn.classList.remove('clicked');
            }, 300);
        }
    });

    // Handle successful like/unlike
     document.body.addEventListener('htmx:afterSwap', function(event) {
        if (event.detail.target.classList.contains('complaint-card')) {
            const likeBtn = event.detail.target.querySelector('.like-btn');
            if (likeBtn) {
                // Trigger animation
                likeBtn.classList.add('animate-pulse');
                setTimeout(() => {
                    likeBtn.classList.remove('animate-pulse');
                }, 500);
            }
        }
    });
});