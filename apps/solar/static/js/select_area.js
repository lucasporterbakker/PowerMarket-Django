var map;
var mpoly = [];
var selectedPolyIdx = 0;
var maxNumPolygons = 8;
var localStorageKey = "PM_AREA_INTRO_STATE";
var defaultState = { showSelectIntroScreen: true };
var polygonColors = ['#fea739', '#ff6347', '#7EB4FF', '#CF66FF'];
var $polygonControl0 = $('#polygon-control-0');
var $polygonAddBtn = $('#polygon-add-btn');

/**
 * Retrieve address from Google Maps API and set map location if available,
 * otherwise display 'not found' screen.
 * @param address: Address string.
 * @param map: map instance.
 */
function geocodeAddress(address, map) {
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({'address': address}, function (results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
            map.setCenter(results[0].geometry.location);
            map.setZoom(19);
        } else {
            // Show 'not found' screen if Google Maps doesn't return a valid map.
            $('.map-container').hide();
            $('.location-not-found').show();
        }
    });
}

/**
 * Polygon Object.
 */
function Polygon() {
    var path = new google.maps.MVCArray;
    var poly = new google.maps.Polygon({
        strokeWeight: 2,
        fillColor: polygonColors[0],
        strokeColor: polygonColors[0]
    });
    poly.setMap(map);
    poly.setPaths(new google.maps.MVCArray([path]));
    return {
        path: path,
        poly: poly,
        markers: []
    }
}

function addPolygon() {
    if (mpoly.length < maxNumPolygons) {
        mpoly.push(new Polygon());
        selectedPolyIdx = mpoly.length - 1;
        var $newPolygonControl = $polygonControl0.clone()
            .prop({id: "polygon-control-" + selectedPolyIdx})
            .attr("data-polygon-id", selectedPolyIdx);
        $newPolygonControl.find('.dropdown-toggle')
            .prop({id: "polygon-dropdown-" + selectedPolyIdx})
            .html(selectedPolyIdx + 1);
        $newPolygonControl.insertAfter("#polygon-control-" + (selectedPolyIdx - 1));
        initControlItemListeners(selectedPolyIdx);
        selectPolygon(selectedPolyIdx);
        if (mpoly.length == maxNumPolygons) $polygonAddBtn.hide();
    } else {
        // Max. X polygons.
        alert("Sorry, the maximum number of polygons is " + maxNumPolygons + ".");
    }
}

function initControlItemListeners(polyIdx) {
    var $el = $('#polygon-control-' + polyIdx);
    $el.find('.select-polygon').unbind().click(function() { selectPolygon(polyIdx); });
    $el.find('.clear-markers').unbind().click(function() { clearMarkers(polyIdx); });
    $el.find('.remove-polygon').unbind().click(function() { removePolygon(polyIdx); });
}

function selectPolygon(polyIdx) {
    selectedPolyIdx = polyIdx;
    var $polygonControls = $('.polygon-control');
    $polygonControls.removeClass('selected');
    $polygonControls.eq(selectedPolyIdx).addClass('selected');
}

function clearMarkers(polyIdx) {
    var poly = mpoly[polyIdx];
    $.each(poly.markers, function(i, marker){
        marker.setMap(null);
        poly.path.removeAt(polyIdx);
        poly.path.removeAt(0);
    });
    poly.markers = [];
    updateSelection();
    return true;
}

function removePolygon(polyIdx) {
    if (mpoly.length > 1) {
        clearMarkers(polyIdx);
        $('#polygon-control-' + polyIdx).remove();
        $.each(mpoly, function(idx) {
            if (idx > polyIdx) {
                var newIdx = idx - 1;
                var $polygonControl = $('#polygon-control-' + idx);
                $polygonControl
                    .prop({'id': 'polygon-control-' + newIdx})
                    .attr('data-polygon-id', newIdx);
                $polygonControl.find('.dropdown-toggle')
                    .prop({'id': 'polygon-dropdown-' + newIdx})
                    .html(idx);
                $polygonControl.find('.dropdown-menu')
                    .data('aria-labelledby', 'polygon-dropdown-' + newIdx);
                initControlItemListeners(newIdx);
            }
        });
        mpoly.splice(polyIdx, 1);
        var idxLast = mpoly.length;
        if (selectedPolyIdx != idxLast) selectPolygon(selectedPolyIdx);
        else selectPolygon(selectedPolyIdx - 1);
        $polygonAddBtn.show();
    } else {
        alert("You can't remove the last polygon. Use 'Clear markers' to clear it.");
    }
}

function setColor(event) {
    // TODO...
}

/**
 * Add a point to the marker array.
 * @param event
 */
function addPoint(event) {
    var path = mpoly[selectedPolyIdx].path;
    path.insertAt(path.length, event.latLng);
    var marker = new google.maps.Marker({
        position: event.latLng,
        map: map,
        draggable: true,
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 5
        }
    });
    marker.setTitle("Polygon " + selectedPolyIdx + " #" + path.length);
    var markers = mpoly[selectedPolyIdx].markers;
    markers.push(marker);
    // EventListener to remove marker.
    google.maps.event.addListener(marker, 'click', function () {
        marker.setMap(null);
        for (var i = 0, I = markers.length; i < I && markers[i] != marker; ++i);
        markers.splice(i, 1);
        path.removeAt(i);
        updateSelection();
    });
    // EventListener to drag marker.
    google.maps.event.addListener(marker, 'drag', function () {
        for (var i = 0, I = markers.length; i < I && markers[i] != marker; ++i);
        mpoly[selectedPolyIdx].path.setAt(i, marker.getPosition());
        updateSelection();
    });
    // TODO: handle clicks on polygons.
    updateSelection();
}

/**
 * Computes area of path and updates form field.
 */
function updateSelection() {

    // TODO:
    // Find better solution, this does not take overlap into account.

    var area = 0;
    $.each(mpoly, function(idx, polygon) {
        area += google.maps.geometry.spherical.computeArea(polygon.poly.getPath());
    });
    area = Math.round((area + 0.00001) * 100) / 100;
    $('#id_selected_area').val(area);
    // $('#marker-counter').val("[ 1 ] : " + mpoly[polyIdx].markers.length);
}

function constructMpolyString() {
    var mpolyLen = mpoly.length;
    var validPolygons = 0;
    var mpolyStr = 'MULTIPOLYGON(';
    $.each(mpoly, function(idx, poly){
        // Basic Validation.
        if (poly.markers.length < 3) {
            alert('Please draw an area to estimate the solar potential of');
            return false;
        }
        var poly_str = '((';
        $.each(poly.markers, function(idx, marker) {
            var pos = marker.getPosition();
            poly_str += pos.lat() + ' ' + pos.lng() + ', ';
        });
        // Append the first marker again at the end to create a closed polygon.
        var first_pos = poly.markers[0].getPosition();
        poly_str += first_pos.lat() + ' ' + first_pos.lng() + '))';
        mpolyStr += poly_str;
        if (idx != mpolyLen - 1) {
            mpolyStr += ', ';
        }
        validPolygons++;
    });
    if (validPolygons == mpolyLen) {
        mpolyStr += ')';
        return mpolyStr
    }
    else return null;
}

function submitForm() {
    var mpolyStr = constructMpolyString();
    if (mpolyStr) {
        $('#id_mpoly').val(mpolyStr);
        $('#select-area-form').submit();
        return true;
    }
    else return false;
}


$(document).ready(function() {
    var savedState = localStorage.getItem(localStorageKey);
    var state = savedState ? JSON.parse(savedState) : defaultState;
    if (state.showSelectIntroScreen) {
        $('.intro-container').show();
    }
    $('#polygon-help-btn').on('click', function () {
        $('.intro-container').show();
    });
    $('#close-intro-btn').on('click', function() {
        $('.intro-container').hide();
        // Save state to local storage.
        state.showSelectIntroScreen = false;
        localStorage.setItem(localStorageKey, JSON.stringify(state));
    });
    $('#close-intro-btn2').on('click', function() {
        $('.intro-container').hide();
        // Save state to local storage.
        state.showSelectIntroScreen = false;
        localStorage.setItem(localStorageKey, JSON.stringify(state));
    });
    // Init map.
    map = new google.maps.Map(document.getElementById('map'), {
        mapTypeId: google.maps.MapTypeId.SATELLITE,
        tilt: 0,
        maxZoom: 20,
        draggableCursor: 'crosshair',
        fullscreenControl: false,
        mapTypeControl: false,
        streetViewControl: false,
        rotateControl: false,
        scrollwheel: true
    });

    // Init polygon.
    mpoly.push(new Polygon());
    // Init search box.
    var input = document.getElementById('pac-input');
    geocodeAddress(input.value, map);
    var searchBox = new google.maps.places.SearchBox(input);
    map.addListener('bounds_changed', function() {
        searchBox.setBounds(map.getBounds());
    });
    searchBox.addListener('places_changed', function() {
        var places = searchBox.getPlaces();
        if (places.length == 0) return;
        // For each place, get the icon, name and location.
        var bounds = new google.maps.LatLngBounds();
        places.forEach(function(place) {
            if (!place.geometry) {
                console.log("Returned place contains no geometry.");
                return;
            }
            if (place.geometry.viewport) {
                // Only geocodes have viewport.
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
        });
        map.fitBounds(bounds);

    });
    // Add EventListener for clicks.
    google.maps.event.addListener(map, 'click', addPoint);
    // Init polygon controls.
    initControlItemListeners(selectedPolyIdx);
    $polygonAddBtn.click(addPolygon);
});

