def add_attachments(report,content):
    """
        Add attachment url to metadata as a string

        Parameters:
            report (dict):  A dict containing the report data
                            of the survey for a specific device
            content (list): A list containing info of the survey.

        Returns:
            metadata (string):  A string containing the attachment urls
                                in a json structure.
     """

    metadata = "{ "
    for idx, file in enumerate(report["_attachments"]):
        """
            Iterate through the attachments to add the file
            url to the metadata field of deployment
          """
        filename = file["filename"].split("/")[4]
        for index, (key, value) in enumerate(report.items()):
            if isinstance(value,str) and value == filename:
                field_label = list(
                                    filter(lambda question: "name" in question and question['name'] == key, content))
                field_name = field_label[0]["label"][0] if len(field_label) > 0 else key
                metadata += ("\"pregunta_" + str(index) + "\": { \"nombre\": \"" + field_name +"\", "
                   + "\"file_url\": \"" + file["download_url"] + "\" }")
                if idx != len(report["_attachments"]) - 1:
                   metadata += ", "

        if len(metadata) < 3:
            for index, (key, value) in enumerate(report.items()):
                if isinstance(value,list):
                    for i in value:
                        if isinstance(i,dict):
                            for name,item in i.items():
                                if isinstance(item,str) and item == filename:
                                    field_label = list(
                                        filter(lambda question: "name" in question and question['name'] == name.split("/")[1], content))
                                    field_name = field_label[0]["label"][0] if len(field_label) > 0 else name
                                    metadata += ("\"pregunta_" + str(index) + "\": { \"nombre\": \"" + field_name +"\", "
                                       + "\"file_url\": \"" + file["download_url"] + "\" }")
                                    if idx != len(report["_attachments"]) - 1:
                                       metadata += ", "

    metadata += " }"

    return metadata
