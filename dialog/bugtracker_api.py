import os
from aiohttp import ClientSession
from datetime import datetime
from dotenv import load_dotenv

from aiogram.utils.i18n import gettext as _
from babel.dates import format_datetime, get_timezone


load_dotenv()
API_LOGIN_URL = os.environ.get("API_LOGIN_URL")
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


async def get_token(
    session: ClientSession,
    email: str,
    password: str
) -> str | dict[str, str]:
    data = {"username": email, "password": password}
    url = f"{API_LOGIN_URL}"

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


def get_translated_timezone(timezone: str):
    timezones = {
        "UTC": "UTC",
        "Moscow": _("Moscow"),
        "Vladivostok": _("Vladivostok")
    }
    return timezones[timezone]


class API:

    def __init__(self):
        self.UNIQUE_ERRORS: dict = ...

    @staticmethod
    async def get_items(
        session: ClientSession,
        headers: dict,
        params: dict | None = None
    ) -> dict | str: ...

    @staticmethod
    async def pagination_next(
        session: ClientSession,
        headers: dict,
        page: str | int
    ) -> dict: ...

    @staticmethod
    async def pagination_back(
        session: ClientSession,
        headers: dict,
        page: str | int
    ) -> dict: ...

    @staticmethod
    async def get_item(
        session: ClientSession,
        id: str | int,
        headers: dict,
        language: str | None = None,
        timezone: str | None = None
    ) -> dict: ...

    async def create_item(
        self,
        session: ClientSession,
        id: str | int,
        headers: dict,
        data: dict
    ) -> dict: ...

    async def edit_item(
        self,
        session: ClientSession,
        id: str | int,
        headers: dict,
        data: dict
    ) -> dict: ...

    @staticmethod
    async def delete_item(
        session: ClientSession,
        id: str | int,
        headers: dict
    ) -> dict: ...


class Project(API):

    def __init__(self):
        self.UNIQUE_ERRORS = {
            "project_name": _("Project with this name already exist!"),
            "project_key": _("Project with this key already exist!")
        }

    @staticmethod
    def get_translated_favorite(favorite: bool) -> str:
        is_favorite = {True: _("True"), False: _("False")}
        return is_favorite[favorite]

    @staticmethod
    async def get_items(
        session,
        headers: dict,
        params: dict | None = None
    ) -> dict | str:
        """ Get first (or N) page of projects via GET request. """
        url = f"{API_BASE_URL}"

        async with session.get(url, headers=headers, params=params) as r:
            results = await r.json()

            if "count" not in results:
                return _("You don't have any project!")
            return results

    async def pagination_next(
        self,
        session: ClientSession,
        headers: dict,
        page: str | int
    ) -> dict:
        return await self.get_items(session, headers, {"page": page})

    async def pagination_back(
        self,
        session: ClientSession,
        headers: dict,
        page: str | int
    ) -> dict:
        return await self.get_items(session, headers, {"page": page})

    @staticmethod
    async def get_item(
        session,
        id: str | int,
        headers: dict,
        language: str | None = None,
        timezone: str | None = None
    ) -> dict:
        """ Take info about project via GET request. """
        url = f"{API_BASE_URL}/{id}"

        if language and timezone:
            async with session.get(url, headers=headers) as r:

                data = await r.json()
                data["created"] = _format_date(
                    datetime_to_format=data["created"],
                    language=language,
                    timezone=timezone
                )
                data["updated"] = _format_date(
                    datetime_to_format=data["updated"],
                    language=language,
                    timezone=timezone
                )
                return data

        async with session.get(url, headers=headers) as r:
            return await r.json()

    async def create_item(self, session, headers: dict, data: dict) -> dict:
        """ Create project via POST request. """
        url = f"{API_BASE_URL}"

        async with session.post(url, json=data, headers=headers) as r:

            if r.status == 201:
                return {"success": _("The project has been created!")}

            results = await r.json()

            if "detail" in results:
                match results["detail"]:
                    case "Project with this name already exist!":
                        return {"error_name": self.UNIQUE_ERRORS["project_name"]}
                    case "Project with this key already exist!":
                        return {"error_key": self.UNIQUE_ERRORS["project_key"]}
            return {"error": _("Error, the project was NOT created!")}

    async def edit_item(
        self,
        session,
        id: str | int,
        headers: dict,
        data: dict
    ) -> dict:
        """ Update project via PATCH request. """
        url = f"{API_BASE_URL}/{id}"

        async with session.patch(url, json=data, headers=headers) as r:
            if r.status == 200:
                return {"success": _("The project has been updated!")}

            results = await r.json()

            if "detail" in results:
                match results["detail"]:
                    case "Project with this name already exist!":
                        return {"error_name": self.UNIQUE_ERRORS["project_name"]}
                    case "Project with this key already exist!":
                        return {"error_key": self.UNIQUE_ERRORS["project_key"]}
            return {"error": _("Error, the project was NOT updated!")}

    @staticmethod
    async def delete_item(session, id: str | int, headers: dict) -> dict:
        """ Delete project via DELETE request. """
        url = f"{API_BASE_URL}/{id}"

        async with session.delete(url, headers=headers) as r:
            match r.status:
                case 200:
                    return {"success": _(
                        "The project was successfully deleted!"
                    )}
                case 400:
                    return {"error": _("The project was deleted earlier.")}
                case _:
                    return {"error": _(
                        "Error, the project was not deleted!"
                    )}


class Issue(API):

    def __init__(self):
        self.UNIQUE_ERRORS = {
            "issue_title": _("Issue with this title already exist!")
        }

    @staticmethod
    def get_translated_fields(issue: dict) -> tuple[str, str, str]:
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

        type = types[issue["type"]]
        priority = prioritys[issue["priority"]]
        status = statuses[issue["status"]]

        return type, priority, status

    @staticmethod
    async def get_items(
        session: ClientSession,
        headers: dict,
        project_id: str | int,
        params: dict | None = None
    ) -> dict | str:
        """ Get first (or N) page of issues via GET request. """
        url = f"{API_BASE_URL}/{project_id}/issues"

        async with session.get(url, headers=headers, params=params) as r:
            results = await r.json()

            if "count" not in results:
                return _("You don't have any issues for this project!")
            return results

    async def pagination_next(
        self,
        session: ClientSession,
        headers: dict,
        project_id: str | int,
        page: str | int
    ) -> dict:
        return await self.get_items(
            session=session,
            headers=headers,
            project_id=project_id,
            params={"page": page}
        )

    async def pagination_back(
        self,
        session: ClientSession,
        headers: dict,
        project_id: str | int,
        page: str | int
    ) -> dict:
        return await self.get_items(
            session=session,
            headers=headers,
            project_id=project_id,
            params={"page": page}
        )

    @staticmethod
    async def get_item(
        session: ClientSession,
        id: str | int,
        project_id: str | int,
        headers: dict,
        language: str | None = None,
        timezone: str | None = None
    ) -> dict:
        """ Take info about issue via GET request. """
        url = f"{API_BASE_URL}/{project_id}/issues/{id}"

        if language and timezone:
            async with session.get(url, headers=headers) as r:
                data = await r.json()
                data["created"] = _format_date(
                    datetime_to_format=data["created"],
                    language=language,
                    timezone=timezone
                )
                data["updated"] = _format_date(
                    datetime_to_format=data["updated"],
                    language=language,
                    timezone=timezone
                )
                return data

        async with session.get(url, headers=headers) as r:
            return await r.json()

    async def create_item(
        self,
        session: ClientSession,
        headers: dict,
        project_id: str | int,
        data: dict,
    ) -> dict:
        """ Create issue via POST request. """
        url = f"{API_BASE_URL}/{project_id}/issues"

        async with session.post(url, json=data, headers=headers) as r:
            if r.status == 201:
                return {"success": _("The issue has been created!")}

            results = await r.json()

            if "detail" in results:
                return {"error_title": self.UNIQUE_ERRORS["issue_title"]}
            return {"error": _("Error, the issue was NOT created!")}

    async def edit_item(
        self,
        session: ClientSession,
        id: str | int,
        headers: dict,
        project_id: str | int,
        data: dict
    ) -> dict:
        """ Update issue via PATCH request. """
        url = f"{API_BASE_URL}/{project_id}/issues/{id}"

        async with session.patch(url, json=data, headers=headers) as r:
            if r.status == 200:
                return {"success": _("The issue has been updated!")}

            results = await r.json()

            if "detail" in results:
                return {"error_title": self.UNIQUE_ERRORS["issue_title"]}
            return {"error": _("Error, the issue was NOT updated!")}

    @staticmethod
    async def delete_item(
        session: ClientSession,
        id: str | int,
        project_id: str | int,
        headers: dict
    ) -> dict:
        """ Delete issue via DELETE request. """
        url = f"{API_BASE_URL}/{project_id}/issues/{id}"

        async with session.delete(url, headers=headers) as r:
            match r.status:
                case 200:
                    return {"success": _("The issue was successfully deleted!")}
                case 400:
                    return {"error": _("The issue was deleted earlier.")}
                case _:
                    return {"error": _("Error, the issue was not deleted!")}
