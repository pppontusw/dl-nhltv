import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import alembic.config  # type: ignore
from nhltv_lib.models import Base
from nhltv_lib.settings import get_download_folder

# this session gets overridden by the database setup function at runtime
empty_session = sessionmaker()
session = empty_session()


def _migrate_db(db_path: str) -> None:
    boo = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    alembicArgs = [f"-xdbPath={db_path}", "upgrade", "head"]
    alembic.config.main(argv=alembicArgs)
    os.chdir(boo)


def setup_db() -> sessionmaker:
    download_dir = get_download_folder()
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    if os.path.isabs(download_dir):
        db_path = "sqlite:///" + os.path.join(download_dir, "nhltv_database")
    else:
        db_path = "sqlite:///" + os.path.join(
            os.getcwd(), download_dir, "nhltv_database"
        )

    _migrate_db(db_path)

    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)

    global session  # pylint: disable=global-statement
    session = DBSession()

    return DBSession
