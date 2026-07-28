from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in tech4all_pos_general/__init__.py
from tech4all_pos_general import __version__ as version

setup(
	name="tech4all_pos_general",
	version=version,
	description="Tech4all POS General",
	author="tech4allERP",
	author_email="info@tech4allerp.cojm",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
