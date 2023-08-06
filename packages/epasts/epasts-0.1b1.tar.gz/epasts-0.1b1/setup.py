from setuptools import setup, find_packages

version = "0.1b1"
requires = []

setup(
    name="epasts",
    version=version,
    description="Simple email handling library.",
    author="Adrians Heidens",
    author_email="adrians.heidens@gmail.com",
    url="http://bitbucket.org/adrians/epasts",
    download_url="http://bitbucket.org/adrians/epasts/downloads",
    license="BSD",
    packages=find_packages(exclude=["examples", "tests"]),
    install_requires=requires,
    )
