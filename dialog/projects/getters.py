from aiogram.utils.i18n import gettext as _

from aiogram_dialog import DialogManager

from aiohttp import ClientSession
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from dialog.utils import get_headers, get_lang_and_tz
from dialog.bugtracker_api import Project


async def get_projects(
    dialog_manager: DialogManager,
    sessionmaker: async_sessionmaker,
    redis: Redis,
    session: ClientSession,
    **kwargs
):
    headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )

    # Limit in 9999 projects (default is 10)
    # is necessary to get pagination working.
    projects = await Project.get_items(session, headers, {"limit": 9999})

    if "count" in projects:
        return {"projects": projects["results"]}
    return {"no_projects": projects}


async def get_project(
    dialog_manager: DialogManager,
    sessionmaker: async_sessionmaker,
    redis: Redis,
    session: ClientSession,
    **kwargs
):
    project_id = dialog_manager.start_data
    headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )
    lang, tz = await get_lang_and_tz(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )

    project = await Project.get_item(session, project_id, headers, lang, tz)

    formatted_project = _(
        """\
            \n<b>Name</b>: {name}\
            \n<b>Key</b>: {key}\
            \n<b>Favorite</b>: {favorite}\
            \n<b>Created</b>: {created}\
            \n<b>Updated</b>: {updated}
        """
    ).format(
        name=project['name'],
        key=project['key'],
        favorite=Project.get_translated_favorite(project["favorite"]),
        created=project['created'],
        updated=project['updated']
    )

    return {"project": formatted_project}
