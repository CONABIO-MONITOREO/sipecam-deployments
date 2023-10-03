import re

def clean_coordinates(lat,lng):
    """
        Given the pair of coordinates validate if
        the format is correct and if is not, then 
        converts the coordinates to a clean form.

        Parameters:
            lat (string):   A string containing the
                            latitude.
            lng (string):   A string containing the
                            longitude.
        
        Returns:
            (list):     A list containing the lat, long
                        pair of clean coordinates.
    """

    lat_format = "^(\d{2}|\d{1})[.](\d+)$"
    lng_format = "^[-](\d{3}|\d{2}|\d{1})[.](\d+)$"
    if re.search(lat_format,lat):
        # If lat does have correct format
        if re.search(lng_format,lng):
            # and also lng has the correct format
            return [lat,lng]
        else:
            # if lng does not have the correct format
            # then format lng.
            if "-" not in lng:
                lng = "-" + lng

            if len(lng.split(".")[0]) > 4:
                lng = lng.replace(".0","").replace(".","")
                if lng[:2][1:] == "9":
                    lng = lng[:3] + "." + lng[3:]
                else:
                    lng = lng[:4] + "." + lng[4:]

            return [lat,lng]
    else:
        # if lat does not have the correct format
        # then format lat.
        if len(lat.split(".")[0]) > 2:
            lat = lat.replace(".0","").replace(".","")
            lat = lat[:2] + "." + lat[2:]
        
        # check also the format of lng. If is bad
        # formatted then correct it.
        if re.search(lng_format,lng):
            return [lat,lng]
        
        else:
            if "-" not in lng:
                lng = "-" + lng

            if len(lng.split(".")[0]) > 4:
                lng = lng.replace(".0","").replace(".","")
                if lng[:2][1:] == "9":
                    lng = lng[:3] + "." + lng[3:]
                else:
                    lng = lng[:4] + "." + lng[4:]
            
            return [lat,lng]
