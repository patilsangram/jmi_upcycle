from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in jute_mark_india/__init__.py
from jute_mark_india import __version__ as version

setup(
	name="jute_mark_india",
	version=version,
	description="jute_mark_india",
	author="admin",
	author_email="admin@example.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
