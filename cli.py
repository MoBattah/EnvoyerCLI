import requests
import json
import os
from dotenv import load_dotenv
import projects

#Load .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')

# Authentication headers
HEADERS = {
    "Authorization": API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
    }


API_URL = "https://envoyer.io/api"


def invite_user_to_project(email, project_string_match):
    project_list = get_projects()
    body = {
        'email' : email
    }

    for key in projects:
        if project_string_match in key["name"]:
            project_id = str(key["id"])
            create_collaborator_response = requests.post(url=API_URL+"/projects/"+project_id+"/collaborators", json=body, timeout=5, headers=HEADERS)
            print(create_collaborator_response.text)
