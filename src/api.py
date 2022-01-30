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

class Hooks:
    def get_hooks_by_project_id(project_id):

        get_list_response = requests.get(url=API_URL + "/projects/" + str(project_id) + "/hooks", headers=HEADERS)
        if get_list_response.status_code != 200:
            print("Issue with retrieving hooks. Exiting.")
            exit()
        elif get_list_response.status_code == 200:
            hooks = json.loads(get_list_response.text)["hooks"]
            return hooks
        else:
            pass

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


    def get_collaborators_from_search_term(search_term):

        for x in Projects.search_projects(search_term).values():
            get_collaborators_response = requests.get(url=API_URL+"/projects/"+x+"/collaborators", timeout=5, headers=HEADERS)
            parsed = json.loads(get_collaborators_response.text)
            parsed = parsed["collaborators"]
            print(parsed)

    def add_server_to_project(hostname, project_id):

        body = {
            "name": hostname,
            "connectAs": "ubuntu",
            "host": hostname,
            "port": 22,
            "phpVersion": "php80",
            "deploymentPath": "/srv/application/",
            "composerPath": "composer"
        }
        body["receivesCodeDeployments"] = True
        body["restartFpm"] = True

        request_url = API_URL+"/projects" + "/" + str(project_id) + "/servers"
        create_server_response = requests.post(url=request_url, json=body, headers=HEADERS)
        if create_server_response.status_code == 200:
            print("Successfully added server to Envoyer project")
        else:
            print("Maybe something went wrong in creating server for project.")

    
    def create_project(name, repo, health_check_url="https://my-laravel-project.com"):
        
        body = {
            "name": name,
            "provider": "github",
            "repository": repo,
            "type": "laravel-5",
            "retain_deployments": 5,
            "monitor": health_check_url,
        }
        body["composer"] = True
        body["composer_dev"] = True
        body["composer_quiet"] = False

        create_project_response = requests.post(url=API_URL+"/projects", json=body, timeout=5, headers=HEADERS)
        
        if create_project_response.status_code == 200:
            
            #If project creation is a success, send project off to set main as branch and autodeploy turned on.

            print("Success, created " + name + " project in Envoyer!")
            
            parsed_response = json.loads(create_project_response.text)
            project_object = parsed_response["project"]
            request_url=API_URL+"/projects/"+ str(project_object["id"]) + "/source"
            
            update_body = {
            "branch": "main",
            }
            update_body["push_to_deploy"] = True
            update_project_source_response = requests.put(url=request_url, json=update_body, timeout=5, headers=HEADERS)
            
            if update_project_source_response.status_code == 200:
                print("Successfully updated branch and auto-deploy setting.")
            else:
                print("Was not successful in setting branch.")
        
        else:
            print("Project not created, status code: " + str(create_project_response.status_code))
            exit()
        
        ##Method returns Project ID
        return project_object["id"]

    def delete_projects(search_term):

        print(Projects.search_projects(search_term).keys())
        print("Are you sure you want to delete these projects?")
        answer = input("Answer? Y or N \n")
        if answer == "Y":
            for x in Projects.search_projects(search_term).values():
                delete_project_response = requests.delete(url=API_URL+"/projects/"+x, headers=HEADERS)
        else:
            exit()

        return "Completed deletion. \n"

    def deploy_project(project_id):
        
        body = {
        "from": "branch",
        "branch": "main"
        }
        project_id = str(project_id)
        deploy_response = requests.post(url=API_URL + "/projects/" + project_id + "/deployments")
        if deploy_response.status_code == 200:
            print("Successfully deployed project.")
    
    def search_and_deploy_projects(search_term):
        projects_to_deploy = Projects.search_projects(search_term)
        answer = input("(Y/N) Do you want to deploy main to the following: " + str(projects_to_deploy.keys())+"\n")
        if answer == "Y":
            print(projects_to_deploy.values())
            for x in projects_to_deploy.values():
                Projects.deploy_project(str(x))
            
