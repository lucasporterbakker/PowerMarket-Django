// Source:
// http://zurb.com/forrst/posts/Django_admin_ajax_search_filter-IlN

$(document).ready(function($) {
    $('#changelist-search input[type=submit]').hide();
    // $('label[for=searchbar]').html('Search:');
    $('#searchbar').keyup(function(e) {
        if (e.keyCode === 27) {
            if (!$(this).val()) {
                return;
            }
            $(this).val('');
        }
        $('#changelist-form').load(window.location.pathname + '?q=' + $(this).val() + ' #changelist-form');
    }).focus();
});