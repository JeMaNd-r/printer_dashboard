from core.data_updater import DatabaseUpdater

with DatabaseUpdater() as db:
    print("Database updating...")
