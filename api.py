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

API_URL = "https://envoyer.io/api"

class Projects:
    
    def get_all():
        try:
            response = requests.get(API_URL+"/projects", timeout=5, headers=HEADERS)
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

    def search_projects(search_term):
            
            full_project_list = Projects.get_all()
            searched_project_list_of_ids = []
            for key in full_project_list:
                if search_term in key["name"]:
                    project_id = str(key["id"])
                    searched_project_list_of_ids.append(project_id)
            return searched_project_list_of_ids

                    
    def invite_user_to_project(email, search_term):
            
            project_list = Projects.search_projects(search_term)
            body = {
                'email' : email
            }

            for project_id in project_list:
                create_collaborator_response = requests.post(url=API_URL+"/projects/"+project_id+"/collaborators", json=body, timeout=5, headers=HEADERS)
                print(create_collaborator_response.text)