import os
import re
import json
import requests

def get_surveys(common_name,headers):
    """
    Makes a request to the kobo api to retrieve all the
    surveys with a common name and then filters the ones
    that do not match completely with the common name.

    Parameters:
        common_name (string):   The common name that the surveys
                                share. Used to find all the surveys
                                that partially match that string.

        headers (dict):         A dictionary that holds the headers
                                to make the auth requests to kobo.

    Returns:
        filtered_surveys (list):    A list containing dicts with asset
                                    names and urls of the filtered
                                    kobo surveys.

    """
    
    name = ''.join(["\'", common_name, "\'"])

    assets_response = requests.get(os.getenv('KOBO_URL') + 
            "/api/v2/assets/?q=(" + 
            name + ')',headers=headers)

    surveys = json.loads(assets_response.text)['results']

    
    # pattern to check
    pattern = re.compile("^"+common_name)

    filtered_surveys = []

    for i in surveys:
        if pattern.match(i['name']):
            asset = {
                "url": i['url'],
                "name": i['name']
            }
            filtered_surveys.append(asset)

    return filtered_surveys