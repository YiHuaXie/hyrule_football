from hyrule_football.tasks.match_task import daily_match_task


async def start_all_tasks() -> None:
    daily_match_task()
