//
// GAME
//

// Initialize and add the map
let map;
let map_lat = parseFloat(document.getElementById('map').getAttribute("map-lat"));
let map_lng = parseFloat(document.getElementById('map').getAttribute("map-lng"));
let map_lat_offset = parseFloat(document.getElementById('map').getAttribute("map-lat-offset"));
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
    mapId: "DEMO_MAP_ID",
    mapTypeControl: false,
    fullscreenControl: false,
    title: 0,
    tilt: 0,
    mapTypeId: 'hybrid',
  });

  // The search area circle
  const locCircle = new google.maps.Circle({
    strokeColor: "#ffeddd",
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
  let infoWindow = new google.maps.InfoWindow({
    content: '<div class="infowindow-game">Search Area</div>',
    position: positionSearch,
  });

  infoWindow.open(map);
  // Configure the click listener.
  map.addListener("click", (mapsMouseEvent) => {
    // Close the current InfoWindow.
    infoWindow.close();
    // Create content of new InfoWindow.
    const contentLat = mapsMouseEvent.latLng.lat();
    const contentLong = mapsMouseEvent.latLng.lng();
    const contentCenter = map.getCenter();
    const contentZoom = map.getZoom();
    const contentString = 
      '<div class="infowindow-game">' + 
      '<form name="submit" action="/result" method="post">' + 
      '<input type="hidden" name="answer-lat" class="hidden-field" value="' + contentLat + '"></input>' +
      '<input type="hidden" name="answer-long" class="hidden-field" value="' + contentLong + '"></input>' +
      '<input type="hidden" name="answer-map-center" class="hidden-field" value="' + contentCenter + '"></input>' +
      '<input type="hidden" name="answer-map-zoom" class="hidden-field" value="' + contentZoom + '"></input>' +
      '<input type="hidden" name="page" class="hidden-field" value="game"></input>' +
      '<input type="hidden" name="goto" class="hidden-field" value="result"></input>' +
      '<button class="bttn bttn-small bttn-primary" type="submit">Submit</button>' +
      '</form>' +
      '</div>';
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







