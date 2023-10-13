//
// GENERAL - ABOUT, HOWTO, HISTORY
//

// Initialize and add the map
let map;
let map_lat = parseFloat(document.getElementById('map').getAttribute("map-lat"));
let map_lng = parseFloat(document.getElementById('map').getAttribute("map-lng"));
let map_zoom = parseFloat(document.getElementById('map').getAttribute("map-zoom"));
let doubleQuote = ' " ';

async function initMap() {
  // The location to find
  const position = { lat: map_lat, lng: map_lng };
  // Request needed libraries.
  //@ts-ignore
  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerView } = await google.maps.importLibrary("marker");

  // The map, centered at location
  map = new Map(document.getElementById("map"), {
    zoom: map_zoom,
    center: position,
    mapId: "map_general",
    title: 0,
    tilt: 0,
    mapTypeId: 'satellite',
    disableDefaultUI: true,
  });

}


initMap();







