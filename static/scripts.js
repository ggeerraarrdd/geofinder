//
//
// Sources:
// https://developers.google.com/maps/documentation/javascript/adding-a-google-map
// https://stackoverflow.com/questions/47104164/call-function-initmap-with-parameters-in-gmaps-api
// https://stackoverflow.com/questions/44795264/add-double-quotes-to-string-which-is-stored-in-variable
//
//
// Initialize and add the map
let map;
let map_lat = parseFloat(document.getElementById('map').getAttribute("map-lat"));
let map_lng = parseFloat(document.getElementById('map').getAttribute("map-lng"));
let map_zoom = parseFloat(document.getElementById('map').getAttribute("map-zoom"));
let map_marker_title = parseFloat(document.getElementById('map').getAttribute("map-marker-title"));
let result_content = parseFloat(document.getElementById('map').getAttribute("result-content"));
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
    title: doubleQuote + map_marker_title + doubleQuote,
  });

  // Getting Lat/Lng from a Click Event
  // https://developers.google.com/maps/documentation/javascript/examples/event-click-latlng
  // Create the initial InfoWindow.
  let infoWindow = new google.maps.InfoWindow({
    content: "Click the house on the map!",
    position: position,
  });

  infoWindow.open(map);
  // Configure the click listener.
  map.addListener("click", (mapsMouseEvent) => {
    // Close the current InfoWindow.
    infoWindow.close();
    // Create content of new InfoWindow.
    const contentLat = mapsMouseEvent.latLng.lat();
    const contentLong = mapsMouseEvent.latLng.lng();
    const contentString = 
      '<form name="submit" action="/submit" method="post">' + 
      '<input type="hidden" name="answer-lat" class="hidden-field" value="' + contentLat + '"></input>' +
      '<input type="hidden" name="answer-long" class="hidden-field" value="' + contentLong + '"></input>' +
      '<button type="submit">Submit</button>' +
      '</form>';
    // Create a new InfoWindow.
    infoWindow = new google.maps.InfoWindow({
      position: mapsMouseEvent.latLng,
    });
    infoWindow.setContent(
      contentString, 
      // JSON.stringify(mapsMouseEvent.latLng.toJSON(), null, 2),
    );
    infoWindow.open(map);
  });


}


initMap();







