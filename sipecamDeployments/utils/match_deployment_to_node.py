import os
import json
from os.path import exists as file_exists

from sipecamDeployments.helpers.clean_coordinates import clean_coordinates
from sipecamDeployments.helpers.inverse_haversine import inverse_haversine
from sipecamDeployments.helpers.validate_coordinates import validate_coordinates

def match_deployment_to_node(deployments, cumulus, session, update=True):
    """
    Given a list of deployments and a cumulus dict with its
    associated nodes and devices, matches a deployment with
    a node by the lat/long values of both.

    Parameters:
        deployments (list): A list of deployments

        cumulus (dict):   A dict containing the cumulus info.

        session (object):       Session object with auth credential
                                of zendro.

    Returns:
        matched_deployments (dict): A dict containing the matched
                                    deployments.
    """ 
    matched_deployments = []
    log_reports = []
    for d in deployments:
        m_deployment = {}
        # parse coordinates to a valid format
        # e.g.: 1615568.0, 9358302.0 -> 16.16038, -93.50838
        clean_coords = clean_coordinates(d["latitude"], d["longitude"])
        latlng = validate_coordinates(
            clean_coords, cumulus["geometry"]
        )

        dist = []
        match = []
        if latlng:
            for node in cumulus["nodesFilter"]:
                # find the distance bewtween the device
                # and the node with haversine function
                dist.append(
                inverse_haversine(
                    [float(latlng[0]), float(latlng[1])],
                    [
                        node["location"]["coordinates"][1],
                        node["location"]["coordinates"][0],
                    ],
                )
                )

            # searches the minimum distance between node
            # and device to get a match
            match = cumulus["nodesFilter"][dist.index(min(dist))]
        
        if update:
            m_deployment.update(d)

        if (
            "individualsFilter" in cumulus.keys()
            or "devicesFilter" in cumulus.keys()
        ):
            m_deployment.update({"zendro_cumulus_id": cumulus["id"]})

        m_deployment.update(
            {
                "zendro_node_id": match["id"] if latlng else "null",
                "node_name": match["nomenclatura"] if latlng else "null",
                "module": match["cat_integr"] if latlng else "null",
                "latitude": latlng[0] if latlng else "null",
                "longitude": latlng[1] if latlng else "null",
                "altitude": match["location"]["coordinates"][2]
                if latlng
                else "null",
                "original_coordinates": clean_coords
            }
        )

        if (
            latlng
            or "devicesFilter" in cumulus.keys()
            or "individualsFilter" in cumulus.keys()
        ):
            # matched_deployments.append(m_deployment)
            yield m_deployment
        else:
            continue

    # return matched_deployments
