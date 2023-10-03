from shapely.geometry import Point, Polygon

def validate_coordinates(coordinates,cumulus_geom):
    """
    validates a pair of lat/lng coordinates
    and retreives null if the coordinates are
    a bad pair

    Parameters:
        coordinates (list):  A list of two float
                             numbers 
        cumulus_geom (dict): A dict containing a
                             geojson for the cumulus
                             geometry
    
    Returns:
        (list or None):     Returns the validated 
                            coordinates or null 
                            if the pair is a bad pair
    """

    try:
        lat = float(coordinates[0])
        lng = float(coordinates[1])

        if lat > 90 or lat < -90:
            return None
    
        if lng > 180 or lng < -180:
            return None

        point_to_check = Point(lat,lng)

        # pass geom to an array of tuples
        geom = []
        for point in cumulus_geom["coordinates"][0]:
            geom.append((point[1],point[0]))
        
        poly = Polygon(geom)

        if not point_to_check.within(poly.buffer(0.2)):
            return None

        return coordinates
    except Exception as e:
        return None

    
    