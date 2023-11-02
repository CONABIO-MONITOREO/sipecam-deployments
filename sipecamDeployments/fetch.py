import os
import json
import time
import datetime
import requests
import argparse

from sipecamDeployments.utils.get_data import *
from sipecamDeployments.utils.get_surveys import *
from sipecamDeployments.utils.get_cumulus_data import *
from sipecamDeployments.utils.match_deployment_to_node import *
from sipecamDeployments.utils.login_to_zendro import *
from sipecamDeployments.utils.clean_kobo_reports import *

def kobo_deployments():
    # Auth credentials for Kobo
    auth = (os.getenv('KOBO_USER'), os.getenv('KOBO_PASSWORD'))

    # login request
    login = requests.get(os.getenv('KOBO_URL') + "token/?format=json", auth=auth)

    # Session for zendro
    session = login_to_zendro()
    survey_type = "deployments"
    common_name = "Camara Trampa y Grabadoras v 1.1 cumulo"
    if login.status_code != 200:
        raise ValueError("Bad Credentials!")
    # retreive token from response
    token = json.loads(login.text)['token']

    # set headers for the following requests
    headers = {
        "Authorization": "Token " + token,
        "Accept": "application/json"
    }

    filtered = get_surveys(common_name, headers)

    # before making another request
    # wait 2 second to not overload the server
    time.sleep(2)
    for r in get_data(filtered, headers):
        clean_data = clean_kobo_deployment_report(r)
        cumulus_name = r["name"].replace(common_name,"").replace(" ","")

        if cumulus_name == "32":
            for n, d in enumerate(clean_data):
                if "-19." in d["longitude"]:
                    latitude = d["latitude"]
                    longitude = d["longitude"]
                    clean_data[n]["longitude"] = longitude.replace("-19.", "-99.")
                    clean_data[n]["coordinates_warning"] = f"Coordinates corrected by hand from (lat, lon) = ({latitude},{longitude})"
                else:
                    clean_data[n]["coordinates_warning"] = None

        cumulus_data = get_cumulus_nodes(
                session,
                int(cumulus_name),
                survey_type
            )

        matched_deployments = match_deployment_to_node(clean_data,cumulus_data,session)

        for depl in matched_deployments:
            depl.update({"cumulus_name": cumulus_name})
            if "coordinates_warning" not in depl:
                depl.update({"coordinates_warning": None})
            yield depl

def current_kobo_deployments():
    depls = [x for x in kobo_deployments()]
    return {
        "kobo_source": os.getenv('KOBO_URL'),
        "kobo_user": os.getenv('KOBO_USER'),
        "zendro_source": os.getenv('ZENDRO_URL'),
        "zendro_user": os.getenv('ZENDRO_USER'),
        "timestamp": datetime.datetime.now().isoformat(),
        "deployments": depls
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''Get kobo deployments
    and match zendro information from SiPeCaM surveys. The following
    environtmental variables should be declared in order to get the
    result: "KOBO_URL", "KOBO_USER", "KOBO_PASSWORD", "ZENDRO_URL",
    "ZENDRO_USER", "ZENDRO_PASSWORD"''')
    parser.add_argument('--output', default=None, required=False,
                        help='A valid output path. If not specified, output will be printed to stdout.')
    args = parser.parse_args()

    depls = current_kobo_deployments()

    if args.output is not None:
        with open(args.output, "w") as f:
            json.dump(depls, f)
    else:
        print(json.dumps(depls, indent=2))
