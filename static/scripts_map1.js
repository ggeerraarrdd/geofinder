//
// INDEX
//

// LEAVE THIS COPY HERE
//
// Sources:
// https://developers.google.com/maps/documentation/javascript/adding-a-google-map
// https://stackoverflow.com/questions/47104164/call-function-initmap-with-parameters-in-gmaps-api
// https://stackoverflow.com/questions/44795264/add-double-quotes-to-string-which-is-stored-in-variable
// 
// All about InfoWindows
// https://developers.google.com/maps/documentation/javascript/infowindows
//
// Getting Lat/Lng from a Click Event
// https://developers.google.com/maps/documentation/javascript/examples/event-click-latlng
//

// Initialize and add the map
let map;
let map_lat = parseFloat(document.getElementById('map').getAttribute("map-lat"));
let map_lng = parseFloat(document.getElementById('map').getAttribute("map-lng"));
let map_zoom = parseFloat(document.getElementById('map').getAttribute("map-zoom"));
let map_marker_title = document.getElementById('map').getAttribute("map-marker-title");
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
    mapId: "DEMO_MAP_ID",
    mapTypeControl: false,
    fullscreenControl: false,
    title: 0,
    tilt: 0,
    mapTypeId: 'satellite',
  });

  // The marker, positioned at location
  const marker = new AdvancedMarkerView({
    map: map,
    position: position,
    title: map_marker_title,
  });

  const contentIndex = 
    '<div class="infowindow-index">' +
    '<form name="submit" action="/game" method="post">' + 
      '<input type="hidden" name="current-game-id" class="hidden-field" value="0"></input>' +
      '<input type="hidden" name="page" class="hidden-field" value="index"></input>' +
      '<input type="hidden" name="goto" class="hidden-field" value="game"></input>' +
      '<input type="hidden" name="try-again" class="hidden-field" value="0"></input>' +
      '<button class="btn btn-primary" type="submit">Start Game</button>' +
    '</form>'
    '</div>';

  let infoWindow = new google.maps.InfoWindow({
    content: contentIndex,
    position: position,
  });

  marker.addListener("click", () => {
    infoWindow.open({
      anchor: position,
      map,
    });
  });

  infoWindow.open(map);
  

}


initMap();







