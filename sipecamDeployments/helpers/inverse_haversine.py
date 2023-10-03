from math import radians, cos, sin, asin, sqrt

def inverse_haversine(point1,point2):
    """
    Apply the inverse haversine function to a pair
    of lat/long points to obtain the distance 
    between them.

    Parameters:
        point1 (list):  A list containing the first
                        point coordinates.
        
        point2 (list):  A list containing the second
                        point coordinates.

    Returns:
        distance (float):   The distance between the 
                            pair of points.
            
    """

    # convert decimal degrees to radians 
    lat1, long1, lat2, long2 = map(radians, 
                [point1[0], point1[1], point2[0], point2[1]])

    # haversine formula 
    dlon = long2 - long1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # Radius of earth in kilometers is 6371
    distance = 6371* c

    return distance