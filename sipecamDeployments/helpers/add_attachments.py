from functools import partial

def build_question_metadata(idx, field_name, download_url):
    return '"pregunta_{idx}": {{"nombre": "{field_name}", "file_url": "{download_url}"}}'.format(idx=idx, field_name=field_name, download_url=download_url)

def field_label_by_key(key, content):
    return list(filter(lambda question: "name" in question and question["name"] == key, content))

def get_field_name(key, field_label):
    return field_label[0]["label"][0] if len(field_label) > 0 else key

def get_metadata_by_question(content, download_url, t):
    field_label = field_label_by_key(t[1][0], content)
    field_name = field_label_by_key(t[1][0], field_label)
    question = build_question_metadata(str(t[0]), field_name, download_url)
    return question

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
        items = [(index, item) for index, item in enumerate(report.items())]
        filter_by_filename = list(filter(lambda t: isinstance(t[1][1], str) and t[1][1] == filename, items))
        get_question = partial(get_metadata_by_question, content, file["download_url"])
        questions = list(map(get_question, filter_by_filename))
        metadata += ", ".join(questions)

        if len(metadata) < 3:
            for index, (key, value) in enumerate(report.items()):
                if isinstance(value,list):
                    for i in value:
                        if isinstance(i,dict):
                            metadata += ", "
                            questions = []
                            for i, (name,item) in enumerate(i.items()):
                                if isinstance(item,str) and item == filename:
                                    field_label = field_label_by_key(name.split("/")[1], content)
                                    field_name = get_field_name(name, field_label)
                                    questions.append(build_question_metadata(str(index), field_name, file["download_url"]))
                            metadata += ",".join(questions)
    metadata += " }"

    return metadata
