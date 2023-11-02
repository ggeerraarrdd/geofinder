//
// REVIEW
//

// Initialize and add the map
let map;
let map_lat = parseFloat(document.getElementById('map').getAttribute("map-lat"));
let map_lng = parseFloat(document.getElementById('map').getAttribute("map-lng"));
let map_lat_offset = parseFloat(document.getElementById('map').getAttribute("map-lat-offset"));
let map_zoom = parseFloat(document.getElementById('map').getAttribute("map-zoom"));
let locations_right = document.getElementById('map').getAttribute("locations-right");
let locations_wrong = document.getElementById('map').getAttribute("locations-wrong");
let locations_none= document.getElementById('map').getAttribute("locations-none");
let locations_quit = document.getElementById('map').getAttribute("locations-quit");
let doubleQuote = ' " ';

async function initMap() {
    // The location to find
    const position = { lat: map_lat, lng: map_lng };

    // Request needed libraries.
    //@ts-ignore
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");

    // The map, centered at location
    map = new Map(document.getElementById("map"), {
        zoom: map_zoom,
        center: position,
        mapId: "DEMO_MAP_ID",
        mapTypeControl: false,
        fullscreenControl: false,
        title: 0,
        tilt: 0,
        mapTypeId: 'satellite',
    });

    // The search area circle
    const locCircle = new google.maps.Circle({
        strokeColor: "#FFEEDD",
        strokeOpacity: 0.9,
        strokeWeight: 4,
        fillColor: "#FF0000",
        fillOpacity: 0,
        map,
        center: position,
        radius: 200,
        clickable: false,
    });

    const positionSearch = { lat: map_lat_offset, lng: map_lng };

    // Create the initial InfoWindow.
    /* let infoWindow = new google.maps.InfoWindow({
        content: '<div class="infowindow-game">Search Area</div>',
        position: positionSearch,
    });

    infoWindow.open(map); */

    // Add markers

    // Attempted locations - correct
    const right = locations_right.replace(/'/g, '"');
    const right_json = JSON.parse(right);

    for (var i = 0; i < right_json.length; i++) {
        var loc = right_json[i];
        var gameLat = parseFloat(Object.values(loc)[0]);
        var gameLng = parseFloat(Object.values(loc)[1]);
        
        const pin = new PinElement({
            glyphColor: "yellow",
            scale: 1.5,
        });

        // Use the gameLat and gameLng values to create a marker or perform other actions
        const marker = new AdvancedMarkerElement({
            map: map,
            position: { lat: parseFloat(gameLat), lng: parseFloat(gameLng) },
            content: pin.element,
        });
    }

    // Attempted locations - wrong
    const wrong = locations_wrong.replace(/'/g, '"');
    const wrong_json = JSON.parse(wrong);

    for (var i = 0; i < wrong_json.length; i++) {
        var loc = wrong_json[i];
        var gameLat = parseFloat(Object.values(loc)[0]);
        var gameLng = parseFloat(Object.values(loc)[1]);
        
        const pin = new PinElement({
            background: "#D95040",
            glyphColor: "#D95040",
            scale: 1,
        });

        // Use the gameLat and gameLng values to create a marker or perform other actions
        const marker = new AdvancedMarkerElement({
            map: map,
            position: { lat: parseFloat(gameLat), lng: parseFloat(gameLng) },
            content: pin.element,
        });
    }

    // Attempted locations - none
    const none = locations_none.replace(/'/g, '"');
    const none_json = JSON.parse(none);

    for (var i = 0; i < none_json.length; i++) {
        var loc = none_json[i];
        var gameLat = parseFloat(Object.values(loc)[0]);
        var gameLng = parseFloat(Object.values(loc)[1]);
        
        const pin = new PinElement({
            background: "white",
            glyphColor: "white",
            borderColor: "gray",
            scale: 1,
        });

        // Use the gameLat and gameLng values to create a marker or perform other actions
        const marker = new AdvancedMarkerElement({
            map: map,
            position: { lat: parseFloat(gameLat), lng: parseFloat(gameLng) },
            content: pin.element,
        });
    }

    // Attempted locations - quit
    const quit = locations_quit.replace(/'/g, '"');
    const quit_json = JSON.parse(quit);

    for (var i = 0; i < quit_json.length; i++) {
        var loc = quit_json[i];
        var gameLat = parseFloat(Object.values(loc)[0]);
        var gameLng = parseFloat(Object.values(loc)[1]);
        
        const pin = new PinElement({
            glyphColor: "black",
            scale: 1.4,
        });

        // Use the gameLat and gameLng values to create a marker or perform other actions
        const marker = new AdvancedMarkerElement({
            map: map,
            position: { lat: parseFloat(gameLat), lng: parseFloat(gameLng) },
            content: pin.element,
        });
    }
    

}


initMap();







