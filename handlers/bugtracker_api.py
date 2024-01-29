import os
import requests
from aiogram.utils.i18n import gettext as _


API_BASE_URL = os.environ.get("API_BASE_URL")


def beatiful_date(datetime):
    """ 
    Remove unnecessary part from the received datetime

    Example: 2023-07-18T18:19:10.327000-05:00 --> 2023-07-18 18:19:10 
    """

    datetime = datetime.split("T")
    date = datetime[0]
    time = datetime[1].split(".")[0]

    return f"{date} {time}"


def get_token(username, password):
    """ 
    Gets the user token for all further requests,
    by making a POST request with the given username and password
    """

    data = {
        "username": username,
        "password": password
	}
    r = requests.post(f"{API_BASE_URL}-token-auth/", json=data)
    token = r.json()["token"]

    return token


class Translate:
    """
    A class for all InlineKeyboards that used to be Replaykeyboards, 
    but were forced to change their gender in order to be localized correctly
    """


    def __init__(self, data):
        self.data = data


    def project(self):
        favorite = {True: _("True"),
                    False: _("False")}

        starred = favorite[self.data["starred"]]

        return starred


    def issue(self):
        types = {"Bug": _("Bug"),
                 "Feature": _("Feature")}

        prioritys = {"Lowest": _("Lowest"),
                     "Low": _("Low"),
                     "Medium": _("Medium"),
                     "High": _("High"),
                     "Highest": _("Highest")}
   
        statuses = {"To do": _("To do"),
                    "In progress": _("In progress"),
                    "Done": _("Done")}
        
        type = types[self.data["type"]]
        priority = prioritys[self.data["priority"]]
        status = statuses[self.data["status"]]

        return type, priority, status


class Paginator:
    """ Class for all paginations """

    def __init__(self, headers, page):
        self.headers = headers
        self.page = page


    def next_projects(self):
        """ Next page with projects """

        results = get_projects(self.headers, params={"page":self.page})
        return results


    def previous_projects(self):
        """ Previous page with projects """

        if self.page == 1:
            results = get_projects(self.headers)
        else:
            results = get_projects(self.headers, params={"page":self.page})

        return results


    def next_issues(self):
        """ Next page with issues """

        results = get_issues(self.headers, params={"page":self.page})
        return results


    def previous_issues(self):
        """ Previous page with issues """

        if self.page == 1:
            results = get_issues(self.headers)
        else:
            results = get_issues(self.headers, params={"page":self.page})

        return results


def get_projects(headers, **kwargs):
    """ Get first page of projects via GET request """

    r = requests.get(f"{API_BASE_URL}/projects", headers=headers, **kwargs)
    return r.json()


def get_project(id, headers):
    """ Take info about single project via GET request """

    r = requests.get(f"{API_BASE_URL}/projects/{id}", headers=headers)
    data = r.json()
    data["created"] = beatiful_date(data["created"])

    return data


def make_project(data, headers):
    """ Create single project via POST request """

    r = requests.post(f"{API_BASE_URL}/projects/", headers=headers, data=data)
    return r.status_code


def update_project(id, data, headers):
    """ Update single project via PUT request"""

    r = requests.put(f"{API_BASE_URL}/projects/{id}/", headers=headers, data=data)
    return r.status_code


def delete_project(id, headers):
    """ Delete single project via DELETE request"""

    r = requests.delete(f"{API_BASE_URL}/projects/{id}", headers=headers)
    return _("The project was successfully deleted!")


def _all_projects(headers):
    """ Get all projects from all pages """

    # Set headers and make first request to get first page of projects
    results = get_projects(headers=headers)

    page = 2
    projects = []

    # If there NO next page (1 page) -> add first results into projects and return it. 
    # Otherwise while there next page with projects -> add projects from current page to projects list
    # Then make request with next page and increase page number
    if results["next"] == None:
        projects += results["results"]
    else:
        while results["next"] != None:
            projects += results["results"]
            results = get_projects(headers=headers, params={"page":page})
            page += 1

    return projects


def convert_project_to_url(headers, project_name):
    """
    Convert project name to project url (necessary for issue creation process).

    Take project name -> get list of projects (list of dict's).
    Iterate over a list trying to find project with given name.
    If project is found -> get url of project and return it.
    """

    projects = _all_projects(headers)

    for project in projects:
        if project["name"] == project_name:
            project_url = project["url"]

    try:
        return project_url
    except UnboundLocalError:
        return "UnboundLocalError"


def convert_url_to_project(headers, project_url):
    """
    Convert project name to project url (necessary for Issue info).

    Works like convert_project_to_url, but reverse
    """

    projects = _all_projects(headers)

    for project in projects:
        if project["url"] == project_url:
            project_name = project["name"]

    try:
        return project_name
    except UnboundLocalError:
        return "UnboundLocalError"


def get_issues(headers, **kwargs):
    """ Get first page of issues via GET request """

    r = requests.get(f"{API_BASE_URL}/issues", headers=headers, **kwargs)
    return r.json()


def get_issue(id, headers):
    """ Take info about single issue via GET request """

    r = requests.get(f"{API_BASE_URL}/issues/{id}", headers=headers)
    data = r.json()
    data["project"] = convert_url_to_project(headers, data["project"])
    data["created"] = beatiful_date(data["created"])
    data["updated"] = beatiful_date(data["updated"])

    return data


def make_issue(data, headers):
    """ Create single issue via POST request """

    r = requests.post(f"{API_BASE_URL}/issues/", headers=headers, data=data)
    return r.status_code


def update_issue(id, data, headers):
    """ Update single issue via PUT request"""

    r = requests.put(f"{API_BASE_URL}/issues/{id}/", headers=headers, data=data)
    return r.status_code


def delete_issue(id, headers):
    """ Delete single issue via DELETE request"""

    r = requests.delete(f"{API_BASE_URL}/issues/{id}", headers=headers)
    return _("The issue was successfully deleted!")
