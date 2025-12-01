from .match_task import daily_match_task


def start_all_tasks() -> None:
    daily_match_task()
