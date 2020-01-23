from setuptools import setup

VERSION = "2.1.3"

setup(
    name="nhltv",
    version=VERSION,
    description="Download NHL games from game center",
    url="https://github.com/cmaxwe/dl-nhltv",
    license="None",
    keywords="NHL GAMECENTER",
    packages=["nhltv_lib"],
    data_files=[("extras", ["nhltv_lib/extras/black.mkv"])],
    include_package_data=True,
    entry_points={"console_scripts": ["nhltv=nhltv_lib.main:main"]},
    install_requires=["requests==2.22.0"],
)
