//
// LOGIN
//

// Initialize and add the map
let map;
let map_lat = parseFloat(document.getElementById('map').getAttribute("map-lat"));
let map_lng = parseFloat(document.getElementById('map').getAttribute("map-lng"));
let map_zoom = parseFloat(document.getElementById('map').getAttribute("map-zoom"));
let map_marker_title = document.getElementById('map').getAttribute("map-marker-title");
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
    title: map_marker_title,
  });

  // Content for Info Window on login.html
  const contentLogin = 
    '<div class="infowindow-login">' + 
    'Explore the world<br>one house at a time!' +
    '</div>' +

    '<form action="/login" method="post">' +
      '<div class="mb-3">' +
          '<input autocomplete="off" autofocus class="form-control form-control-sm mx-auto w-auto" id="username" name="username" placeholder="Username" type="text">' +
      '</div>' +
      '<div class="mb-3">' +
          '<input class="form-control form-control-sm mx-auto w-auto" id="password" name="password" placeholder="Password" type="password">' +
      '</div>' +
      '<div class="infowindow-login-button">' +
          '<input type="hidden" name="page" class="hidden-field" value="login"></input>' +
          '<input type="hidden" name="goto" class="hidden-field" value="index"></input>' +
          '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' +
          '<input type="hidden" name="bttn" class="hidden-field" value="login"></input>' +
          '<button class="bttn bttn-small bttn-primary"" type="submit">Log In</button>' +
      '</div>' +
    '</form>'
    ;

  // Add Info Window to map
  let infoWindow = new google.maps.InfoWindow({
    content: contentLogin,
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







