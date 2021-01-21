var themeColor = '#1a2238';
var primaryColor = '#248e57';
var secondaryColor = '#fea739';

function hex2rgba(hex, opacity) {
    hex = hex.replace('#','');
    var r = parseInt(hex.substring(0,2), 16);
    var g = parseInt(hex.substring(2,4), 16);
    var b = parseInt(hex.substring(4,6), 16);
    return 'rgba('+r+','+g+','+b+','+opacity+')';
}

$('a.smooth-scroll').bind('click', function(event) {
    var link = $(this);
    $('html, body').stop().animate({
        scrollTop: $(link.attr('href')).offset().top - 100  // 70
    }, 500);
    event.preventDefault();
});

function comingSoon() {
    alert('This feature is not quite ready yet, but will be available soon.');
}

function doNothing() {
    // Nothing happens here...
}

$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip({
        animation: true
    });
});
