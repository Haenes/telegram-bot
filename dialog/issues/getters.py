from aiogram.utils.i18n import gettext as _

from aiogram_dialog import DialogManager

from aiohttp import ClientSession
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from dialog.utils import get_headers, get_lang_and_tz
from dialog.bugtracker_api import Issue


async def get_issues(
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
    project_id = dialog_manager.start_data

    if headers is not None:
        # Limit in 9999 projects (default is 10)
        # is necessary to get pagination working.
        issues = await Issue.get_items(session, headers, project_id, {"limit": 9999})

        if "count" in issues:
            return {"issues": issues["results"]}
        return {"no_issues": issues}


async def get_issue(
    dialog_manager: DialogManager,
    sessionmaker: async_sessionmaker,
    redis: Redis,
    session: ClientSession,
    **kwargs
):
    project_id, issue_id = dialog_manager.start_data
    headers = await get_headers(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )
    language, timezone = await get_lang_and_tz(
        user_id=dialog_manager.event.from_user.id,
        sessionmaker=sessionmaker,
        redis=redis
    )

    issue = await Issue.get_item(
        session=session,
        id=issue_id,
        project_id=project_id,
        headers=headers,
        language=language,
        timezone=timezone
    )
    issue_type, priority, status = Issue.get_translated_fields(issue)

    formatted_issue = _(
        """\
            \n<b>Title</b>: {title}\
            \n<b>Description</b>: {description}\
            \n<b>Type</b>: {type}\
            \n<b>Priority</b>: {priority}\
            \n<b>Status</b>: {status}\
            \n<b>Created</b>: {created}\
            \n<b>Updated</b>: {updated}
        """
    ).format(
        title=issue["title"],
        description=issue["description"],
        type=issue_type,
        priority=priority,
        status=status,
        created=issue["created"],
        updated=issue["updated"]
    )

    return {"issue": formatted_issue}
