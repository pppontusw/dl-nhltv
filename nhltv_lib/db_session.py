import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nhltv_lib.models import Base
from nhltv_lib.settings import get_download_folder

# this session gets overridden by the database setup function at runtime
empty_session = sessionmaker()
session = empty_session()


def setup_db() -> sessionmaker:
    download_dir = get_download_folder()
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    engine = create_engine("sqlite:///" + os.path.join(download_dir, "app.db"))
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)

    global session
    session = DBSession()

    Base.metadata.create_all()
    session.commit()

    return session
