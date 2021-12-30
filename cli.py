import requests
import json
import os
from dotenv import load_dotenv

#Load .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')

# Authentication headers
HEADERS = {
    "Authorization": API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
    }

GENERAL_ENDPOINT = "https://envoyer.io/api"

def get_projects():
    try:
        response = requests.get(GENERAL_ENDPOINT+"/projects", timeout=5, headers=HEADERS)
        response.raise_for_status()
        parsed = json.loads(response.text)
        parsed = parsed["projects"]
        return parsed
    except requests.exceptions.HTTPError as errh:
        print(errh)
    except requests.exceptions.ConnectionError as errc:
        print(errc)
    except requests.exceptions.Timeout as errt:
        print(errt)
    except requests.exceptions.RequestException as err:
        print(err)


def invite_user_to_project(email, project_string_match):
    project_list = get_projects()
    body = {
        'email' : email
    }

    for key in projects:
        if project_string_match in key["name"]:
            project_id = str(key["id"])
            create_collaborator_response = requests.post(url=GENERAL_ENDPOINT+"/projects/"+project_id+"/collaborators", json=body, timeout=5, headers=HEADERS)
            print(create_collaborator_response.text)

def string_match(string_expression):
    project_list = get_projects()
    for key in project_list:
        if string_expression in key["name"]:
            project_id = str(key["id"])
            print(key["name"])

