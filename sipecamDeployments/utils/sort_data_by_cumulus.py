def sort_data_by_cumulus(data):
    """
     Sort data by submitted_by field, which holds
     the cumulus number (or id),

     Parameters:
        data (list):    A list containing the report
                        data.

     Returns:
        (dict):  A dict containg the data sorted by the 
                cumulus id.
     """

    sorted_data = {}
    for d in data:
        if d["user"] not in sorted_data:
            sorted_data[d["user"]] = []
            sorted_data[d["user"]].append(d)
        else:
            sorted_data[d["user"]].append(d)
    
    return sorted_data
        