import os
import json
import math
import time
from sipecamDeployments.utils.match_deployment_to_node import match_deployment_to_node
from sipecamDeployments.utils.clean_kobo_reports import *
from sipecamDeployments.utils.parse_to_graphql_query import parse_to_graphql_query
from sipecamDeployments.utils.get_cumulus_data import get_cumulus_nodes
from sipecamDeployments.utils.sort_data_by_cumulus import sort_data_by_cumulus

def build_n_post_deployment_query(session,reports,common_name,survey_type):
    """
     Build the query to post to zendro from the data
     extracted for device deployments from kobo.

     Params:
        session (object):       Session object with auth credential
                                of zendro.
        reports (list):         A list containing the data of the 
                                reports.
        common_name (string):   A string containing the name of the
                                surveys.
        survey_type (string):   A string that indicates the type of
                                the surveys.

     Returns:
        (void) 
     """

    deployments = []
    log_reports = []
    for r in reports:
        """
            Match reports with its node id, cumulus id and
            device id to build a deployment dict so the script
            can make a post to zendro to create the deployment.
          """
        clean_data = clean_kobo_deployment_report(r) 
        
         
        cumulus_data = get_cumulus_nodes(
                    session,
                    int(r["name"].replace(common_name,"")),
                    survey_type
                )
        
        matched_deployments,logs = match_deployment_to_node(clean_data,cumulus_data,session)
        
        log_reports = [
            *log_reports,
            *logs
        ]

        deployments = [
            *deployments,
            *matched_deployments]
        # before making another request in the loop
        # wait 2 second to not overload the server
        time.sleep(2)

    if len(deployments) > 0:
        # post data to zendro
        response = session.post(os.getenv("ZENDRO_URL")
                                + "/graphql",json={
                                    "query": "mutation {" +
                                        parse_to_graphql_query(
                                            deployments,
                                            survey_type) + "}"
                                })
        # generate a report 
        deployments_created = json.loads(response.text)["data"]
        print("\n\nFueron creados %d reportes satisfactoriamente.\n\n" % len(deployments_created))
        
        for r in log_reports:
            filename = os.getenv('LOG_PATH') + "extracted_reports.log"
            with open(filename, 'a') as log_file:
                log_file.writelines(r + "\n")
    else:
        print("\n\nNo hay nuevos desplieges que registrar.\n\n")


def build_n_post_individuals_n_erie_query(session,reports,survey_type):
    """
     Build the query to post to zendro from the data
     extracted for individuals and erie from kobo.

     Params:
        session (object):       Session object with auth credential
                                of zendro.
        reports (list):         A list containing the data of the 
                                reports.
        survey_type (string):   A string that indicates the type of
                                the surveys.

     Returns:
        (void) 
     """

    if survey_type == "individuals":
        clean_data = clean_kobo_individual_report(reports[0]) 
    elif survey_type == "erie":
        clean_data = clean_kobo_erie_report(reports[0])

    # sort data by cumulus
    sorted_data = sort_data_by_cumulus(clean_data)
    
    deployments = []
    for key,data in sorted_data.items():
        cumulus_data = get_cumulus_nodes(
                    session,
                    int(key.replace("sipecam","")),
                    survey_type
                )
        
        deployments = [
            *deployments,
            *match_deployment_to_node(data,cumulus_data,session)[0]]
            
        # before making another request in the loop
        # wait 2 second to not overload the server
        time.sleep(2)
   
    if len(deployments) > 0:
        # post data to zendro

        deployments_created = []
        if len(deployments) > 50:
            # if too many deployments then 
            # split the data into parts to
            # upload

            print("Too many reports, uploading by parts...")

            total_deployments = len(deployments)

            parts_deployments = math.ceil(total_deployments/50)

            part = int(total_deployments/parts_deployments)

            left_slice = 0

            for i in range(1,parts_deployments+1):
                
                if i == parts_deployments and part*i < total_deployments:
                    part_of_deployments = total_deployments 
                else:
                    part_of_deployments = part*i

                partial_deployments = deployments[left_slice:part_of_deployments]
                response = session.post(os.getenv("ZENDRO_URL")
                                        + "/graphql",json={
                                            "query": "mutation {" +
                                                parse_to_graphql_query(
                                                    partial_deployments,
                                                    survey_type) + "}"
                                        })
                
                time.sleep(5)

                if response.status_code == 200:
                    print("Part %d of %d uploaded\n" % (i,parts_deployments) )
                    deployments_created = [*deployments_created, *json.loads(response.text)["data"]]
                else:
                    print(response.status_code,response.text)

                left_slice = ( part*i ) + 1

        else:
            response = session.post(os.getenv("ZENDRO_URL")
                                        + "/graphql",json={
                                            "query": "mutation {" +
                                                parse_to_graphql_query(
                                                    deployments,
                                                    survey_type) + "}"
                                        })
            
            if response.status_code == 200:
                    deployments_created = [*deployments_created, *json.loads(response.text)["data"]]
            else:
                print(response.status_code,response.text)

        if len(deployments_created) > 0:
            print("\n\nFueron creados %d reportes de %s satisfactoriamente.\n\n" % (
                len(deployments_created), "individuos" if survey_type == "individuals" else "erie"))

    else:
        print("\n\nNo hay nuevas capturas de %s que registrar.\n\n" % ("individuos" if survey_type == "individuals" else "erie"))
