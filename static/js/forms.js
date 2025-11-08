// Form validation and enhancement

$(document).ready(function() {
    // Add Bootstrap validation classes
    $('form').addClass('needs-validation');
    
    // Custom form validation
    $('form').on('submit', function(e) {
        if (!this.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        $(this).addClass('was-validated');
    });
    
    // File upload preview
    $('input[type="file"]').on('change', function() {
        const input = this;
        const preview = $(this).data('preview');
        
        if (input.files && input.files[0] && preview) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $(`#${preview}`).attr('src', e.target.result).show();
            };
            reader.readAsDataURL(input.files[0]);
        }
        
        // Show filename
        const fileName = $(this).val().split('\\').pop();
        const label = $(this).next('.form-label');
        if (label.length) {
            label.text(fileName || 'Choose file');
        }
    });
    
    // Character counter for textareas
    $('textarea[maxlength]').each(function() {
        const textarea = $(this);
        const maxLength = textarea.attr('maxlength');
        const counter = $(`<div class="text-muted small mt-1"><span class="char-count">0</span>/${maxLength}</span></div>`);
        textarea.after(counter);
        
        textarea.on('input', function() {
            const length = $(this).val().length;
            counter.find('.char-count').text(length);
            
            if (length > maxLength * 0.9) {
                counter.addClass('text-warning');
            } else {
                counter.removeClass('text-warning');
            }
        });
        
        textarea.trigger('input');
    });
    
    // Auto-grow textareas
    $('textarea.auto-grow').on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Confirm before leaving page with unsaved changes
    let formChanged = false;
    $('form input, form textarea, form select').on('change', function() {
        formChanged = true;
    });
    
    $('form').on('submit', function() {
        formChanged = false;
    });
    
    $(window).on('beforeunload', function() {
        if (formChanged) {
            return 'You have unsaved changes. Are you sure you want to leave?';
        }
    });
    
    // Multi-select enhancement
    $('select[multiple]').each(function() {
        const select = $(this);
        const helpText = select.next('.form-text');
        
        select.on('change', function() {
            const count = $(this).val() ? $(this).val().length : 0;
            if (count > 0) {
                if (!helpText.find('.selection-count').length) {
                    helpText.append(` <span class="selection-count badge bg-primary">${count} selected</span>`);
                } else {
                    helpText.find('.selection-count').text(`${count} selected`);
                }
            } else {
                helpText.find('.selection-count').remove();
            }
        });
    });
    
    // Date input helper - prevent past dates for certain fields
    $('input[type="date"].future-only').on('change', function() {
        const today = new Date().toISOString().split('T')[0];
        const selected = $(this).val();
        
        if (selected < today) {
            $(this).val(today);
            alert('Please select a future date.');
        }
    });
    
    // Form submission with loading state
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        if (submitBtn.length) {
            const originalText = submitBtn.html();
            submitBtn.prop('disabled', true);
            submitBtn.html('<span class="spinner-border spinner-border-sm" role="status"></span> Processing...');
            
            // Re-enable after 5 seconds (safety)
            setTimeout(function() {
                submitBtn.prop('disabled', false);
                submitBtn.html(originalText);
            }, 5000);
        }
    });
});

// AJAX form submission helper
function submitFormAjax(formId, successCallback, errorCallback) {
    const form = $(`#${formId}`);
    const formData = new FormData(form[0]);
    
    $.ajax({
        url: form.attr('action') || window.location.href,
        type: form.attr('method') || 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (successCallback) successCallback(response);
        },
        error: function(xhr, status, error) {
            if (errorCallback) errorCallback(xhr, status, error);
        }
    });
}

// Export functions
window.formsModule = {
    submitFormAjax
};

