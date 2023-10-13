//
// RESULT
//

// Initialize and add the map
let map;
let lat_default = parseFloat(document.getElementById('map').getAttribute("current-game-lat-default"));
let long_default = parseFloat(document.getElementById('map').getAttribute("current-game-long-default"));
let map_zoom = parseFloat(document.getElementById('map').getAttribute("map-zoom"));
let map_marker_title = document.getElementById('map').getAttribute("map-marker-title");
let current_game_lat_answer_user = parseFloat(document.getElementById('map').getAttribute("current-game-lat-answer-user"));
let current_game_long_answer_user = parseFloat(document.getElementById('map').getAttribute("current-game-long-answer-user"));
let current_game_answer_user_validation = document.getElementById('map').getAttribute("current-game-answer-user-validation");
let current_game_loc_id = parseFloat(document.getElementById('map').getAttribute("current-game-loc-id"));
let current_game_loc_attempts = parseFloat(document.getElementById('map').getAttribute("current-game-loc-attempts"));
let time_game = parseFloat(document.getElementById('map').getAttribute("time-game"));
let time_location = parseFloat(document.getElementById('map').getAttribute("time-location"));
let base_score = parseFloat(document.getElementById('map').getAttribute("base-score"));
let bonus_score = parseFloat(document.getElementById('map').getAttribute("bonus-score"));
let game_score = parseFloat(document.getElementById('map').getAttribute("game-score"));
let total_score = parseFloat(document.getElementById('map').getAttribute("total-score"));
let doubleQuote = ' " ';


async function initMap() {
  // The game default location
  const position = { lat: current_game_lat_answer_user, lng: current_game_long_answer_user };
  
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

  // Content for Info Window on submit.html
  let try_again

  if (current_game_answer_user_validation == 'incorrect.') {
    try_again = 
    '<div class="infowindow-result-footer-try">' +
      '<form name="router" action="/traffic" method="post">' + 
      '<input type="hidden" name="page" class="hidden-field" value="result"></input>' + 
      '<input type="hidden" name="goto" class="hidden-field" value="game_again"></input>' +
      '<input type="hidden" name="try-again" class="hidden-field" value="1"></input>' +
      '<button name="router" class="btn btn-primary btn-sm" type="submit">Try Again</button>' +
      '</form>' +
    '</div>';
  } else {
    try_again = ''
  }

  const contentResult = 
    '<div class="infowindow-result">' +
      '<div class="infowindow-result-title">' + 
        '<div class="infowindow-result-title-left">' + 
          current_game_answer_user_validation  +
        '</div>' + 
        '<div class="infowindow-result-title-right">' + 
        'Score: ' + game_score + ' pts<br>' +
        '</div>' +
      '</div>' +
      '<div class="infowindow-result-body">' +
        'Location ID: ' + current_game_loc_id + '<br>' +
        'Attempt(s): ' + current_game_loc_attempts + '<br>' +
        'Game Time: ' + time_game + ' minutes<br>' + 
        'Location Time: ' + time_location + ' minutes<br><br>' +
        'Base Score: ' + base_score + '<br>' +
        'Bonus Score: ' + bonus_score + '<br>' +
      '</div>' +
      '<div class="infowindow-result-footer">' + 
        try_again + 
        '<div class="infowindow-result-footer-new">' +
          '<form name="router" action="/traffic" method="post">' +  
            '<input type="hidden" name="page" class="hidden-field" value="result"></input>' + 
            '<input type="hidden" name="goto" class="hidden-field" value="game_new"></input>' +
            '<input type="hidden" name="try-again" class="hidden-field" value="0"></input>' +
            '<button name="router" class="btn btn-primary btn-sm" type="submit">New Search</button>' + 
          '</form>' +
        '</div>' + 
        '<div class="infowindow-result-footer-quit">' +
          '<form name="submit" action="/traffic" method="post">' +  
            '<input type="hidden" name="page" class="hidden-field" value="result"></input>' + 
            '<input type="hidden" name="goto" class="hidden-field" value="index"></input>' + 
            '<input type="hidden" name="try-again" class="hidden-field" value="0"></input>' +
            '<button name="router" class="btn btn-link btn-sm" type="submit">Quit Game</button>' + 
          '</form>' +
        '</div>' + 
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







