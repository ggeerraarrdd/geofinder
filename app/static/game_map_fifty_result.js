//
// FIFTY - RESULT
//

// Initialize and add the map
let map;
let map_zoom = parseFloat(document.getElementById('map').getAttribute("map-zoom"));
let map_marker_title = document.getElementById('map').getAttribute("map-marker-title");
let loc_id = parseFloat(document.getElementById('map').getAttribute("loc-id"));
let loc_view_lat = parseFloat(document.getElementById('map').getAttribute("loc-view-lat"));
let loc_view_lng = parseFloat(document.getElementById('map').getAttribute("loc-view-lng"));
let submit_lat_display = parseFloat(document.getElementById('map').getAttribute("submit-lat-display"));
let submit_lng_display = parseFloat(document.getElementById('map').getAttribute("submit-lng-display"));
let submit_validation = parseFloat(document.getElementById('map').getAttribute("submit-validation"));
let submit_attempts = parseFloat(document.getElementById('map').getAttribute("submit-attempts"));
let duration_total = document.getElementById('map').getAttribute("duration-total");
let base_score = parseFloat(document.getElementById('map').getAttribute("base-score"));
let bonus_score = parseFloat(document.getElementById('map').getAttribute("bonus-score"));
let game_score = parseFloat(document.getElementById('map').getAttribute("game-score"));
let doubleQuote = ' " ';


async function initMap() {

  // The game default location
  const position = { lat: submit_lat_display, lng: submit_lng_display };
  
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
  let score
  let review
  let body
  let try_again

  if (submit_validation == 0) {
    // Incorrect
    if (submit_attempts < 6) {
      message = 'incorrect'; 
      score = 'Score: na'; 
      review = '';
      body =
        'Attempts: ' + submit_attempts  + '<br>' +
        'Current Total Time: ' + duration_total + '<br><br>' +
        'Base Score: na<br>' +
        'Bonus Score: na<br>';
      try_again = 
        '<div class="infowindow-result-footer-try">' +
          '<form name="router" action="/fifty/results" method="post">' + 
          '<input type="hidden" name="page" class="hidden-field" value="fifty_page_results"></input>' + 
          '<input type="hidden" name="goto" class="hidden-field" value="fifty_page_game"></input>' +
          '<input type="hidden" name="bttn" class="hidden-field" value="again"></input>' +
          '<input type="hidden" name="loc" class="hidden-field" value="' + loc_id + '"></input>' + 
          '<button name="router" class="bttn bttn-xsmall bttn-primary" type="submit">' +
            'Try Again' +
          '</button>' +
          '</form>' +
        '</div>';
    } else {
      message = 'incorrect'; 
      score = 'Score: na'; 
      review = 
        '<div class="infowindow-result-title-right-review">' +
          '<form name="router" action="/fifty/results" method="post">' + 
            '<input type="hidden" name="page" class="hidden-field" value="fifty_page_results"></input>' + 
            '<input type="hidden" name="goto" class="hidden-field" value="fifty_page_review"></input>' +
            '<input type="hidden" name="bttn" class="hidden-field" value="review"></input>' +
            '<input type="hidden" name="loc" class="hidden-field" value="' + loc_id + '"></input>' + 
            '<input type="hidden" name="time" class="hidden-field" value="' + duration_total + '"></input>' + 
            '<input type="hidden" name="score" class="hidden-field" value="' + game_score + '"></input>' + 
            '<button name="router" class="bttn bttn-xsmall" type="submit">' +
              'Review' + 
            '</button>' +
          '</form>' +
        '</div>';
      body =
        'Attempts: max 6<br>' +
        'Total Time: ∅<br><br>' +
        'Base Score: ' + base_score  + '<br>' +
        'Bonus Score: ' + bonus_score  + '<br>';
      try_again = 
        '<div class="infowindow-result-footer-try">' +
          '<form>' + 
          '<button name="router" class="bttn bttn-xsmall" type="submit" disabled>' +
            'Try Again' +
          '</button>' +
          '</form>' +
        '</div>';
    }
  } else if (submit_validation == 2) {
    // Quit
    message = 'quit'; 
    score = 'Score: 0 pts'; 
    review = 
    '<div class="infowindow-result-title-right-review">' +
      '<form name="router" action="/fifty/results" method="post">' + 
        '<input type="hidden" name="page" class="hidden-field" value="fifty_page_results"></input>' + 
        '<input type="hidden" name="goto" class="hidden-field" value="fifty_page_review"></input>' +
        '<input type="hidden" name="bttn" class="hidden-field" value="review"></input>' +
        '<input type="hidden" name="loc" class="hidden-field" value="' + loc_id + '"></input>' + 
        '<input type="hidden" name="time" class="hidden-field" value="' + duration_total + '"></input>' + 
        '<input type="hidden" name="score" class="hidden-field" value="' + game_score + '"></input>' + 
        '<button name="router" class="bttn bttn-xsmall" type="submit">' +
          'Review' + 
        '</button>' +
      '</form>' +
    '</div>';
    body =
      'Attempts: ' + submit_attempts + '<br>' +
      'Total Time: ' + duration_total + '<br><br>' +
      'Base Score: ' + base_score + '<br>' +
      'Bonus Score: ' + bonus_score + '<br>';
    try_again = 
    '<div class="infowindow-result-footer-try">' +
      '<form name="router">' + 
      '<button name="router" class="bttn bttn-xsmall" type="submit" disabled>Try Again</button>' +
      '</form>' +
    '</div>';
  } else if (submit_validation == 1) {
    // Correct
    message = 'correct!';
    score = 'Score: ' + game_score + ' pts'; 
    review = 
    '<div class="infowindow-result-title-right-review">' +
      '<form name="router" action="/fifty/results" method="post">' + 
        '<input type="hidden" name="page" class="hidden-field" value="fifty_page_results"></input>' + 
        '<input type="hidden" name="goto" class="hidden-field" value="fifty_page_review"></input>' +
        '<input type="hidden" name="bttn" class="hidden-field" value="review"></input>' +
        '<input type="hidden" name="loc" class="hidden-field" value="' + loc_id + '"></input>' + 
        '<input type="hidden" name="time" class="hidden-field" value="' + duration_total + '"></input>' + 
        '<input type="hidden" name="score" class="hidden-field" value="' + game_score + '"></input>' + 
        '<button name="router" class="bttn bttn-xsmall" type="submit">' +
          'Review' + 
        '</button>' +
      '</form>' +
    '</div>';
    body =
      'Attempts: ' + submit_attempts + '<br>' +
      'Total Time: ' + duration_total + '<br><br>' +
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
          score + 
          review + 
        '</div>' +
      '</div>' +
        '<div class="infowindow-result-body">' +
          '<div style="padding-bottom: 15px; display: flex; flex-direction: row; align-items: center;">' +
            '<div style="padding-right: 6px;">' +
              '<span class="material-symbols-outlined" style="line-height: normal; font-size: 22px;">travel_explore</span>' +
            '</div>' +
            '<div>' +
              'Geo50x #: ' + loc_id +
            '</div>' +
          '</div>' +
          body +
      '</div>' +
      '<div class="infowindow-result-footer">' + 

        '<div style="display: flex; flex-direction: row;">' +
          try_again + 
          '<div class="infowindow-result-footer-new">' +
            '<form name="router" action="/fifty/results" method="post">' +  
              '<input type="hidden" name="page" class="hidden-field" value="fifty_page_results"></input>' + 
              '<input type="hidden" name="goto" class="hidden-field" value="fifty_page_game"></input>' +
              '<input type="hidden" name="bttn" class="hidden-field" value="new"></input>' +
              '<button name="router" class="bttn bttn-xsmall bttn-primary" type="submit">' + 
                'New Search' + 
              '</button>' +
            '</form>' +
          '</div>' + 
        '</div>' +
        
        '<div class="infowindow-result-footer-quit">' +
          '<form name="submit" action="/fifty/results" method="post">' +  
            '<input type="hidden" name="page" class="hidden-field" value="fifty_page_results"></input>' + 
            '<input type="hidden" name="goto" class="hidden-field" value="fifty_page_dash"></input>' + 
            '<input type="hidden" name="bttn" class="hidden-field" value="history"></input>' +
            '<button name="router" class="bttn bttn-xsmall" type="submit">' +
              'Search History' + 
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







