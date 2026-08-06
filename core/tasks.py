from core.data_updater import DatabaseUpdater


def update_database() -> None:
    DatabaseUpdater(with_image=True).run()
