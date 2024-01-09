import psycopg2
from psycopg2 import sql
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.ops import nearest_points
from haversine import haversine, Unit
from math import floor


def shapefile(db, coordinates, loc_id):

    # Create a GeoDataFrame with a single polygon from the property_coordinates list
    polygon = Polygon([(coord['lng'], coord['lat']) for coord in coordinates])
    gdf = gpd.GeoDataFrame(geometry=[polygon])

    # Save the GeoDataFrame as a shapefile
    # gdf.to_file('property_polygon.shp', driver='ESRI Shapefile')

    # Connect to the PostgreSQL database
    connection = psycopg2.connect(db)
    cursor = connection.cursor()

    query = "UPDATE locs SET "
    query = query + "loc_key_shp = ST_GeomFromText('{}'), "
    query = query + "loc_key_shp_valid = TRUE, "
    query = query + "loc_date_updated = CURRENT_TIMESTAMP "
    query = query + "WHERE id = %s; "

    for i, row in gdf.iterrows():
        cursor.execute(sql.SQL(query).format(sql.SQL(row['geometry'].wkt)), (loc_id,))

    # Commit the changes
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()

    return 1


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

