import requests
import json
import os
from dotenv import load_dotenv

#Load .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')
API_URL = "https://envoyer.io/api"

# Authentication headers
HEADERS = {
    "Authorization": API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
    }



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
            
            searched_project_list_of_names_and_ids = {}
            for key in Projects.get_all():
                if search_term in key["name"]:
                    searched_project_list_of_names_and_ids[key["name"]] = str(key["id"])
            return searched_project_list_of_names_and_ids

                    
    def invite_user_to_project(email, search_term):      
            
            body = {
                'email' : email
            }

            for x in Projects.search_projects(search_term).values():
                create_collaborator_response = requests.post(url=API_URL+"/projects/"+x+"/collaborators", json=body, timeout=5, headers=HEADERS)

