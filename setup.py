from setuptools import setup

VERSION = "2.2.3"

setup(
    name="nhltv",
    version=VERSION,
    description="Download NHL games from game center",
    url="https://github.com/cmaxwe/dl-nhltv",
    license="None",
    keywords="NHL GAMECENTER",
    packages=["nhltv_lib", "nhltv_lib.alembic", "nhltv_lib.alembic.versions"],
    data_files=[
        ("extras", ["nhltv_lib/extras/black.mkv", "nhltv_lib/alembic.ini"])
    ],
    include_package_data=True,
    entry_points={"console_scripts": ["nhltv=nhltv_lib.main:main"]},
    install_requires=[
        "requests==2.22.0",
        "alembic==1.3.3",
        "SQLAlchemy==1.3.12",
    ],
)
