import setuptools
from pathlib import Path

# read the contents of your README file
current_directory = Path(__file__).parent
long_description = (current_directory / "README.md").read_text()

setuptools.setup(
    name="ThermiaOnlineAPI",
    packages=[
        "ThermiaOnlineAPI",
        "ThermiaOnlineAPI.api",
        "ThermiaOnlineAPI.exceptions",
        "ThermiaOnlineAPI.model",
        "ThermiaOnlineAPI.utils",
    ],
    setuptools_git_versioning={
        "enabled": True,
        "dev_template": "{tag}",
    },
    license="GPL-3.0",
    description="A Python API for Thermia heat pumps using https://online.thermia.se",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Krisjanis Lejejs",
    author_email="krisjanis.lejejs@gmail.com",
    url="https://github.com/klejejs/python-thermia-online-api",
    download_url="https://github.com/klejejs/python-thermia-online-api/releases",
    keywords=["Thermia", "Online"],
    install_requires=[],
    setup_requires=["setuptools-git-versioning"],
    classifiers=[],
)
