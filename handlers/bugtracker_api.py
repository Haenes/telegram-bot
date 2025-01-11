import os
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

from aiogram.utils.i18n import gettext as _
from babel.dates import format_datetime, get_timezone


load_dotenv()
API_BASE_URL = os.environ.get("API_BASE_URL")


def _format_date(datetime_to_format: str, language: str, timezone: str) -> str:
    """ Remove unnecessary part from the received datetime.

    And convert it by language and timezone
    Example: 2023-07-18T18:19:10.327000-05:00 --> 2023-07-18 18:19:10
    """

    format = "%Y-%m-%dT%H:%M:%S.%fZ"
    dt = datetime.strptime(datetime_to_format, format)
    dt = format_datetime(dt, "short",  get_timezone(timezone), language)

    return dt


async def get_token(email: str, password: str) -> str | dict[str, str]:
    data = {"username": email, "password": password}
    url = f"{API_BASE_URL}/auth/bearer/login"

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.post(url, data=data) as r:
            if r.status == 400:
                error = await r.json()

                match error["detail"]:
                    case "LOGIN_BAD_CREDENTIALS":
                        return {"error": _("Invalid email/password!")}
                    case "LOGIN_USER_NOT_VERIFIED":
                        return {"error": _("Not verified! Check email.")}

            res = await r.json()

            if "access_token" in res:
                return res["access_token"]


class Translate:
    """
    A class for all InlineKeyboards that used to be Replaykeyboards,
    but were forced to change their gender in order to be localized correctly
    """

    def __init__(self, data: dict | str):
        self.data = data

    def project(self) -> str:
        favorite = {True: _("True"), False: _("False")}
        starred = favorite[self.data["starred"]]
        return starred

    def timezones(self) -> str:
        timezone = {
            "UTC": "UTC",
            "Moscow": _("Moscow"),
            "Vladivostok": _("Vladivostok")
        }
        return timezone[self.data]

    def issue(self) -> tuple[str, str, str]:
        types = {"Bug": _("Bug"), "Feature": _("Feature")}
        prioritys = {
            "Lowest": _("Lowest"),
            "Low": _("Low"),
            "Medium": _("Medium"),
            "High": _("High"),
            "Highest": _("Highest")
        }
        statuses = {
            "To do": _("To do"),
            "In progress": _("In progress"),
            "Done": _("Done")
        }

        type = types[self.data["type"]]
        priority = prioritys[self.data["priority"]]
        status = statuses[self.data["status"]]

        return type, priority, status


class Paginator:
    """ Class for all paginations. """

    def __init__(self, headers: dict, page: str | int):
        self.headers = headers
        self.page = page

    async def next_projects(self) -> dict:

        results = await get_projects(self.headers, {"page": self.page})
        return results

    async def previous_projects(self) -> dict:

        if self.page == 1:
            results = await get_projects(self.headers)
        else:
            results = await get_projects(self.headers, {"page": self.page})
        return results

    async def next_issues(self, project_id) -> dict:
        results = await get_issues(
            headers=self.headers,
            project_id=project_id,
            params={"page": self.page}
        )

        return results

    async def previous_issues(self, project_id) -> dict:

        if self.page == 1:
            results = await get_issues(self.headers, project_id)
        else:
            results = await get_issues(
                headers=self.headers,
                project_id=project_id,
                params={"page": self.page}
            )

        return results


async def get_projects(headers: dict, params: dict | None = None) -> dict:
    """ Get first (or N) page of projects via GET request. """
    url = f"{API_BASE_URL}/projects"

    # async with aiohttp.ClientSession(trust_env=True) as session:
    #     if params:
    #         async with session.get(url, headers=headers, params=params) as r:
    #             return await r.json()

    #     async with session.get(url, headers=headers) as r:
    #         results = await r.json()

    #         if "You don't have any project!" in results:
    #             return _("You don't have any project!")
    #         return results
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url, headers=headers, params=params) as r:
            results = await r.json()

            if "count" not in results:
                "SGFSDFSDF"
                return _("You don't have any project!")
            return results


async def get_project(
    id: str | int,
    headers: dict,
    language: str | None = None,
    timezone: str | None = None
) -> dict:
    """ Take info about project via GET request. """
    url = f"{API_BASE_URL}/projects/{id}"

    async with aiohttp.ClientSession(trust_env=True) as session:
        if language and timezone:
            async with session.get(url, headers=headers) as r:
                data = await r.json()
                data["created"] = _format_date(
                    data["created"],
                    language,
                    timezone
                )
                data["updated"] = _format_date(
                    data["updated"],
                    language,
                    timezone
                )
                return data

        async with session.get(url, headers=headers) as r:
            return await r.json()


async def make_project(headers: dict, data: dict) -> str:
    """ Create project via POST request. """
    UNIQUE_ERRORS = {
        "project_name": _("Project with this name already exist!"),
        "project_key": _("Project with this key already exist!")
    }
    url = f"{API_BASE_URL}/projects"

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.post(url, json=data, headers=headers) as r:
            if r.status == 201:
                return _("The project has been successfully created!")

            results = await r.json()

            if "detail" in results:
                match results["detail"]:
                    case "Project with this name already exist!":
                        return UNIQUE_ERRORS["project_name"]
                    case "Project with this key already exist!":
                        return UNIQUE_ERRORS["project_key"]
            return _("An error occurred, the project was NOT created!")


async def update_project(id: str | int, headers: dict, data: dict) -> str:
    """ Update project via PATCH request. """
    UNIQUE_ERRORS = {
        "project_name": _("Project with this name already exist!"),
        "project_key": _("Project with this key already exist!")
    }
    url = f"{API_BASE_URL}/projects/{id}"

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.patch(url, json=data, headers=headers) as r:
            if r.status == 200:
                return _("The project has been successfully updated!")

            results = await r.json()

            if "detail" in results:
                match results["detail"]:
                    case "Project with this name already exist!":
                        return UNIQUE_ERRORS["project_name"]
                    case "Project with this key already exist!":
                        return UNIQUE_ERRORS["project_key"]
            return _("An error occurred, the project was NOT updated!")


async def delete_project(headers: dict, id: str | int) -> str:
    """ Delete project via DELETE request. """
    url = f"{API_BASE_URL}/projects/{id}"

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.delete(url, headers=headers) as r:
            match r.status:
                case 200:
                    return _("The project was successfully deleted!")
                case 400:
                    return _("The project was deleted earlier.")
                case _:
                    return _(
                        "An error occurred, the project was not deleted!"
                    )


async def get_issues(
    headers: dict,
    project_id: str | int,
    params: dict | None = None
) -> dict:
    """ Get first (or N) page of issues via GET request. """
    url = f"{API_BASE_URL}/projects/{project_id}/issues"

    # async with aiohttp.ClientSession(trust_env=True) as session:
    #     if params:
    #         async with session.get(url, headers=headers, params=params) as r:
    #             return await r.json()
    #     async with session.get(url, headers=headers) as r:
    #         results = await r.json()

    #         if "You don't have any issues for this project!" in results:
    #             return _("You don't have any issues for this project!")
    #         return results

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(url, headers=headers, params=params) as r:
            results = await r.json()

            if "count" not in results:
                return _("You don't have any issues for this project!")
            return results


async def get_issue(
    id: str | int,
    project_id: str | int,
    headers: dict,
    language: str | None = None,
    timezone: str | None = None
) -> dict:
    """ Take info about issue via GET request. """
    url = f"{API_BASE_URL}/projects/{project_id}/issues/{id}"

    async with aiohttp.ClientSession(trust_env=True) as session:
        if language and timezone:
            async with session.get(url, headers=headers) as r:
                data = await r.json()
                print("DATA", data)
                data["created"] = _format_date(
                    data["created"],
                    language,
                    timezone
                )
                data["updated"] = _format_date(
                    data["updated"],
                    language,
                    timezone
                )
                return data

        async with session.get(url, headers=headers) as r:
            return await r.json()


async def make_issue(data: dict, project_id: str | int, headers: dict) -> str:
    """ Create issue via POST request. """
    url = f"{API_BASE_URL}/projects/{project_id}/issues"
    UNIQUE_ERRORS = {
        "issue_title": _("Issue with this title already exist!")
    }

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.post(url, json=data, headers=headers) as r:
            if r.status == 201:
                return _("The issue has been successfully created!")

            results = await r.json()

            if "detail" in results:
                return UNIQUE_ERRORS["issue_title"]
            return _("An error occurred, the project was NOT created!")


async def update_issue(
    id: str | int,
    project_id: str | int,
    data: dict,
    headers: dict
) -> str:
    """ Update issue via PATCH request. """
    url = f"{API_BASE_URL}/projects/{project_id}/issues/{id}"
    UNIQUE_ERRORS = {
        "issue_title": _("Issue with this title already exist!")
    }

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.patch(url, json=data, headers=headers) as r:
            if r.status == 200:
                return _("The issue has been successfully updated!")

            results = await r.json()

            if "detail" in results:
                return UNIQUE_ERRORS["issue_title"]
            return _("An error occurred, the issue was NOT updated!")


async def delete_issue(
    id: str | int,
    project_id: str | int,
    headers: dict
) -> str:
    """ Delete issue via DELETE request. """
    url = f"{API_BASE_URL}/projects/{project_id}/issues/{id}"

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.delete(url, headers=headers) as r:
            match r.status:
                case 200:
                    return _("The issue was successfully deleted!")
                case 400:
                    return _("The issue was deleted earlier.")
                case _:
                    return _("An error occurred, the issue was not deleted!")
