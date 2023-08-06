from setuptools import setup, find_packages

setup(
    name="indianrailways",
    version="0.1",
    author="Anand Chitipothu",
    author_email="anandology@gmail.com",
    description="Python library to interact with Indian Railways website.",
    entry_points={
	"console_scripts": [
	    "pnr-status = indianrailways.cli:pnr_status"
	]
    },
    packages=find_packages(),
    install_requires=[
	"BeautifulSoup"
    ]
)
