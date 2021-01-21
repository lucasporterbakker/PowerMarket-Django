var $navbarDefault = $('.navbar-default');
var $navbarBrand = $navbarDefault.find('.navbar-brand');
var $navbarLinks = $navbarDefault.find('.navbar-nav > li > a');
var themeColor = "#1a2238";

$(window).on('load scroll resize', function(){
    if ($(document).scrollTop() < 50 && $(window).width() > 767) {
        $navbarDefault.addClass('hide-box-shadow');
        $navbarDefault.css('background-color', 'transparent');
        $navbarBrand.css('color', 'white');
        $navbarLinks.css('color', themeColor);
    } else {
        $navbarDefault.removeClass('hide-box-shadow');
        $navbarDefault.css('background-color', themeColor);
        $navbarBrand.css('color', 'inherit');
        $navbarLinks.css('color', 'inherit');
        $navbarDefault.css('box-shadow', '0 4px 8px rgba(0,0,0,0.4)');
    }
});

$('.nav a').click(function() {
    var $navbarToggle = $('.navbar-toggle');
    if($navbarToggle.css('display') != 'none') {
        $navbarToggle.trigger( "click" );
    }
});

var locationAutocomplete;
var componentForm = {
    route: 'long_name',
    street_number: 'short_name',
    locality: 'long_name',
    administrative_area_level_1: 'short_name',
    administrative_area_level_2: 'short_name',
    country: 'long_name',
    postal_code: 'short_name'
};

function initMapsAutocomplete() {
    var input = document.getElementById('id_address');
    input.onfocus = geolocateAutocomplete;
    locationAutocomplete = new google.maps.places.Autocomplete(input);
    locationAutocomplete.addListener('place_changed', populateFormLocationElements);
}


function populateFormLocationElements(callback) {
    var place = locationAutocomplete.getPlace();
    if (place) {
        if (place.address_components) {
            for (var i = 0; i < place.address_components.length; i++) {
                var addressType = place.address_components[i].types[0];
                if (componentForm[addressType]) {
                    var el = document.getElementById('id_' + addressType);
                    if (el){
                        el.value = place.address_components[i][componentForm[addressType]];
                    }
                }
            }
            document.getElementById('id_lat').value = place.geometry.location.lat();
            document.getElementById('id_lng').value = place.geometry.location.lng();
        }
    }
    if (typeof callback == 'function') callback();
}

function geolocateAutocomplete() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var geolocation = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            var circle = new google.maps.Circle({
                center: geolocation,
                radius: position.coords.accuracy
            });
            locationAutocomplete.setBounds(circle.getBounds());
        });
    }
}

function submitForm() {
    console.log('submit form');
    populateFormLocationElements(finalizeSubmit);
}

function finalizeSubmit() {
    $("#address-form").submit();
}

google.maps.event.addDomListener(window, 'load', initMapsAutocomplete);

$(document).ready(function() {
    $('#id_address').focus();

    // Avoid submit on enter (important to populate location components).
    $(window).keydown(function(event){
        if(event.keyCode === 13) {

            event.preventDefault();
            return false;
        }
    });
});

