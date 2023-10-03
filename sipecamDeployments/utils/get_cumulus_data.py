import os
import json

def get_cumulus_nodes(session,cumulus_id,survey_type):
    """
    Get the cumulus from zendro by the given id and
    its associated nodes with its location.

    Parameters:
        session (Session):  A session object with 
                            zendro credentials.
        cumulus_id (int):   A number containing the
                            cumulus id to retreive

    Returns:
        cumulus_data (dict):    A dict containing info
                                of the cumulus and its
                                nodes
    """

    device_deployment = """
                devicesFilter(pagination: {limit: 0},
                    search: {
                      operator: or
                      search: [{
                      field: device_id,
                      value: "1",
                      operator: eq
                    },{
                      field: device_id,
                      value: "2",
                      operator: eq
                    }]}) {
                        id
                        serial_number
                        device_deploymentsFilter(pagination: {limit:0}) {
                            date_deployment
                        }
                    }
                """
    
    individual = """
        individualsFilter(pagination:{limit:0}) {
          date_trap
        }
    """

    erie = """
        transectsFilter(pagination:{limit: 0}) {
        	date_transecto
      	}
    """

    cumulus_query = {
        "query": """
            query (
                $limit: Int!,
                $field: cumulusField,
                $value: String,
                $valueType: InputType,
                $operator: GenericPrestoSqlOperator
            ) {
                cumulus(search: {
                    field: $field,
                    value: $value,
                    valueType: $valueType,
                    operator: $operator
                } pagination: { limit: $limit }) { 
                    id
                    geometry
                    %s
                    nodesFilter(
                        pagination: {
                            limit: $limit
                        }) {
                    id
                    location
                    nomenclatura
                    cat_integr
                    %s
                  }
                }
            }
        """ % (
            device_deployment if survey_type == "deployments"
            else (individual if survey_type == "individuals" else ""),
            erie if survey_type == "erie" else ""),
        "variables": {
            "limit": 0,
            "field": "name",
            "value": str(cumulus_id),
            "valueType": "String",
            "operator": "eq"
        }
    }

    response = session.post(os.getenv("ZENDRO_URL") 
                            + "/graphql",json=cumulus_query)
    return json.loads(response.text)["data"]["cumulus"][0]