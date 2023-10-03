import json

def parse_to_graphql_query(deployments,survey_type):
    """
    Parse a deployments dict to graphql query type
    to post to zendro api.

    Parameters:
        deployments (dict):     A dict containing the deployments
                                of devices.
        survey_type (string):   A string that indicates the type of
                                the surveys.

    Returns:
        deployments_query (string): A strng containing the query
                                  to create each deployment.
    """

    query = ""
    for idx,d in enumerate(deployments):
        if survey_type == "deployments":
            query = query + ("d" + str(idx) + ": addDeployment("
             + "date_deployment: \"" + d["date_deployment"] + "\","
             + "latitude: " +  d["latitude"] + ","
             + "longitude: " + d["longitude"] + ","
             + "altitude: " + str(d["altitude"]) + ","
             + "metadata: " + d["metadata"] + ","
             + "kobo_url: \"" + d["kobo_url"] + "\","
             + "addCumulus: " + d["cumulus_id"] + ","
             + "addNode: " + d["node_id"] + ","
             + "addDevice: " + d["device_id"] + ")"
             + "{ id }   "
            )
        elif survey_type == "individuals":
            query = query + ("d" + str(idx) + ": addIndividual("
             + "date_trap: \"" + d["date_trap"] + "\","
             + "latitude: " +  d["latitude"] + ","
             + "longitude: " + d["longitude"] + ","
             + "altitude: " + str(d["altitude"]) + ","
             + "metadata: " + d["metadata"].replace('\n','') + ","
             + "clave_posicion_malla: \"" + d["clave_posicion_malla"] + "\",")

            if "arete" in d:
                query += "arete: " + d["arete"] + ","

            query += ("kobo_url: \"" + d["kobo_url"] + "\","
             + "addAssociated_cumulus: " + d["cumulus_id"] + ","
             + "addAssociated_node: " + d["node_id"] + ")"
             + "{ id }   "
            )
        
        elif survey_type == "erie":
            query = query + ("d" + str(idx) + ": addTransect("
             + "date_transecto: \"" + d["date_transecto"] + "\","
             + "number: " + d["number"] + ","
             + "latitude: " +  d["latitude"] + ","
             + "longitude: " + d["longitude"] + ","
             + "sum_vegetation_structure: " + d["sum_vegetation_structure"] + ","
             + "sum_indicator_species: " + d["sum_indicator_species"] + ","
             + "sum_impact: " + d["sum_impact"] + ","
             + "percentage: " + d["percentage"] + ","
             + "addAssociated_node: " + d["node_id"] + ")"
             + "{ id }   "
            )

    return query
