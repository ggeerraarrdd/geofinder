//
// REGISTER
//

// Initialize and add the map
let map;
let map_lat = parseFloat(document.getElementById('map').getAttribute("map-lat"));
let map_lng = parseFloat(document.getElementById('map').getAttribute("map-lng"));
let map_zoom = parseFloat(document.getElementById('map').getAttribute("map-zoom"));
let map_marker_title = document.getElementById('map').getAttribute("map-marker-title");
let result_content = parseFloat(document.getElementById('map').getAttribute("result-content"));
let button_type = document.getElementById('map').getAttribute("button-type");
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

  // Content for Info Window on register.html
  const contentRegister = 
    '<div class=' + doubleQuote + 'infowindow-login">' + 
    'Explore the world<br>one building at a time!' +
    '</div>' +
    '<form action="/admin/users/add" method="post">' +
    '<div class="mb-3">' +
    '<input autocomplete="off" autofocus class="form-control form-control-sm mx-auto w-auto" id="username" name="username" placeholder="Username" type="text" maxlength="16">' +
    '</div>' +
    '<div class="mb-3">' +
    '<input class="form-control form-control-sm mx-auto w-auto" id="password" name="password" placeholder="Password" type="password">' +
    '</div>' +
    '<div class="mb-3">' +
    '<input class="form-control form-control-sm mx-auto w-auto" id="confirmation" name="confirmation" placeholder="Password (again)" type="password">' +
    '</div>' +
    '<div class="infowindow-login-button">' + 
    '<button class="bttn bttn-small ' + button_type + '" type="submit">Register</button>' +
    '<div>' +
    '</form>'
    ;

  // Add Info Window to map
  let infoWindow = new google.maps.InfoWindow({
    content: contentRegister,
    position: position,
  });

  // Add Info Window back if closed
  marker.addEventListener('gmp-click', () => {
    infoWindow.open({
      anchor: position,
      map,
    });
  });

  infoWindow.open(map);
  

}


initMap();







