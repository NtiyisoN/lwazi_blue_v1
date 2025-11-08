// Search and filter functionality

$(document).ready(function() {
    // Live search with debounce
    const searchInput = $('input[name="query"]');
    if (searchInput.length) {
        const debouncedSearch = lwazi.debounce(function() {
            const form = searchInput.closest('form');
            if (form.length) {
                // Auto-submit form on typing (optional, can be disabled)
                // form.submit();
            }
        }, 500);
        
        searchInput.on('input', debouncedSearch);
    }
    
    // Filter change auto-submit (optional)
    $('.auto-submit-filter').on('change', function() {
        $(this).closest('form').submit();
    });
    
    // Clear all filters
    $('#clearFilters').on('click', function(e) {
        e.preventDefault();
        const form = $(this).closest('form');
        form.find('input, select').val('');
        form.find('input[type="checkbox"]').prop('checked', false);
        window.location.href = window.location.pathname;
    });
    
    // Advanced search toggle
    $('#toggleAdvancedSearch').on('click', function(e) {
        e.preventDefault();
        $('#advancedSearchPanel').slideToggle(300);
        $(this).find('i').toggleClass('bi-chevron-down bi-chevron-up');
    });
    
    // Search suggestions (for future implementation)
    const searchSuggestions = $('#searchSuggestions');
    if (searchSuggestions.length) {
        searchInput.on('input', function() {
            const query = $(this).val();
            if (query.length >= 3) {
                // AJAX call to get suggestions
                $.get('/api/search-suggestions/', { q: query }, function(data) {
                    displaySuggestions(data.suggestions);
                }).fail(function() {
                    // Silent fail
                });
            } else {
                searchSuggestions.hide();
            }
        });
    }
});

function displaySuggestions(suggestions) {
    const container = $('#searchSuggestions');
    container.empty();
    
    if (suggestions && suggestions.length > 0) {
        suggestions.forEach(function(suggestion) {
            const item = $(`
                <a href="${suggestion.url}" class="list-group-item list-group-item-action">
                    ${suggestion.title}
                    <br><small class="text-muted">${suggestion.description}</small>
                </a>
            `);
            container.append(item);
        });
        container.show();
    } else {
        container.hide();
    }
}

// Filter count display
function updateFilterCount() {
    const activeFilters = $('form .form-select, form .form-control').filter(function() {
        return $(this).val() && $(this).val() !== '';
    }).length;
    
    const badge = $('#activeFilterCount');
    if (activeFilters > 0) {
        badge.text(activeFilters).show();
    } else {
        badge.hide();
    }
}

// Save search preferences to localStorage
function saveSearchPreferences() {
    const preferences = {
        query: $('input[name="query"]').val(),
        industry: $('select[name="industry"]').val(),
        province: $('select[name="province"]').val(),
    };
    
    localStorage.setItem('searchPreferences', JSON.stringify(preferences));
}

// Load search preferences from localStorage
function loadSearchPreferences() {
    const saved = localStorage.getItem('searchPreferences');
    if (saved) {
        const preferences = JSON.parse(saved);
        $('input[name="query"]').val(preferences.query || '');
        $('select[name="industry"]').val(preferences.industry || '');
        $('select[name="province"]').val(preferences.province || '');
    }
}

// Export functions
window.searchModule = {
    updateFilterCount,
    saveSearchPreferences,
    loadSearchPreferences
};

