import os
import asyncio
import aiohttp
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv

from aiogram.utils.i18n import gettext as _

from babel.dates import format_datetime, get_timezone


load_dotenv()
API_BASE_URL = os.environ.get("API_BASE_URL")


async def latest_key(headers: dict, project_id: int):
    """ Returns a latest key for issue related with project

    Example 1: if the project already has two issues: latest key = 2
    Example 2: if the project doesn't have issues yet: latest key = 0
    """
    projects = []
    keys = []

    async with aiohttp.ClientSession() as session:
        preresults = await get_issues(session, headers=headers)
        results = preresults["results"]

        for issue in results:
            project = issue["project"].removeprefix(
                f"{API_BASE_URL}/projects/"
                )[0]
            projects.append(project)

            if int(project) == project_id:
                keys.append(issue["key"])
            elif project_id not in projects:
                keys.append(0)

        return max(keys)


def _beautiful_date(datetime_to_format: str, language: str, timezone: str):
    """Remove unnecessary part from the received datetime.

    And convert it by language and timezone
    Example: 2023-07-18T18:19:10.327000-05:00 --> 2023-07-18 18:19:10
    """

    format = "%Y-%m-%dT%H:%M:%S.%fZ"
    dt = datetime.strptime(datetime_to_format, format)
    dt = format_datetime(dt, "short",  get_timezone(timezone), language)

    return dt


async def get_token(session, username: str, password: str):
    """Gets the user token for all further requests,

    by making a POST request with the given username and password
    """

    data = {"username": username, "password": password}
    url = f"{API_BASE_URL}-token-auth/"

    async with session.post(url, json=data) as r:
        res = await r.json()
        return res["token"]


class Translate:
    """A class for all InlineKeyboards that used to be Replaykeyboards,

    but were forced to change their gender in order to be localized correctly
    """

    def __init__(self, data: Dict | str):
        self.data = data

    def project(self):
        favorite = {True: _("True"), False: _("False")}

        starred = favorite[self.data["starred"]]

        return starred

    def timezones(self):
        timezone = {
            "UTC": "UTC",
            "Moscow": _("Moscow"),
            "Vladivostok": _("Vladivostok")
            }

        return timezone[self.data]

    def issue(self):
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
    """ Class for all paginations """

    def __init__(self, headers, page):
        self.headers = headers
        self.page = page

    async def next_projects(self, session, **kwargs):
        """ Next page with projects """

        results = await get_projects(
            session=session, headers=self.headers,
            params={"page": self.page}
            )
        return results

    async def previous_projects(self, session, **kwargs):
        """ Previous page with projects """

        if self.page == 1:
            results = await get_projects(session, self.headers)
        else:
            results = await get_projects(
                session=session, headers=self.headers,
                params={"page": self.page}
                )

        return results

    async def next_issues(self, session, **kwargs):
        """ Next page with issues """

        results = await get_issues(
            session=session, headers=self.headers,
            params={"page": self.page}
            )

        return results

    async def previous_issues(self, session, **kwargs):
        """ Previous page with issues """

        if self.page == 1:
            results = await get_issues(session, self.headers)
        else:
            results = await get_issues(
                session=session, headers=self.headers,
                params={"page": self.page}
                )

        return results


async def get_projects(session, headers, **kwargs):
    """ Get first (or N) page of projects via GET request """

    url = f"{API_BASE_URL}/projects/"
    try:
        # This block is executing when we
        # want to get N page of projects.
        async with session.get(
            url, headers=headers,
            params=kwargs["params"]
        ) as r:
            return await r.json()
    except KeyError:
        async with session.get(url, headers=headers) as r:
            return await r.json()


async def get_project(session, headers, id, **kwargs):
    """ Take info about single project via GET request """

    try:
        language, timezone = kwargs["language"], kwargs["timezone"]

        url = f"{API_BASE_URL}/projects/{id}/"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
            data["created"] = _beautiful_date(
                data["created"],
                language,
                timezone
                )
            return data
    except KeyError:
        url = f"{API_BASE_URL}/projects/{id}/"
        async with session.get(url, headers=headers) as r:
            return await r.json()


async def make_project(session, headers, data, **kwargs):
    """ Create single project via POST request """

    url = f"{API_BASE_URL}/projects/"
    async with session.post(url, data=data, headers=headers) as r:
        return r.status


async def update_project(session, headers, id, data, **kwargs):
    """ Update single project via PUT request"""

    url = f"{API_BASE_URL}/projects/{id}/"
    async with session.put(url, data=data, headers=headers) as r:
        return r.status


async def delete_project(session, headers, id, **kwargs):
    """ Delete single project via DELETE request"""

    url = f"{API_BASE_URL}/projects/{id}/"
    async with session.delete(url, headers=headers) as r:
        if r.status == 204:
            return _("The project was successfully deleted!")
        # TODO: Add else scenario


async def _all_projects(headers):
    """ Get all projects from all pages """

    # Set headers and make first request to get first page of projects.

    # The creation of a new session is necessary, because
    # I don't see a way to throw into the get_projects()
    # created in the main() session.

    async with aiohttp.ClientSession() as session:
        results = await get_projects(session=session, headers=headers)
        page = 2
        projects = []

        # If there is NO next page (only 1 page) ->
        # add first results into projects and return it.
        # Otherwise while there next page with projects ->
        # add projects from current page to projects list.
        # Then make request with next page and increase page number.
        if results["next"] is None:
            projects += results["results"]
        else:
            while results["next"] is not None:
                projects += results["results"]
                results = await get_projects(
                    headers=headers,
                    params={"page": page}
                    )
                page += 1

        return projects


async def convert_project_to_url(headers, project_name):
    """Convert project name to project url (necessary for issue creation).

    Take project name -> get list of projects (list of dict's).
    Iterate over a list trying to find project with given name.
    If project is found -> get url of project and return it.
    """

    projects = await _all_projects(headers)

    for project in projects:
        if project["name"] == project_name:
            project_url = project["url"]

    try:
        return project_url
    except UnboundLocalError:
        return "UnboundLocalError"


async def convert_url_to_project(headers, project_url):
    """Convert project name to project url (necessary for Issue info).

    Works like convert_project_to_url, but reverse
    """

    projects = await _all_projects(headers)

    for project in projects:
        if project["url"] == project_url:
            project_name = project["name"]

    try:
        return project_name
    except UnboundLocalError:
        return "UnboundLocalError"


async def get_issues(session, headers, **kwargs):
    """ Get first (or N) page of issues via GET request """

    url = f"{API_BASE_URL}/issues/"
    try:
        # This block is executing when we
        # want to get N page of issues.
        async with session.get(
            url, headers=headers,
            params=kwargs["params"]
        ) as r:
            return await r.json()
    except KeyError:
        async with session.get(url, headers=headers) as r:
            return await r.json()


async def get_issue(session, id, headers, **kwargs):
    """ Take info about single issue via GET request """

    try:
        language, timezone = kwargs["language"], kwargs["timezone"]

        url = f"{API_BASE_URL}/issues/{id}/"
        async with session.get(url, headers=headers) as r:
            data = await r.json()
            data["project"] = await convert_url_to_project(
                headers,
                data["project"]
                )
            data["created"] = _beautiful_date(
                data["created"],
                language,
                timezone
                )
            data["updated"] = _beautiful_date(
                data["updated"],
                language,
                timezone
                )

            return data
    except KeyError:
        url = f"{API_BASE_URL}/issues/{id}/"
        async with session.get(url, headers=headers) as r:
            return await r.json()


async def make_issue(session, data, headers, **kwargs):
    """ Create single issue via POST request """

    url = f"{API_BASE_URL}/issues/"
    async with session.post(url, data=data, headers=headers) as r:
        return r.status


async def update_issue(session, id, data, headers, **kwargs):
    """ Update single issue via PUT request"""

    url = f"{API_BASE_URL}/issues/{id}/"
    async with session.put(url, data=data, headers=headers) as r:
        return r.status


async def delete_issue(session, id, headers, **kwargs):
    """ Delete single issue via DELETE request"""

    url = f"{API_BASE_URL}/issues/{id}/"
    async with session.delete(url, headers=headers) as r:
        if r.status == 204:
            return _("The issue was successfully deleted!")


async def main(**kwargs):
    async with aiohttp.ClientSession() as session:
        if kwargs:
            try:
                # This block executes only when we work
                # with pagination of projects and/or issues.
                res = await getattr(
                    Paginator(kwargs["headers"], kwargs["page"]),
                    kwargs["method"]
                    )(session)
                return res
            except KeyError:
                # A block that usually works with API by running
                # functions with a request to a specific endpoint.
                res = await globals()[kwargs["endpoint"]](session, **kwargs)
                return res


asyncio.run(main())
