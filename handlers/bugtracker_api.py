import os
import requests


API_BASE_URL = "http://127.0.0.1:8000/api"


def beatiful_date(datetime):
    datetime = datetime.split("T")
    date = datetime[0]
    time = datetime[1].split(".")[0]

    return f"{date} {time}"


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


def get_issues(header, **kwargs):
    r = requests.get(f"{API_BASE_URL}/issues", headers=header, **kwargs)
    return r.json()


def get_issue(id, header):
    r = requests.get(f"{API_BASE_URL}/issues/{id}", headers=header)
    data = r.json()
    data["created"] = beatiful_date(data["created"])
    data["updated"] = beatiful_date(data["updated"])

    return data


def delete_issue(id, header):
    r = requests.delete(f"{API_BASE_URL}/issues/{id}", headers=header)
    return "The issue was successfully deleted!"
