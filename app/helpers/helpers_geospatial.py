# Python Standard Library
from datetime import timezone
from functools import wraps
from math import floor

# Third-Party Libraries
from flask import redirect, session
from geographiclib.geodesic import Geodesic
from haversine import haversine, Unit
from shapely.ops import nearest_points







def get_distance(point, polygon):
    
    # Get nearest polygon point
    point1, p2 = nearest_points(polygon, point)
    
    # Get coordinate1
    coordinate1 = (point.y, point.x)

    # Get coordinate2
    coordinate2 = (point1.y, point1.x)

    # Calculate distance
    game_answer_distance = haversine(coordinate1, coordinate2, unit=Unit.FEET)
    game_answer_distance = floor(game_answer_distance)

    return game_answer_distance


def get_duration(game_start, game_end):

    # Calculate time difference in seconds
    game_duration = game_end.replace(tzinfo=timezone.utc) - game_start.replace(tzinfo=timezone.utc)
    duration_sec = game_duration.seconds

    return duration_sec


def latitude_offset(lat, long):
    """Get latlng for first info window on game page."""

    geod = Geodesic.WGS84

    lat1 = lat
    lon1 = long
    theta = 0 #direction from North, clockwise 
    azi1 = theta - 0 #(90 degrees to the left)
    shift = 201 #meters

    g = geod.Direct(lat1, lon1, azi1, shift)

    lat2 = g['lat2']
    lon2 = g['lon2']

    return(lat2)


def longitude_offset(lat, long, j):
    """Get latlng for first info window on game page."""

    geod = Geodesic.WGS84

    lat1 = lat
    lon1 = long
    theta = 0 # direction from North, clockwise 
    azi1 = theta - 90 # (90 degrees to the left)
    shift = j #meters

    g = geod.Direct(lat1, lon1, azi1, shift)

    lat2 = g['lat2']
    lon2 = g['lon2']

    return(lat2, lon2)

