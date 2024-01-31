//
// FIFTY - RESULT
//

// Initialize and add the map
let map;
let lat_default = parseFloat(document.getElementById('map').getAttribute("current-game-lat-default"));
let long_default = parseFloat(document.getElementById('map').getAttribute("current-game-long-default"));
let map_zoom = parseFloat(document.getElementById('map').getAttribute("map-zoom"));
let map_marker_title = document.getElementById('map').getAttribute("map-marker-title");
let current_game_lat_answer_user = parseFloat(document.getElementById('map').getAttribute("current-game-lat-answer-user"));
let current_game_long_answer_user = parseFloat(document.getElementById('map').getAttribute("current-game-long-answer-user"));
let current_game_answer_user_validation = parseFloat(document.getElementById('map').getAttribute("current-game-answer-user-validation"));
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

  if (current_game_answer_user_validation == 0) {
    // Incorrect
    message = 'incorrect'; 
    review = '';
    body =
      'Attempts: ' + current_game_loc_attempts  + '<br>' +
      'Game Time: ' + time_game + ' secs<br>' +
      'Total Time: ' + time_location + ' secs<br><br>' +
      'Base Score: ' + base_score  + '<br>' +
      'Bonus Score: ' + bonus_score  + '<br>';
    try_again = 
    '<div class="infowindow-result-footer-try">' +
      '<form name="router" action="/fifty" method="post">' + 
      '<input type="hidden" name="page" class="hidden-field" value="fifty_result"></input>' + 
      '<input type="hidden" name="goto" class="hidden-field" value="fifty_start"></input>' +
      '<input type="hidden" name="try-again" class="hidden-field" value="1"></input>' +
      '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' +
      '<input type="hidden" name="bttn" class="hidden-field" value="again"></input>' +
      '<input type="hidden" name="loc" class="hidden-field" value="' + current_game_loc_id + '"></input>' + 
      '<button name="router" class="bttn bttn-xsmall bttn-primary" type="submit">' +
        'Try Again' +
      '</button>' +
      '</form>' +
    '</div>';
  } else if (current_game_answer_user_validation == 2) {
    // Quit
    message = 'quit'; 
    review = 
    '<div class="infowindow-result-title-right-review">' +
      '<form name="router" action="/fifty/result" method="post">' + 
        '<input type="hidden" name="page" class="hidden-field" value="fifty_result"></input>' + 
        '<input type="hidden" name="goto" class="hidden-field" value="fifty_review"></input>' +
        '<input type="hidden" name="try-again" class="hidden-field" value="0"></input>' +
        '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' +
        '<input type="hidden" name="bttn" class="hidden-field" value="review"></input>' +
        '<input type="hidden" name="review" class="hidden-field" value="' + current_game_loc_id + '"></input>' + 
        '<button name="router" class="bttn bttn-xsmall" type="submit">' +
          'Review' + 
        '</button>' +
      '</form>' +
    '</div>';
    body =
      'Attempts: ' + current_game_loc_attempts + '<br>' +
      'Game Time: ' + time_game + ' secs<br>' +
      'Total Time: ' + time_location + ' secs<br><br>' +
      'Base Score: ' + base_score + '<br>' +
      'Bonus Score: ' + bonus_score + '<br>';
    try_again = 
    '<div class="infowindow-result-footer-try">' +
      '<form name="router">' + 
      '<button name="router" class="bttn bttn-xsmall" type="submit" disabled>Try Again</button>' +
      '</form>' +
    '</div>';
  } else if (current_game_answer_user_validation == 1) {
    // Correct
    message = 'correct!';
    review = 
    '<div class="infowindow-result-title-right-review">' +
      '<form name="router" action="/fifty/result" method="post">' + 
        '<input type="hidden" name="page" class="hidden-field" value="fifty_result"></input>' + 
        '<input type="hidden" name="goto" class="hidden-field" value="review"></input>' +
        '<input type="hidden" name="try-again" class="hidden-field" value="0"></input>' +
        '<input type="hidden" name="review" class="hidden-field" value="' + current_game_loc_id + '"></input>' + 
        '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' +
        '<input type="hidden" name="bttn" class="hidden-field" value="review"></input>' +
        '<button name="router" class="bttn bttn-xsmall" type="submit">' +
          'Review' + 
        '</button>' +
      '</form>' +
    '</div>';
    body =
      'Attempts: ' + current_game_loc_attempts + '<br>' +
      'Game Time: ' + time_game + ' secs<br>' +
      'Total Time: ' + time_location + ' secs<br><br>' +
      'Base Score: ' + base_score + '<br>' +
      'Bonus Score: ' + bonus_score + '<br>';
    try_again = '';
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
        'Score: ' + game_score + ' pts' + 
        review + 
        '</div>' +
      '</div>' +
        '<div class="infowindow-result-body">' +
          '<div style="padding-bottom: 15px; display: flex; flex-direction: row; align-items: center;">' +
            '<div style="padding-right: 6px;">' +
              '<span class="material-symbols-outlined" style="line-height: normal; font-size: 22px;">travel_explore</span>' +
            '</div>' +
            '<div>' +
              'Geo50x #: ' + current_game_loc_id +
            '</div>' +
          '</div>' +
          body +
      '</div>' +
      '<div class="infowindow-result-footer">' + 
        try_again + 
        '<div class="infowindow-result-footer-new">' +
          '<form name="router" action="/fifty" method="post">' +  
            '<input type="hidden" name="page" class="hidden-field" value="fifty_result"></input>' + 
            '<input type="hidden" name="goto" class="hidden-field" value="fifty_start"></input>' +
            '<input type="hidden" name="try-again" class="hidden-field" value="0"></input>' +
            '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' + 
            '<input type="hidden" name="bttn" class="hidden-field" value="new"></input>' +
            '<button name="router" class="bttn bttn-xsmall bttn-primary" type="submit">' + 
              'New Search' + 
            '</button>' +
          '</form>' +
        '</div>' + 
        '<div class="infowindow-result-footer-quit">' +
          '<form name="submit" action="/fifty/result" method="post">' +  
            '<input type="hidden" name="page" class="hidden-field" value="fifty_result"></input>' + 
            '<input type="hidden" name="goto" class="hidden-field" value="dashboard_fifty"></input>' + 
            '<input type="hidden" name="try-again" class="hidden-field" value="0"></input>' +
            '<input type="hidden" name="nav" class="hidden-field" value="no"></input>' + 
            '<input type="hidden" name="bttn" class="hidden-field" value="stop"></input>' +
            '<button name="router" class="bttn bttn-xsmall bttn-naked" type="submit">' +
              'Stop Search' + 
            '</button>' +
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







