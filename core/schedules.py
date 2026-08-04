from django_q.models import Schedule
from django_q.tasks import async_task, schedule


def retrieve_printer_data_once() -> int:
    """Create schedule that updates database once"""
    return async_task("core.tasks.update_database", task_name="Printer data retrieval once")


def retrieve_printer_data_regularly() -> None:
    """Create schedule that updates database regularly"""
    schedule("core.tasks.update_database", name="Printer data retrieval regularly", schedule_type="I", minutes=2)


def stop_retrieving_printer_data() -> None:
    """Stop schedulers that update database"""
    Schedule.objects.filter(name__startswith="Printer data retrieval").delete()
