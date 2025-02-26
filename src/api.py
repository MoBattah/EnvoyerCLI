import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_URL = "https://envoyer.io/api"

if not API_KEY:
    raise ValueError("API_KEY not found in environment variables.")

HEADERS = {
    "Authorization": API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

class Hooks:
    @staticmethod
    def get_hooks_by_project_id(project_id):
        """
        Retrieve hooks for a specific project.

        :param project_id: ID of the project.
        :return: A list of hooks, or an empty list if retrieval fails.
        """
        try:
            response = requests.get(f"{API_URL}/projects/{project_id}/hooks", headers=HEADERS)
            response.raise_for_status()
            return response.json().get("hooks", [])
        except requests.RequestException as exc:
            print(f"Error retrieving hooks for project {project_id}: {exc}")
            return []

class Projects:
    @staticmethod
    def get_all():
        """
        Retrieve all projects.

        :return: A list of project objects, or an empty list on failure.
        """
        try:
            response = requests.get(f"{API_URL}/projects", headers=HEADERS, timeout=5)
            response.raise_for_status()
            return response.json().get("projects", [])
        except requests.RequestException as exc:
            print(f"Error retrieving projects: {exc}")
            return []

    @staticmethod
    def search_projects(search_term):
        """
        Search for projects containing the given term in their name.

        :param search_term: Partial or full string to match project names.
        :return: Dict of {project_name: project_id} for matches.
        """
        results = {}
        all_projects = Projects.get_all()
        for project in all_projects:
            if search_term.lower() in project["name"].lower():
                results[project["name"]] = str(project["id"])
        return results

    @staticmethod
    def invite_user_to_project(email, search_term):
        """
        Invite a user (by email) to all projects matching the search term.

        :param email: Email address of the user to invite.
        :param search_term: Search term to locate projects by name.
        """
        body = {"email": email}
        matching_projects = Projects.search_projects(search_term)

        for project_id in matching_projects.values():
            try:
                url = f"{API_URL}/projects/{project_id}/collaborators"
                response = requests.post(url, json=body, headers=HEADERS, timeout=5)
                response.raise_for_status()
                print(f"Invited {email} to project ID {project_id}.")
            except requests.RequestException as exc:
                print(f"Failed to invite {email} to project ID {project_id}: {exc}")

    @staticmethod
    def get_collaborators_from_search_term(search_term):
        """
        Print collaborators for all projects matching the search term.

        :param search_term: Search term to locate projects by name.
        """
        matching_projects = Projects.search_projects(search_term)
        for project_id in matching_projects.values():
            try:
                url = f"{API_URL}/projects/{project_id}/collaborators"
                response = requests.get(url, headers=HEADERS, timeout=5)
                response.raise_for_status()
                collaborators = response.json().get("collaborators", [])
                print(f"Collaborators for project ID {project_id}: {collaborators}")
            except requests.RequestException as exc:
                print(f"Failed to retrieve collaborators for project ID {project_id}: {exc}")

    @staticmethod
    def add_server_to_project(hostname, project_id):
        """
        Add a new server to a specific Envoyer project.

        :param hostname: Hostname of the server.
        :param project_id: Envoyer project ID.
        """
        body = {
            "name": hostname,
            "connectAs": "ubuntu",
            "host": hostname,
            "port": 22,
            "phpVersion": "php80",
            "deploymentPath": "/srv/application/",
            "composerPath": "composer",
            "receivesCodeDeployments": True,
            "restartFpm": True
        }
        url = f"{API_URL}/projects/{project_id}/servers"

        try:
            response = requests.post(url, json=body, headers=HEADERS)
            response.raise_for_status()
            print(f"Successfully added server '{hostname}' to project {project_id}.")
        except requests.RequestException as exc:
            print(f"Error adding server '{hostname}' to project {project_id}: {exc}")

    @staticmethod
    def create_project(name, repo, health_check_url="https://my-laravel-project.com"):
        """
        Create a new Envoyer project, then set its default branch to 'main' with auto-deploy.

        :param name: Name of the new project.
        :param repo: GitHub repository URL.
        :param health_check_url: Health check URL for Envoyer monitoring.
        :return: The newly created project's ID, or None on failure.
        """
        body = {
            "name": name,
            "provider": "github",
            "repository": repo,
            "type": "laravel-5",
            "retain_deployments": 5,
            "monitor": health_check_url,
            "composer": True,
            "composer_dev": True,
            "composer_quiet": False
        }

        try:
            create_project_response = requests.post(
                f"{API_URL}/projects",
                json=body,
                headers=HEADERS,
                timeout=5
            )
            create_project_response.raise_for_status()
            print(f"Success: Created '{name}' project in Envoyer!")

            project_object = create_project_response.json().get("project")
            if not project_object:
                print("Project data not returned by Envoyer.")
                return None

            # Update project's default branch and enable push-to-deploy
            request_url = f"{API_URL}/projects/{project_object['id']}/source"
            update_body = {"branch": "main", "push_to_deploy": True}

            update_response = requests.put(request_url, json=update_body, headers=HEADERS, timeout=5)
            if update_response.status_code == 200:
                print("Successfully set branch to 'main' and enabled auto-deploy.")
            else:
                print("Failed to set branch to 'main' or enable auto-deploy.")

            return project_object["id"]
        except requests.RequestException as exc:
            print(f"Project creation failed: {exc}")
            return None

    @staticmethod
    def delete_projects(search_term):
        """
        Delete all projects matching the given search term, upon user confirmation.

        :param search_term: String to match project names.
        :return: Status message about the deletion process.
        """
        matching_projects = Projects.search_projects(search_term)
        if not matching_projects:
            return "No projects found to match the search term."

        print("The following projects will be deleted:")
        for name in matching_projects:
            print(f"- {name}")

        answer = input("Are you sure you want to delete these projects? [Y/N]: ")
        if answer.lower() == "y":
            for project_id in matching_projects.values():
                try:
                    response = requests.delete(f"{API_URL}/projects/{project_id}", headers=HEADERS)
                    response.raise_for_status()
                    print(f"Deleted project ID {project_id}.")
                except requests.RequestException as exc:
                    print(f"Failed to delete project ID {project_id}: {exc}")
            return "Deletion completed."
        else:
            return "Deletion aborted by user."

    @staticmethod
    def deploy_project(project_id):
        """
        Trigger a deployment from the 'main' branch on the specified project.

        :param project_id: Envoyer project ID.
        """
        body = {
            "from": "branch",
            "branch": "main"
        }
        url = f"{API_URL}/projects/{project_id}/deployments"

        try:
            response = requests.post(url, json=body, headers=HEADERS)
            response.raise_for_status()
            print(f"Successfully deployed project {project_id} from 'main'.")
        except requests.RequestException as exc:
            print(f"Deployment failed for project {project_id}: {exc}")

    @staticmethod
    def search_and_deploy_projects(search_term):
        """
        Search for all projects matching the term and deploy each from 'main'.

        :param search_term: String to match project names.
        """
        matching_projects = Projects.search_projects(search_term)
        if not matching_projects:
            print("No matching projects found for deployment.")
            return

        print("The following projects will be deployed from 'main':")
        for name in matching_projects:
            print(f"- {name}")

        answer = input("Do you want to deploy these projects? [Y/N]: ")
        if answer.lower() == "y":
            for project_id in matching_projects.values():
                Projects.deploy_project(project_id)
        else:
            print("Deployment cancelled.")
