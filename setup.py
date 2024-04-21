from setuptools import setup

VERSION = "3.0.0"

setup(
    name="nhltv",
    version=VERSION,
    description="Download NHL games from game center",
    url="https://github.com/pppontusw/dl-nhltv",
    license="None",
    keywords="NHL GAMECENTER",
    packages=["nhltv_lib", "nhltv_lib.alembic", "nhltv_lib.alembic.versions"],
    data_files=[
        ("extras", ["nhltv_lib/extras/black.mkv", "nhltv_lib/alembic.ini"])
    ],
    include_package_data=True,
    entry_points={"console_scripts": ["nhltv=nhltv_lib.main:main"]},
    install_requires=[
        "requests==2.31.0",
        "alembic==1.13.1",
        "SQLAlchemy==2.0.29",
        "streamlink==6.7.3",
    ],
)
