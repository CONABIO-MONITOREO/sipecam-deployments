import json
import time
import requests

def get_data(surveys, headers):
    """
    Request the data of the given kobo survyes, excludes
    from the assets list the ones that doesn't have at least
    one data submission, and return a dict with the assets
    and its data.

    Parameters:
        surveys (list):                  A list containing dicts with
                                         asset names and urls of the filtered
                                         kobo surveys.

        headers (dict):                  A dictionary that holds the headers
                                         to make the auth requests to kobo.

    Returns:
        assets_with_responses (list):    A list containing dicts with the assets,
                                         its data, name and url.

    """

    assets_with_responses = []
    first = True
    for asset in surveys:
        if not first:
            time.sleep(2)
        else:
            first = False
        survey_data_response = requests.get(
                    asset["url"] + "data",headers=headers)
        reports = json.loads(survey_data_response.text)

        if "count" in reports and reports["count"] > 0:
            """
                Check if given survey has any data submission,
                if it has, store it in dict as a report.
              """

            time.sleep(2)

            survey_data_labels = requests.get(
                        asset["url"],headers=headers)

            asset_report = {
                "kobo_url": asset["url"],
                "reports": reports["results"],
                "content": json.loads(survey_data_labels.text)["content"]["survey"]
            }

            # add name of the survey to dict (url is already in kobo_url key)
            asset_report.update({"name": asset["name"]})

            # assets_with_responses.append(asset_report)
            yield asset_report
        else:
            continue
