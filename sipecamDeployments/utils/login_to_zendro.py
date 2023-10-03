import os
import requests

def login_to_zendro():
    """
    Tries a login to zendro and returns a session
    object to be able to make requests.

    Returns: 
        session (Session):  A session object to make 
                            requests to zendro.
    """
    # login to zendro
    auth = {
        "username": os.getenv("ZENDRO_USER"),
        "password": os.getenv("ZENDRO_PASSWORD"),
    }
    
    login = requests.post(os.getenv("ZENDRO_URL") + "/login",data=auth)

    # se crea un objeto de Session para hacer requests
    session = requests.Session()
    # se establece bearer token
    session.headers.update({'Authorization': 'Bearer ' + login.json()['token']})

    return session