from pathlib import Path

from piccolo.conf.apps import AppConfig, table_finder

CURRENT_DIRECTORY = Path(__file__).parent

APP_CONFIG = AppConfig(
    app_name="db",
    migrations_folder_path=CURRENT_DIRECTORY / "piccolo_migrations",
    table_classes=table_finder(modules=["db.tables"]),
    migration_dependencies=[],
    commands=[],
)
