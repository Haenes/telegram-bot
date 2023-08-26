import os
import requests


API_BASE_URL = "http://127.0.0.1:8000/api"


def beatiful_date(datetime):
    datetime = datetime.split("T")
    date = datetime[0]
    time = datetime[1].split(".")[0]

    return f"{date} {time}"


def convert_project_to_url(project_name):
    headers = set_up()
    results = get_projects(headers=headers)
    projects = results["results"]

    for project in projects:
        if project["name"] == project_name:
            project_url = project["url"]
    
    return project_url


def set_up():
    token = os.environ.get("API_TOKEN")
    headers = {"Authorization": f"Token {token}"}

    return headers


def get_token(username, password):
    data = {
        "username": username,
        "password": password
	}
    r = requests.post(f"{API_BASE_URL}-token-auth/", json=data)
    token = r.json()["token"]

    os.environ["API_TOKEN"] = token


def get_projects(headers, **kwargs):
    r = requests.get(f"{API_BASE_URL}/projects", headers=headers, **kwargs)
    return r.json()


def get_project(id, header):
    r = requests.get(f"{API_BASE_URL}/projects/{id}", headers=header)
    data = r.json()
    data["created"] = beatiful_date(data["created"])

    return data


def make_project(data, headers):
    r = requests.post(f"{API_BASE_URL}/projects/", headers=headers, data=data)
    return r.status_code


def update_project(id, data, headers):
    r = requests.put(f"{API_BASE_URL}/projects/{id}/", headers=headers, data=data)
    return r.status_code


def delete_project(id, header):
    r = requests.delete(f"{API_BASE_URL}/projects/{id}", headers=header)
    return "The project was successfully deleted!"


def _all_projects():
    """ Get all projects from all pages """

    # Set headers and make first request to get first page of projects
    headers = set_up()
    results = get_projects(headers=headers)

    page = 2
    projects = []

    # While there next page with projects -> add projects from current page to projects list
    # Then make request with next page and increase page number
    while results["next"] != None:
        projects += results["results"]
        results = get_projects(headers=headers, params={"page":page})
        page += 1

    return projects


def convert_project_to_url(project_name):
    """
    Take project name -> get list of projects (list of dict's).
    Iterate over a list trying to find project with given name.
    If project is found -> get url of project and return it.
    """

    projects = _all_projects()

    for project in projects:
        if project["name"] == project_name:
            project_url = project["url"]

    # return project_url
    try:
        return project_url
    except UnboundLocalError:
        return "UnboundLocalError"


def get_issues(header, **kwargs):
    r = requests.get(f"{API_BASE_URL}/issues", headers=header, **kwargs)
    return r.json()


def get_issue(id, header):
    r = requests.get(f"{API_BASE_URL}/issues/{id}", headers=header)
    data = r.json()
    data["created"] = beatiful_date(data["created"])
    data["updated"] = beatiful_date(data["updated"])

    return data


def make_issue(data, headers):
    r = requests.post(f"{API_BASE_URL}/issues/", headers=headers, data=data)
    return r.status_code


def update_issue(id, data, headers):
    r = requests.put(f"{API_BASE_URL}/issues/{id}/", headers=headers, data=data)
    return r.status_code


def delete_issue(id, header):
    r = requests.delete(f"{API_BASE_URL}/issues/{id}", headers=header)
    return "The issue was successfully deleted!"
