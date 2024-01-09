//
// LOCS - EDIT
//

// Initialize and add the map
let map;
let map_lat = parseFloat(document.getElementById('map').getAttribute("map-lat"));
let map_lng = parseFloat(document.getElementById('map').getAttribute("map-lng"));
let map_lat_offset = parseFloat(document.getElementById('map').getAttribute("map-lat-offset"));
let map_nw_lat = parseFloat(document.getElementById('map').getAttribute("map-nw-lat"));
let map_nw_lng = parseFloat(document.getElementById('map').getAttribute("map-nw-lng"));
let map_ne_lat = parseFloat(document.getElementById('map').getAttribute("map-ne-lat"));
let map_ne_lng = parseFloat(document.getElementById('map').getAttribute("map-ne-lng"));
let map_sw_lat = parseFloat(document.getElementById('map').getAttribute("map-sw-lat"));
let map_sw_lng = parseFloat(document.getElementById('map').getAttribute("map-sw-lng"));
let map_se_lat = parseFloat(document.getElementById('map').getAttribute("map-se-lat"));
let map_se_lng = parseFloat(document.getElementById('map').getAttribute("map-se-lng"));
let map_polygon = document.getElementById('map').getAttribute("map-polygon");
let map_corners = document.getElementById('map').getAttribute("map-corners");
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

    var polyOptions = {
        strokeWeight: 0,
        fillOpacity: 0.45,
        strokeColor: "#FF0000",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#FF0000",
        fillOpacity: 0.35
    };

    // Prepare to load coordinates
    const coordinates = JSON.parse(map_polygon);

    // loads databased saved coordinates
    var propertyCoords = '';
    var points = coordinates;

    var existingPolygon = null;

    var drawingManager = null;

    if (typeof points !== 'undefined') {
        if (!google.maps.Polygon.prototype.getBounds) {
        google.maps.Polygon.prototype.getBounds = function() {
            var bounds = new google.maps.LatLngBounds();
            this.getPath().forEach(function(element, _) {
            bounds.extend(element);
            });
            return bounds;
        };
        }

        /**
        * used for tracking polygon bounds changes within the drawing manager
        */
        google.maps.Polygon.prototype.enableCoordinatesChangedEvent = function() {
            var me = this,
                isBeingDragged = false,
                triggerCoordinatesChanged = function() {
                    //broadcast normalized event
                    google.maps.event.trigger(me, "coordinates_changed");
                };

            //if  the overlay is being dragged, set_at gets called repeatedly, so either we can debounce that or igore while dragging, ignoring is more efficient
            google.maps.event.addListener(me, "dragstart", function() {
                isBeingDragged = true;
            });

            //if the overlay is dragged
            google.maps.event.addListener(me, "dragend", function() {
                triggerCoordinatesChanged();
                isBeingDragged = false;
            });

            //or vertices are added to any of the possible paths, or deleted
            var paths = me.getPaths();
            paths.forEach(function(path, i) {
                google.maps.event.addListener(path, "insert_at", function() {
                    triggerCoordinatesChanged();
                });
                google.maps.event.addListener(path, "set_at", function() {
                    if (!isBeingDragged) {
                        triggerCoordinatesChanged();
                    }
                });
                google.maps.event.addListener(path, "remove_at", function() {
                    triggerCoordinatesChanged();
                });
            });
        };

        function extractPolygonPoints(data) {
            var MVCarray = data.getPath().getArray();

            var to_return = MVCarray.map(function(point) {
                return `(${point.lat()},${point.lng()})`;
            });
            // first and last must be same
            return to_return.concat(to_return[0]).join(",");
        }

        existingPolygon = new google.maps.Polygon({
            paths: points,
            editable: true,
            draggable: false,
            map: map,
            ...polyOptions
        });

        map.fitBounds(existingPolygon.getBounds());

        existingPolygon.enableCoordinatesChangedEvent();

        google.maps.event.addListener(existingPolygon, 'coordinates_changed', function() {
            // console.warn('coordinates changed!', extractPolygonPoints(existingPolygon))
            var polygonData = extractPolygonPoints(existingPolygon);
            console.warn('coordinates changed!', polygonData);
            document.getElementById("propertyCoordinates").value = polygonData;

            // var input_element = document.getElementById('shapefile');
            // input_element.value = polygonData;
            // console.warn('coordinates changed!', input_element);
        });

    // My guess is to use a conditional statement to check if the map has any coordinates saved?
    } else {
        drawingManager = new google.maps.drawing.DrawingManager({
            drawingMode: google.maps.drawing.OverlayType.POLYGON,
            drawingControlOptions: {
                position: google.maps.ControlPosition.TOP_CENTER,
                drawingModes: ["polygon"]
            },
            polylineOptions: {
                editable: true,
                draggable: true
            },
            rectangleOptions: polyOptions,
            circleOptions: polyOptions,
            polygonOptions: polyOptions,
            map: map
        });

        google.maps.event.addListener(drawingManager, 'overlaycomplete', function(e) {
            if (e.type !== google.maps.drawing.OverlayType.MARKER) {
                // Switch back to non-drawing mode after drawing a shape.
                drawingManager.setDrawingMode(null);
                // Add an event listener that selects the newly-drawn shape when the user
                // mouses down on it.
                var newShape = e.overlay;
                newShape.type = e.type;
                google.maps.event.addListener(newShape, 'click', function(e) {
                    if (e.vertex !== undefined) {
                        if (newShape.type === google.maps.drawing.OverlayType.POLYGON) {
                            var path = newShape.getPaths().getAt(e.path);
                            path.removeAt(e.vertex);
                            if (path.length < 3) {
                                newShape.setMap(null);
                            }
                        }
                    }
                    setSelection(newShape);
                });
            }
            var coords = e.overlay.getPath().getArray();
            document.getElementById("propertyCoordinates").value = coords;
        });

    }









}


initMap();







