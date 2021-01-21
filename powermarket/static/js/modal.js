/*
 *   AJAX modals
 *
 *   Author: Toni Engelhardt
 *   Created: Oct 9, 2016
 *   Last modified: Oct 9, 2016
 */

/**
 * Render modal dialog with loading animation.
 */
function modal_loading_animation() {
    html = '<div class="modal-dialog modal-sm"><div class="modal-content"><div class="text-center"><br/><br/>' +
        '<span class="glyphicon glyphicon-refresh glyphicon-refresh-animate"></span>&nbsp;&nbsp;Working...' +
        '<br/><br/><br/></div></div></div>';
    return html
}

/**
 * Render JSON response into a modal and handle form actions if present.
 * @param data: JSON response, contains either object pk or form errors depending on form_valid().
 * @param url: request URL.
 */
function handleModalData(data, url) {

    var $modal = $('#ajaxModal');
    $modal.html(data.html);

    // Activate select2 for the case it is needed.
    // Can this be added to the modal html itself?
    // $('.select2').select2();

    // Intercept submit, handle JSON response.
    $('form', $modal).on('submit', function (e) {
        e.preventDefault();

        // console.log($(this));
        // console.log($(this).serializeArray());
        /*
        $.post(url, $(this).serializeArray(), function (data) {
            if (!data['valid']) {
                // Reopen the modal with validation errors
                handleModalData(data, url);
            } else {
                $modal.empty();
                $modal.modal('hide');
                if (data['success_url']) {
                    // Redirect if a success_url was given.
                    if (data['success_url'] == '#') {
                        // Reload page if success_url is '#'.
                        location.reload();
                    }
                    else {
                        window.location.href = data['success_url'];
                    }
                }
            }
        });*/

        $.ajax({
            url: url,
            type: $(this).attr("method"),
            dataType: "JSON",
            data: new FormData(this),
            processData: false,
            contentType: false,
            success: function (data, status)
            {
                if (!data['valid']) {
                    // Reopen the modal with validation errors
                    handleModalData(data, url);
                } else {
                    $modal.empty();
                    $modal.modal('hide');
                    if (data['success_url']) {
                        // Redirect if a success_url was given.
                        if (data['success_url'] == '#') {
                            // Reload page if success_url is '#'.
                            location.reload();
                        }
                        else {
                            window.location.href = data['success_url'];
                        }
                    }
                }
            },
            error: function (xhr, desc, err)
            {
                console.log('AJAX error in modal.js.');
            }
        });
    });

    // Not sure if this is needed..
    /* $('a[data-dismiss="modal"]', $modal).on('click', function() {
        if(callback !== undefined){
            callback(null);
        }
    });*/

    $modal.modal('show');
}

/**
 * Create modal and request JSON response.
 * Use with Django ModalResponseMixin and Create-, Update- or DeleteView.
 * @param url: request URL.
 */
function createModal(url) {

    $('#ajaxModal').remove();  // Remove old modal in case one exists.

    var modal = $('<div class="modal" id="ajaxModal"></div>');
    $('body').append(modal);

    modal.modal({
        backdrop: 'static',
        keyboard: false
    });
    modal.html(modal_loading_animation());  // Display animation while loading.

    $.getJSON(url, function (data) {
        handleModalData(data, url);
    });
}
