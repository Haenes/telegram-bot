import os
import requests


API_BASE_URL = "http://127.0.0.1:8000/api"


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
    return r.json()


def get_issues(header, **kwargs):
    r = requests.get(f"{API_BASE_URL}/issues", headers=header, **kwargs)
    return r.json()


def get_issue(id, header):
    r = requests.get(f"{API_BASE_URL}/issues/{id}", headers=header)
    return r.json()
