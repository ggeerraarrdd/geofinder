//
// GEOFINDER - RESULT
//

// Initialize and add the map
let map;
let map_zoom = parseFloat(document.getElementById('map').getAttribute("map-zoom"));
let map_marker_title = document.getElementById('map').getAttribute("map-marker-title");
let current_geo_game_geofinder_id = document.getElementById('map').getAttribute("current-geo-game-geofinder-id");
let current_geo_game_geofinder_date = document.getElementById('map').getAttribute("current-geo-game-geofinder-date");
let current_geo_game_submit_lat = parseFloat(document.getElementById('map').getAttribute("current-geo-game-submit-lat"));
let current_geo_game_submit_lng = parseFloat(document.getElementById('map').getAttribute("current-geo-game-submit-lng"));
let current_geo_game_submit_validation = parseInt(document.getElementById('map').getAttribute("current-geo-game-submit-validation"));
let current_geo_game_loc_id = parseFloat(document.getElementById('map').getAttribute("current-geo-game-loc-id"));
let display_geo_game_duration = parseInt(document.getElementById('map').getAttribute("display-geo-game-duration"));
let display_geo_game_score_base = parseInt(document.getElementById('map').getAttribute("display-geo-game-score-base"));
let display_geo_game_score_bonus = parseInt(document.getElementById('map').getAttribute("display-geo-game-score-bonus"));
let display_geo_game_score_total = parseInt(document.getElementById('map').getAttribute("display-geo-game-score-total"));
let doubleQuote = ' " ';


async function initMap() {
  // The game default location
  const position = { lat: current_geo_game_submit_lat, lng: current_geo_game_submit_lng };

  // Request needed libraries.
  //@ts-ignore
  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerView } = await google.maps.importLibrary("marker");

  // The map, centered at location
  map = new Map(document.getElementById("map"), {
    zoom: map_zoom,
    center: position,
    mapId: "DEMO_MAP_ID",
    disableDefaultUI: true,
    gestureHandling: "none",
    zoomControl: false,
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

  // Content for Info Window on submit.html
  let message
  let review
  let body
  let try_again

  if (current_geo_game_submit_validation == 0) {
    // Incorrect
    message = 'incorrect';
    review = 
    'Score: na';
    body = 
    'Attempts: tbd<br>' +
    'Game Time: ' + display_geo_game_duration + ' secs<br>' +
    'Total Time: tbd<br><br>' +
    'Base Score: na<br>' +
    'Bonus Score: na<br>';
    try_again = 
    '<div class="infowindow-geofinder-result-footer-left">' + 
      '<div class="infowindow-geofinder-result-footer-item">' +
        '<form name="router" action="/" method="post">' + 
          '<input type="hidden" name="page" class="hidden-field" value="index"></input>' + 
          '<input type="hidden" name="goto" class="hidden-field" value="geofinder_game"></input>' +
          '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' +
          '<input type="hidden" name="bttn" class="hidden-field" value="again"></input>' +
          '<button name="router" class="bttn bttn-xsmall bttn-primary" type="submit">' +
            'Try Again' + 
          '</button>' +
        '</form>' +
      '</div>' +
      '<div class="infowindow-geofinder-result-footer-item">' +
        '<form name="router" action="/geofinder/result" method="post">' + 
          '<input type="hidden" name="page" class="hidden-field" value="geofinder_result"></input>' + 
          '<input type="hidden" name="goto" class="hidden-field" value="index"></input>' +
          '<input type="hidden" name="try-again" class="hidden-field" value="1"></input>' +
          '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' +
          '<input type="hidden" name="bttn" class="hidden-field" value="pause"></input>' +
          '<button name="router" class="bttn bttn-xsmall bttn-primary" type="submit">' +
            'Pause Search' + 
          '</button>' +
        '</form>' +
      '</div>' +
    '</div>' +
    '<div class="infowindow-geofinder-result-footer-right">' + 
      '<div class="infowindow-geofinder-result-footer-item">' +
        '<form name="router" action="/geofinder/result" method="post">' + 
          '<input type="hidden" name="page" class="hidden-field" value="geofinder_result"></input>' + 
          '<input type="hidden" name="goto" class="hidden-field" value="zero"></input>' +
          '<input type="hidden" name="try-again" class="hidden-field" value="1"></input>' +
          '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' +
          '<input type="hidden" name="bttn" class="hidden-field" value="quit"></input>' +
          '<button name="router" class="bttn bttn-xsmall bttn-naked" style="color: gray;" type="submit">' +
            'Quit' + 
          '</button>' +
        '</form>' +
      '</div>' +
    '</div>';
  } else if (current_geo_game_submit_validation == 2) {
    // Quit
    message = 'quit';
    review = 
    'Score: 0 pts' +
    '<div class="infowindow-result-title-right-review">' +
      '<form name="router" action="/geofinder/result" method="post">' + 
        '<input type="hidden" name="page" class="hidden-field" value="geofinder_result"></input>' + 
        '<input type="hidden" name="goto" class="hidden-field" value="review"></input>' +
        '<input type="hidden" name="try-again" class="hidden-field" value="0"></input>' +
        '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' +
        '<input type="hidden" name="bttn" class="hidden-field" value="review"></input>' +
        '<input type="hidden" name="review" class="hidden-field" value="' + current_geo_game_geofinder_id + '"></input>' + 
        '<button name="router" class="bttn bttn-xsmall" type="submit">' +
          'Review' +
        '</button>' +
      '</form>' +
    '</div>';
    body = 
      'Attempts: tbd<br>' +
      'Game Time: ' + display_geo_game_duration + ' secs<br>' +
      'Total Time: tbd<br><br>' +
      'Base Score: 0 pts<br>' +
      'Bonus Score: 0 pts<br>';
    try_again = 
    '<div class="infowindow-result-footer-try">' +
      '<form name="router">' + 
      '<button name="router" class="bttn bttn-xsmall" type="submit" disabled>' +
          'Next Search in 14h 12m' + 
        '</button>' +
      '</form>' +
    '</div>';
  } else if (current_geo_game_submit_validation == 1) {
    // Correct
    message = 'correct!';
    review = 
    'Score: ' + display_geo_game_score_total + ' pts' +
    '<div class="infowindow-result-title-right-review">' +
      '<form name="router" action="/geofinder/result" method="post">' + 
        '<input type="hidden" name="page" class="hidden-field" value="geofinder_result"></input>' + 
        '<input type="hidden" name="goto" class="hidden-field" value="review"></input>' +
        '<input type="hidden" name="try-again" class="hidden-field" value="0"></input>' + 
        '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' +
        '<input type="hidden" name="bttn" class="hidden-field" value="review"></input>' +
        '<input type="hidden" name="review" class="hidden-field" value="' + current_geo_game_geofinder_id + '"></input>' + 
        '<button name="router" class="bttn bttn-xsmall" type="submit">' +
          'Review' +
        '</button>' +
      '</form>' +
    '</div>';
    body = 
    'Attempts: tbd<br>' +
    'Game Time: ' + display_geo_game_duration + ' secs<br>' +
    'Total Time: ' + display_geo_game_duration + ' seconds<br><br>' +
    'Base Score: ' + display_geo_game_score_base + '<br>' +
    'Bonus Score: ' + display_geo_game_score_bonus + '<br>';
    try_again = 
    '<div class="infowindow-result-footer-try">' +
      '<form name="router">' + 
        '<button name="router" class="bttn bttn-xsmall" type="submit" disabled>' +
          'Next Search in 14h 12m' + 
        '</button>' +
      '</form>' +
    '</div>';
  } else {
    message = '';
    review = '';
    body = '';
    try_again = '';
  }
  

  const contentResult = 
    '<div class="infowindow-result">' +
      '<div class="infowindow-result-title">' + 
        '<div class="infowindow-result-title-left">' + 
          message  +
        '</div>' + 
        '<div class="infowindow-result-title-right">' + 
          review + 
        '</div>' +
      '</div>' +
      '<div class="infowindow-result-body">' +
        '<div style="padding-bottom: 15px; display: flex; flex-direction: row; align-items: center;">' +
          '<div style="padding-right: 6px;">' +
            '<span class="material-symbols-outlined" style="line-height: normal; font-size: 22px;">travel_explore</span>' +
          '</div>' +
          '<div>' +
            'Geofinder #: ' + current_geo_game_geofinder_date +
          '</div>' +
        '</div>' +
        body +
      '</div>' +
      '<div class="infowindow-geofinder-result-footer">' + 
        try_again + 
      '</div>' +
    '</div>'
    ;

  // Add Info Window to map
  let infoWindow = new google.maps.InfoWindow({
    content: contentResult,
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







