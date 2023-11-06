from functools import partial

def build_question_metadata(idx, field_name, download_url):
    return '"pregunta_{idx}": {{"nombre": "{field_name}", "file_url": "{download_url}"}}'.format(idx=idx, field_name=field_name, download_url=download_url)

def field_label_by_key(key, content):
    return list(filter(lambda question: "name" in question and question['name'] == key, content))

def get_field_name(key, field_label):
    return field_label[0]["label"][0] if len(field_label) > 0 else key

def get_metadata_by_question(content, download_url, t):
    field_label = field_label_by_key(t[1][0], content)
    field_name = get_field_name(t[1][0], field_label)
    question = build_question_metadata(str(t[0]), field_name, download_url)
    return question

# def add_attachments(report,content):
#     """
#         Add attachment url to metadata as a string

#         Parameters:
#             report (dict):  A dict containing the report data
#                             of the survey for a specific device
#             content (list): A list containing info of the survey.

#         Returns:
#             metadata (string):  A string containing the attachment urls
#                                 in a json structure.
#      """

#     metadata = "{ "
#     for idx, file in enumerate(report["_attachments"]):
#         """
#             Iterate through the attachments to add the file
#             url to the metadata field of deployment
#           """
#         url = file["download_url"]
#         filename = file["filename"].split("/")[4]
#         items = [(index, item) for index, item in enumerate(report.items())]
#         filter_by_filename = list(filter(lambda t: isinstance(t[1][1], str) and t[1][1] == filename, items))
#         get_question = partial(get_metadata_by_question, content, url)
#         questions = list(map(get_question, filter_by_filename))
#         metadata += ",".join(questions)
#         if idx != len(report["_attachments"]) - 1:
#             metadata += ","

#         if len(metadata) < 3:
#             all_items = []
#             for index, (key, value) in enumerate(report.items()):
#                 if isinstance(value,list):
#                     all_questions = []
#                     for i in value:
#                         if isinstance(i,dict):
#                             questions = []
#                             for name, item in i.items():
#                                 if isinstance(item,str) and item == filename:
#                                     key = name.split("/")[1]
#                                     field_label = field_label_by_key(key, content)
#                                     field_name = get_field_name(key, field_label)
#                                     questions.append(build_question_metadata(str(index), field_name, url))
#                             all_questions.append(",".join(questions))
#                     all_items.append(",".join(all_questions))
#             metadata += ",".join(all_items)
#     metadata += "}"

#     return metadata


def filter_by_filename(filename, items):
    return list(filter(lambda t: isinstance(t[1][1], str) and t[1][1] == filename, items))

def add_attachments(report, content):
    attachments = [(i, f) for i, f in enumerate(report['_attachments'])]
    items = [(j, it) for j, it in enumerate(report.items())]
    questions = []
    for idx, _file in attachments:
        url = _file['download_url']
        filename = _file['filename'].split('/')[4]
        filtered = filter_by_filename(filename, items)
        get_question = partial(get_metada_by_question, content, url)
        qs = list(map(get_question, filtered))
        if qs:
            questions.extend(qs)

        if not qs:
            all_items = []
            for index, (key, value) in items:
                if isinstance(value, list):
                    all_questions = []
                    for i in value:
                        if isinstance(i, dict):
                            qs = []
                            for name, item in i.items():
                                if isinstance(item, str) and item == filename:
                                    key = name.split('/')[1]
                                    field_label = field_label_by_key(key, content)
                                    field_name = get_field_name(key, field_label)
                                    qs.append(build_question_metadata(str(index), field_name, url))
                            if qs:
                                all_questions.extend(qs)
                    if all_questions:
                        all_items.extend(all_questions)
            if all_items:
                questions.extend(all_items)
        metadata = '{' + ','.join(questions) + '}'
        return metadata
